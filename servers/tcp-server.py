import socket
import sys


# Define the server host and port
HOST = '0.0.0.0'  # Accept connections from any IP address
PORT = 8080      # Port to listen on (non-privileged ports > 1023)

if len(sys.argv) > 1 and sys.argv[1].isnumeric:
    PORT = int(sys.argv[1])



# Create a socket object
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the host and port
server_socket.bind((HOST, PORT))

# Start listening for incoming connections
server_socket.listen()  # Allows up to 5 connections in the queue
print(f"TCP Server listening on {HOST}:{PORT}")

try:
    # Accept a client connection
    client_socket, client_address = server_socket.accept()
    print(f"Connection established with {client_address}")

    while True:
        
        # Receive and display the client's message
        message = client_socket.recv(1024).decode('utf-8')  # Buffer size: 1024 bytes
        if message:
            print(message)

except KeyboardInterrupt:
    print("\nShutting down the server...")
    client_socket.close()

finally:
    # Close the server socket
    client_socket.close()
    server_socket.close()
