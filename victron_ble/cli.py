from VictronScanner import VictronScanner
import asyncio
import click
import logging
from typing import List, Tuple, Optional
from bleak.backends.device import BLEDevice
from devices import Device

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())

@click.group()
@click.option("-v", "--verbose", is_flag=True, help="Increase logging output")
def cli(verbose):
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)

@cli.command(help="scan for data from victron bluetooth devices specified by address and key")
@click.option("-t", "--timeout", default=3, help="Timeout in seconds for the scan")
@click.option("-a", "--address", default=None, help="Address of the device to scan for")
@click.option("-k", "--key", default=None, help="Encryption key for the device to scan for")
def scan(timeout, address, key):

    loop = asyncio.new_event_loop()   
    scanning = asyncio.Event()
    foundDevices = set()
    
    def onDeviceFound(bleDevice: BLEDevice, device: Device):
        if (timeout > 0 and bleDevice.address not in foundDevices):
            foundDevices.add(bleDevice.address)
            # if all devices have been found let the timeout loop stop of the scan
            if (bleDevice.address == address):
                if scanning.is_set(): 
                    scanning.clear()
        print(device._data)


    async def startScanning():
        victronScanner = VictronScanner(address, key, onDeviceFound)     
        await victronScanner.start()
        
        if timeout > 0:
            scanning.set()
            end_time = loop.time() + timeout
            while scanning.is_set():
                if loop.time() > end_time:
                    scanning.clear()
                    print('\nScan has timed out so we terminate')
                await asyncio.sleep(0.1)
            await victronScanner.stop()

    if (timeout > 0 ):
        loop.run_until_complete(startScanning())
    else:
        asyncio.ensure_future(startScanning(), loop=loop)
        loop.run_forever()

if __name__ == "__main__":
    cli()
