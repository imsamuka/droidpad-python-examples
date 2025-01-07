## This Repository contains Python examples for [DroidPad](https://github.com/umer0586/DroidPad) Android app 

1. ### Clone this Repo
```bash
git clone https://github.com/umer0586/droidpad-python-examples
```  
2. ### Install requirements
```bash
pip install -r requirements.txt
```

3. ### Move to servers directory
```bash
cd droidpad-python-examples/servers
```
-  #### To Start a websocket server
    ```bash
     python websocket-server.py 8080
    ```
-  #### To Start a TCP server
    ```bash
     python tcp-server.py 8081
    ```
-  #### To Start a UDP server
    ```bash
     python udp-server.py 8082
    ```
### To find your machines's IP address:
  - On Windows, use the `ipconfig` command.
  - On Linux, use the `ifconfig` command.

For BLE navigate to `BLEClient` directory and run `python subscribe.py`

Create a new controller in [DroidPad](https://github.com/umer0586/DroidPad). Then, navigate to the connection settings and specify the IP address and port number. Once connected, and you should see JSON messages being printed in the console.
