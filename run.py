""" run the client and server together """
'''
To run the code, you would need to follow these steps:

In terminal run run.py server
Open another terminal by clicking on +
Type the command run.py client
Enter the text in the client window and see the effect.
to kill server use ctrl+c
'''
import argparse, socket

MAX_SIZE_BYTES = 65535  # Mazimum size of a UDP datagram


def server(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    hostname = '127.0.0.1'
    s.bind((hostname, port))
    print('Listening at {}'.format(s.getsockname()))
    while True:
        data, client_address = s.recvfrom(MAX_SIZE_BYTES)
        message = data.decode('ascii')
        processed_message = message.upper()
        print('The client at {} says {!r}'.format(client_address, message))
        data = processed_message.encode('ascii')
        s.sendto(data, client_address)


def client(port):
    host = '127.0.0.1'
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    message = input('Input lowercase sentence:')
    data = message.encode('ascii')
    s.sendto(data, (host, port))
    print('The OS assigned the address {} to me'.format(s.getsockname()))
    data, address = s.recvfrom(MAX_SIZE_BYTES)
    text = data.decode('ascii')
    print('The server {} replied with {!r}'.format(address, text))


if __name__ == '__main__':
    funcs = {'client': client, 'server': server}
    parser = argparse.ArgumentParser(description='UDP client and server')
    parser.add_argument('functions', choices=funcs, help='client or server')
    parser.add_argument('-p', metavar='PORT', type=int, default=3000,
                        help='UDP port (default 3000)')
    args = parser.parse_args()
    function = funcs[args.functions]
    function(args.p)


def client_improved(port):
    """ no server other than the one the client connected to can send it messages. The operating system discards any
    of those messages by default. The main disadvantage of this method is that the client can only be connected to
    one server at a time. In most real life scenarios, singular applications connect to multiple servers.
    However, servers can actually spoof their IP addresses and masquerade as the server we expect a reply from. The only way to guarantee
    that authorized servers are contacting a client is to use encryption """
    host = '127.0.0.1'
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect((host, port))  # to forbid other addresses from sending packets to the client.
    message = input('Input lowercase sentence:')
    data = message.encode('ascii')
    s.send(data)  # no need to use sendto here
    print('The OS assigned the address {} to me'.format(s.getsockname()))
    data, address = s.recv(MAX_SIZE_BYTES)  # no need to use recvfrom with connect as well
    text = data.decode('ascii')
    print('The server {} replied with {!r}'.format(address, text))


def client_better(port):
    """A better, though more tedious approach, to handle multiple servers would be to check the return address of
    each reply against a list of addresses that replies are expected from. """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    hosts = []
    while True:
        host = input('Input host address:')
        hosts.append((host, port))
        message = input('Input message to send to server:')
        data = message.encode('ascii')
        s.sendto(data, (host, port))
        print('The OS assigned the address {} to me'.format(s.getsockname()))
        data, address = s.recvfrom(MAX_SIZE_BYTES)
        text = data.decode('ascii')
        if address in hosts:
            print('The server {} replied with {!r}'.format(address, text))
            hosts.remove(address)
        else:
            print('message {!r} from unexpected host {}!'.format(text, address))
