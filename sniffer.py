import sys
import socket
from threading import Thread


SERVER_HOST = sys.argv[1]
SERVER_PORT = int(sys.argv[2])
SNIFFER_HOST = sys.argv[3]
SNIFFER_PORT = int(sys.argv[4])


def sniffer_thread(thread_name, from_connection, to_connection):
    while True:
        try:
            data = from_connection.recv(65536)
        except:
            print(f"{thread_name}: Error receiving data.")
            return
        if len(data) == 0:
            print(f"{thread_name}: Connection closed.")
            try:
                to_connection.close()
            except:
                pass
            return
        else:
            print(f"{thread_name}: {repr(data)}")
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

sniffer_socket.bind((SNIFFER_HOST, SNIFFER_PORT))
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
