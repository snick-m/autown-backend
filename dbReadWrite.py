import ast
import socket

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 65431        # Port to listen on (non-privileged ports are > 1023)

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((HOST, PORT))
        sock.listen()

        while True:
            conn, addr = sock.accept()
            with conn:
                print('Connected by', addr)
                data = conn.recv(2048)
                print("A new block received: ", data.decode())
                conn.sendall("Request Received.".encode())

                msg = ast.literal_eval(data.decode())
                process_block(msg)

def process_block(block):
    print("Processing block: ", block)
    print(block['request'])