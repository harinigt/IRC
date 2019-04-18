""" IRC APPLICATION
SUBMITTED BY : HARINI G T"""

import select,socket, sys
QUIT_STRING = "[quit]"
READ_BUFFER = 1000


def chat_client():
    if len(sys.argv) < 3:
        print ('Usage : python chat_client.py hostname port')
        sys.exit()
    host = sys.argv[1]
    port = int(sys.argv[2])

    server_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server_connection.connect((host, port))  # trying to connect to server
    except:
        print('Unable to connect to the server.')
        sys.exit()

    print('Welcome to the IRC-Bot!!')
    msg_prefix = ''
    socket_list = [sys.stdin, server_connection]
    while True:
            ready_to_read, ready_to_write, in_error_sockets = select.select(socket_list, [], [])
            for s in ready_to_read:
                if s is server_connection:  # incoming message
                    msg = s.recv(READ_BUFFER)
                    if not msg:
                        print("Server down!")
                        sys.exit(2)
                    else:
                        if msg == QUIT_STRING.encode():
                            sys.stdout.write('Good Bye. Have a nice day\n')
                            sys.exit(2)
                        else:
                            sys.stdout.write(msg.decode())
                            if b'Please enter your name:' in msg.decode():
                                msg_prefix = 'name: '
                            else:
                                msg_prefix = ''
                            sys.stdout.write('[Me]')
                            sys.stdout.flush()
                else:
                    msg = msg_prefix + sys.stdin.readline()
                    server_connection.sendall(msg.encode())


if __name__ == '__main__':
    sys.exit(chat_client())
