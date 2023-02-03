from OneTimeScanner import OneTimeScanner
import asyncio
import click
import logging
from typing import List, Tuple

logger = logging.getLogger(__name__)

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
def read(device_keys: List[Tuple[str, str]]):
    
    async def scanAndReport(keys):
        my_scanner = OneTimeScanner(keys)
        await my_scanner.run()

    loop = asyncio.new_event_loop()
    loop.run_until_complete(scanAndReport({k: v for k, v in device_keys}))


if __name__ == "__main__":
    cli()