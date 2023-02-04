from VictronScanner import VictronScanner
from FirebaseClient import FirebaseClient
import asyncio
import click
import logging
from typing import List, Tuple, Optional

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())


class DeviceKeyParam(click.ParamType):
    name = "device_key"

    def convert(self, value, param, ctx):
        if isinstance(value, str):
            parts = value.split("@")
            if len(parts) == 2:
                addr = parts[0].strip()
                key = parts[1].strip()
                return (addr, key)

        self.fail(f"{value} is not a valid <addr>@<key> pair", param, ctx)

@click.group()
@click.option("-v", "--verbose", is_flag=True, help="Increase logging output")
def cli(verbose):
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)


@cli.command(help="Read data from specified devices")
@click.argument("device_keys", nargs=-1, type=DeviceKeyParam())
def read(device_keys: List[Tuple[str, str]], timeout: Optional[int] = 10):

    scanning = asyncio.Event()
    loop = asyncio.new_event_loop()   
    
    def onDeviceFound(str):
        if scanning.is_set(): # let the timeout loop handle the stopping of the scan
            scanning.clear()
        print(str)
        my_reporter = FirebaseClient()
        my_reporter.send()

    async def startScanning(keys):
        victronScanner = VictronScanner(onDeviceFound, keys)
        await victronScanner.start()
        scanning.set()
        
        end_time = loop.time() + timeout
        while scanning.is_set():
            if loop.time() > end_time:
                scanning.clear()
                print('\nScan has timed out so we terminate')
            await asyncio.sleep(0.1)
        await victronScanner.stop()

    loop.run_until_complete(startScanning({k: v for k, v in device_keys}))

if __name__ == "__main__":
    cli()