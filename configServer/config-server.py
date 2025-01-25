from pprint import pprint
import threading
import tomllib
import socketserver
import json


class RulesMixIn(socketserver.BaseServer):
    rules = []
    state = {}

    def setup_rules(self, pad_config: dict):
        pass

    def on_event(self, event: dict):
        print(event)
        pass


class UDPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        self.server.__getattribute__("on_event")(
            json.loads(self.request[0].strip()))


class TCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        # self.request is the TCP socket connected to the client
        data = b""

        while True:
            _data = self.request.recv(1024).strip()
            if not _data:
                break
            data += _data

            while -1 != (pos := data.find(b'}')):
                event, data = (data[:pos+1], data[pos+1:])
                self.server.__getattribute__("on_event")(json.loads(event))


class TCPServer(RulesMixIn, socketserver.ThreadingTCPServer):
    pass


class UDPServer(RulesMixIn, socketserver.UDPServer):
    pass  # A thread for each UDP datagram is overkill


# Read config file
with open("configServer/droidpad-servers.toml", "rb") as f:
    config = tomllib.load(f)
    pprint(config)


# Create all servers
servers = []
for pad, pad_config in config.items():
    if not isinstance(pad_config, dict):
        print(f"[Error] Invalid configuration for pad '{pad}'.")
        continue

    pad_host = pad_config.setdefault("host", "0.0.0.0")
    pad_port = pad_config.setdefault("port", 8080)
    pad_type = pad_config.setdefault("type", "UDP").upper()

    if not isinstance(pad_port, int):
        print(f"[Error] Port in pad '{pad}' is not a integer.")
        continue

    server_address = (pad_host, pad_port)
    match pad_type:
        case "TCP":
            ServerClass = TCPServer
            RequestHandlerClass = TCPHandler
        case "UDP":
            ServerClass = UDPServer
            RequestHandlerClass = UDPHandler
        case _type:
            print(f"[Error] Server type '{_type}' in pad '{
                  pad}' is invalid, only 'TCP' and 'UDP' supported")
            continue

    # Start server thread
    server = ServerClass(server_address, RequestHandlerClass)
    server.setup_rules(pad_config)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.start()
    print(f"{pad_type} Server {server_address} running in thread {server_thread.name}")
    servers.append((server, server_thread))
