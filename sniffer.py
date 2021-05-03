import sys
import socket
from threading import Thread, Lock
import shutil
import math


SERVER_HOST = "localhost"
SERVER_PORT = int(sys.argv[1])
CLIENT_HOST = "localhost"
CLIENT_PORT = int(sys.argv[2])
output_lock = Lock()


def sniffer_thread(thread_name, from_connection, to_connection):
    while True:
        try:
            data = from_connection.recv(65536)
        except:
            with output_lock:
                print(f"{thread_name}: Error receiving data.")
            return
        if len(data) == 0:
            with output_lock:
                print(f"{thread_name}: Connection closed.")
            try:
                to_connection.close()
            except:
                pass
            return
        else:
            with output_lock:
                columns = shutil.get_terminal_size().columns
                total_bytes = len(data)
                print(f"{thread_name}: {total_bytes} {'byte' if total_bytes == 1 else 'bytes'}...")
                print()
                bytes_per_segment = (columns - 3) // 3
                total_segments = math.ceil(len(data) / bytes_per_segment)
                for segment_index in range(total_segments):
                    hex_output = ["#"]
                    chr_output = ["-"]
                    for byte_offset in range(bytes_per_segment):
                        byte_index = (segment_index * bytes_per_segment) + byte_offset
                        if byte_index >= total_bytes:
                            break
                        byte_value = data[byte_index]
                        hex_output.append(f"{byte_value:02X}")
                        chr_output.append(f" {chr(byte_value)}" if 0x21 <= byte_value <= 0x7E else "  ")
                    print(" ".join(hex_output))
                    print(" ".join(chr_output))
                print()
            try:
                to_connection.sendall(data)
            except:
                print(f"{thread_name}: Error sending data.")
                try:
                    from_connection.close()
                except:
                    pass
                return


sniffer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sniffer_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

sniffer_socket.bind((CLIENT_HOST, CLIENT_PORT))
sniffer_socket.listen(5)

client_count = 0
try:
    while True:
        client_connection, client_address = sniffer_socket.accept()
        client_count += 1
        server_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_connection.connect((SERVER_HOST, SERVER_PORT))

        print(f"Connected client #{client_count}: {client_address[0]}:{client_address[1]}")

        Thread(target=sniffer_thread,
               args=(f"From client #{client_count} to server", client_connection, server_connection),
               daemon=True).start()
        Thread(target=sniffer_thread,
               args=(f"From server to client #{client_count}", server_connection, client_connection),
               daemon=True).start()
except KeyboardInterrupt:
    sys.exit()
finally:
    try:
        sniffer_socket.shutdown(socket.SHUT_RDWR)
        sniffer_socket.close()
    except:
        pass
