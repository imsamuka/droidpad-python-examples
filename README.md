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


Create a new controller in [DroidPad](https://github.com/umer0586/DroidPad). Then, navigate to the connection settings and specify the IP address and port number. Once connected, and you should see JSON messages being printed in the console.


### Bluetooth Low Energy (BLE) in DroidPad

DroidPad functions as a **BLE peripheral** and sends notifications containing `CSV` strings to connected client through the characteristic UUID: `dc3f5274-33ba-48de-8246-43bf8985b323`.

#### Steps to Connect:
1. **Start the GATT Server on DroidPad**:  
   - Open a control pad with BLE connection and tap the **Play** button to initialize the GATT server and start advertising.

2. **Subscribe Using the Python Client**:  
   - Navigate to the `BLEClient` directory in the DroidPad Python examples repository.
   - Run the `subscribe.py` script:
     
     ```bash
     python subscribe.py
     ```
   - This script performs the following:
     - Scans for nearby BLE devices advertising the service UUID: `4fbfc1d7-f509-44ab-afe1-62ea40a4b111`.
     - Subscribes to notifications from the characteristic UUID: `dc3f5274-33ba-48de-8246-43bf8985b323`.

3. **View Notifications**:  
   - Once the script connects to DroidPad, it displays `CSV` strings in the console.
   - These notifications are triggered by interactions with items on the control pad.

