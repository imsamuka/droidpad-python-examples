import asyncio
from bleak import BleakScanner, BleakClient
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# UUID Constants
SERVICE_UUID = "4fbfc1d7-f509-44ab-afe1-62ea40a4b111"
CHARACTERISTIC_UUID = "dc3f5274-33ba-48de-8246-43bf8985b323"


async def notification_handler(sender, data):
    """Handle incoming notifications."""
    logger.info(f"Notification received: {data}")

def detection_callback(device: BLEDevice, advertisement_data: AdvertisementData):
    """Callback for device detection during scanning."""
    logger.info(f"Detected device: {device.name} ({device.address})")
    
    # Print all advertised service UUIDs
    if advertisement_data.service_uuids:
        logger.info(f"Advertised services: {advertisement_data.service_uuids}")
    
    if SERVICE_UUID.lower() in [str(uuid).lower() for uuid in advertisement_data.service_uuids]:
        logger.info(f"Found matching device: {device.name} ({device.address})")
        return device


async def run_ble_client():
    """Main function to handle BLE operations."""
    try:
        # Scan for devices
        logger.info("Scanning for BLE devices...")
        target_device = await BleakScanner.find_device_by_filter(
            detection_callback,
            timeout=5.0
        )
        
        if not target_device:
            logger.error(f"No device found with service UUID : {SERVICE_UUID}")
            return
        
        logger.info(f"Connecting to device: {target_device.name} ({target_device.address})")
        
        # Connect to the device
        async with BleakClient(address_or_ble_device=target_device.address, winrt={"use_cached_services" : False}) as client:
            logger.info(f"Connected to {target_device.address}")
                              

            # Try to get the service
            service = client.services.get_service(SERVICE_UUID)
            
            
            if not service:
                logger.error(f"Service {SERVICE_UUID} not found")
                return
                
            # Get the characteristic
            characteristic = service.get_characteristic(CHARACTERISTIC_UUID)
            
            if not characteristic:
                logger.error(f"Characteristic {CHARACTERISTIC_UUID} not found")
                return
            
            # Start notification subscription
            logger.info("Starting notification subscription...")
            await client.start_notify(characteristic, notification_handler)
            
            # Keep the connection alive to receive notifications
            logger.info("Listening for notifications. Press Ctrl+C to exit...")
            while True:
                await asyncio.sleep(1.0)
                
    except KeyboardInterrupt:
        logger.info("Stopping...")
        client.disconnect()
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        logger.error(f"Error type: {type(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")

def main():
    """Entry point of the script."""
    try:
        asyncio.run(run_ble_client())
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except Exception as e:
        logger.error(f"Main error: {str(e)}")

if __name__ == "__main__":
    main()