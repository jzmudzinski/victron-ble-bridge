from VictronScanner import VictronScanner
from FirebaseClient import FirebaseClient
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


@cli.command(help="Read data from victron bluetooth devices specified in config.py")
def read(timeout: Optional[int] = 10):

    firebaseClient = FirebaseClient()
    scanning = asyncio.Event()
    loop = asyncio.new_event_loop()   
    
    def onDeviceFound(bleDevice: BLEDevice, device: Device):
        if scanning.is_set(): # let the timeout loop handle the stopping of the scan
            scanning.clear()
        firebaseClient.send(bleDevice, device)

    async def startScanning():
        victronScanner = VictronScanner(onDeviceFound)
        await victronScanner.start()
        scanning.set()
        
        end_time = loop.time() + timeout
        while scanning.is_set():
            if loop.time() > end_time:
                scanning.clear()
                print('\nScan has timed out so we terminate')
            await asyncio.sleep(0.1)
        await victronScanner.stop()

    loop.run_until_complete(startScanning())

if __name__ == "__main__":
    cli()