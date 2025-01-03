import socket
import threading
import sys


class UDPServer:
    def __init__(self, address, buffer_size=1024):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.address = address
        self.buffer_size = buffer_size

    def setDataCallBack(self, callback):
        self.callback = callback

    def start(self, daemon=False):
        self.thread = threading.Thread(target=self.__listen__)
        self.thread.daemon = daemon  # Daemon thread, so it terminates with the main program
        self.thread.start()

    def stop(self):
        self.sock.close()  # Close the socket to unblock recvfrom

    def __listen__(self):
        self.sock.bind(self.address)
        
        while True:
            try:                    
                data, address = self.sock.recvfrom(self.buffer_size)
                
                if self.callback != None:
                    self.callback(data)

            except socket.error:
                break  # Break if the socket is closed
                   

PORT = 8080      # Port to listen on (non-privileged ports > 1023)

if len(sys.argv) > 1 and sys.argv[1].isnumeric:
    PORT = int(sys.argv[1])

def onData(data):
    print(data)


server = UDPServer(address=("0.0.0.0",PORT))
server.setDataCallBack(onData)
server.start()
print(f"UDP server listening: 0.0.0.0:{PORT}")


