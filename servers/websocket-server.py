from websockets.sync.server import serve
import sys

# Keep track of connected clients
connected_clients = set()

def handler(websocket):
    # Add the new client to the set
    client_address = websocket.remote_address  # Get client address
    connected_clients.add(client_address)
    print(f"Client connected: {client_address}. Total connected clients: {len(connected_clients)}")

    try:
        # Handle incoming messages
        for message in websocket:
            print(message)
    except Exception as e:
        print(f"Error with client {client_address}: {e}")
    finally:
        # Remove client when they disconnect
        connected_clients.remove(client_address)
        print(f"Client disconnected: {client_address}. Total connected clients: {len(connected_clients)}")


def start():
    
    PORT = 8080

    if len(sys.argv) > 1 and sys.argv[1].isnumeric:
        PORT = int(sys.argv[1])

    with serve(handler, "0.0.0.0", PORT) as server:
        print(f"WebSocket server started on ws://0.0.0.0:{PORT}")
        server.serve_forever()


if __name__ == "__main__":
    start()
