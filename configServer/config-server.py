import re
import sys
import threading
import tomllib
import socketserver
import json
import subprocess


def create_servers(config):
    servers = []
    for pad, pad_config in config.items():
        if not isinstance(pad_config, dict):
            print(f"[Error] Invalid configuration for pad '{pad}'.")
            continue

        pad_host = pad_config.setdefault("host", "0.0.0.0")
        pad_port = pad_config.setdefault("port", 8080)
        pad_type = pad_config.setdefault("type", "UDP").upper()
        pad_rules = pad_config.setdefault("rules", {})

        pad_config["fstring_sim"] = pad_config.get("fstring_sim", True)
        pad_config["format_map"] = pad_config.get("format_map", True)
        pad_config["default_eval"] = pad_config.get("default_eval", "sh").lower()
        pad_config["call_sync"] = pad_config.get("call_sync", "threaded_async").lower()


        if not isinstance(pad_port, int):
            print(f"[Error] Port in pad '{pad}' is not a integer.")
            continue

        if not isinstance(pad_rules, dict):
            print(f"[Error] Rules in pad '{pad}' are not in the correct format.")
            continue

        if not isinstance(pad_config["fstring_sim"], bool):
            print(f"[Error] 'fstring_sim' in pad '{pad}' is not a boolean true or false.")
            continue

        if not isinstance(pad_config["format_map"], bool):
            print(f"[Error] 'format_map' in pad '{pad}' is not a boolean true or false.")
            continue

        choices = ("sh", "bash", "cmd", "powershell", "pwsh", "py", "eval", "exec")
        if pad_config["default_eval"] not in choices:
            print(f"[Error] 'default_eval' in pad '{pad}' should be one of {repr(choices)}")
            continue

        choices = ("simple", "threaded_sync", "threaded_async")
        if pad_config["call_sync"] not in choices:
            print(f"[Error] 'call_sync' in pad '{pad}' should be one of {repr(choices)}")
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
        server.setup_rules(pad_rules, pad_config)
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.start()
        print(f"{pad_type} Server {
            server_address} running in thread {server_thread.name}")
        servers.append((server, server_thread))
    return servers


class RulesMixIn(socketserver.BaseServer):
    def setup_rules(self, pad_rules: dict[str, str], pad_config: dict):
        self.memo = {} # memory-persistent data storage to manipulate complex operations
        self.rules: dict[str, list[tuple[str | None, str | list[str]]]] = {}
        self.default_eval: str = pad_config["default_eval"]
        self.call_sync: str = pad_config["call_sync"]
        self.fstring_sim: bool = pad_config["fstring_sim"]
        self.format_map: bool = pad_config["format_map"]

        for key, value in pad_rules.items():
            key_parts: list[str] = key.split("-")
            if len(key_parts) <= 1:
                print(f"[Error] rule '{
                      key}' is not well formed, need to have at least one '-' delimiter.")
                continue

            rule_id = key_parts[0] + '-' + key_parts[1].lower()
            eval_type = key_parts[2].lower() if len(key_parts) >= 3 else None
            rule_list = self.rules.setdefault(rule_id, [])

            if isinstance(value, str):
                rule_list.append((eval_type, value))

            elif isinstance(value, list):
                match ((eval_type or self.default_eval), value):
                    case (_, []):
                        print(f"[Error] Empty command list for rule '{key}'.")
                        continue

                    case ("exec", [cmd0, *_]) if isinstance(cmd0, str):
                        rule_list.append((eval_type, value)) # type: ignore

                    case ("exec", [cmd0, *_]) if isinstance(cmd0, list):
                        for cmd in value:
                            rule_list.append((eval_type, cmd))

                    case (_, [cmd0, *_]) if isinstance(cmd0, str):
                        for cmd in value:
                            rule_list.append((eval_type, cmd))

                    case _:
                        print(f"[Error] Unsupported value type in rule '{
                              key}': {type(value[0]).__name__}")
                        continue

            else:
                print(f"[Error] Unsupported value type for rule '{
                      key}': {type(value).__name__}")
                continue

    def on_event(self, event: dict):
        rules_ids = self.event_ruleids(event)

        if not set(rules_ids).intersection(self.rules):
            print(f"[Warning] None of these rules were found: {rules_ids}")
            return

        for rule_id in rules_ids:
            if rule_id not in self.rules:
                continue

            # print(f"[Info] Running rule '{rule_id}':")
            for (eval_type, cmd) in self.rules[rule_id]:
                self.run_command(
                    event,
                    (
                        self.cmd_format(event, cmd) if isinstance(cmd, str) else
                        [self.cmd_format(event, c) for c in cmd]
                    ),
                    (eval_type or self.default_eval)
                )



    def run_command(self, event: dict, command: str | list[str], eval_type: str):
        target = subprocess.run
        args = tuple()

        match eval_type.lower():
            case "exec":
                args = (command if isinstance(command, list) else [command],)
            case _ if isinstance(command, list):
                assert False, f"[Error] Unsupported eval_type '{
                    eval_type}' using a list"
            case "sh":
                args = (["sh", "-c", command],)
            case "bash":
                args = (["bash", "-c", command],)
            case "cmd":
                args = (["cmd", "/C", command],)
            case "powershell":
                args = (["powershell", "-Command", command],)
            case "pwsh":
                args = (["pwsh", "-Command", command],)
            case "py":
                args = (["python", "-c", command],)
            case "eval":
                # simple match will add the values to the scope
                memo = self.memo
                match event:
                    case {"id": id, "type": "SWITCH" | "BUTTON" as type, "state": state}: pass
                    case {"id": id, "type": "DPAD" as type, "state": state, "button": button}: pass
                    case {"id": id, "type": "JOYSTICK" as type, "x": x, "y": y}: pass
                    case {"id": id, "type": "SLIDER" as type, "value": value}: pass
                    case _: pass

                target = eval
                args = (command, globals(), locals())
            case _:
                print(f"[Error] Unsupported eval type '{eval_type}'")
                return

        match self.call_sync:
            case "simple":
                target(*args) # type: ignore
            case "threaded_async":
                threading.Thread(target=target, args=args).start()
            case "threaded_sync":
                thread = threading.Thread(target=target, args=args)
                thread.start()
                thread.join()
            case _:
                assert False, f"[Error] Unsupported call_sync '{self.call_sync}'"


    def event_ruleids(self, event: dict):
        match event:
            case {"id": id, "type": "SWITCH" | "BUTTON" as type, "state": state}:
                return (f"{id}-{type.lower()}",
                        f"{id}-{str(state).lower()}")

            case {"id": id, "type": "JOYSTICK"}:
                return (f"{id}-joy", )

            case {"id": id, "type": "SLIDER"}:
                return (f"{id}-slider", )

            case {"id": id, "type": "DPAD", "state": state, "button": btn}:
                return (f"{id}-dp_button",
                        f"{id}-dp_{state.lower()}",
                        f"{id}-dp_{btn.lower()}_{state.lower()}")

            case _:
                assert False, f"[Error] Event without any possible rules: {event}"


    def cmd_format(self, event: dict, command: str):
        # will find the pattern __{}__ and interpret as a fstring
        if self.fstring_sim:
            # simple match will add the values to the scope
            memo = self.memo
            match event:
                case {"id": id, "type": "SWITCH" | "BUTTON" as type, "state": state}: pass
                case {"id": id, "type": "DPAD" as type, "state": state, "button": button}: pass
                case {"id": id, "type": "JOYSTICK" as type, "x": x, "y": y}: pass
                case {"id": id, "type": "SLIDER" as type, "value": value}: pass
                case _: pass

            matches = re.split(r"__{(.+?)}__", command)
            for i in range(1, len(matches), 2):
                matches[i] = str(eval('f"{' + matches[i] + '}"'))
            command = "".join(matches)

        # any other {} will be passed to common format()
        if self.format_map:
            command = command.format_map(event)

        return command


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


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1]:
        config_file = sys.argv[1]
    else:
        config_file = "configServer/default.toml"

    with open(config_file, "rb") as f:
        config = tomllib.load(f)

    create_servers(config)
