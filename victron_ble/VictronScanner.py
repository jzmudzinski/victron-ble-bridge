import asyncio
import inspect
import logging
import json
from typing import Set, Callable, List
from enum import Enum
from bleak import BleakScanner
from bleak.backends.device import BLEDevice
from devices import Device, DeviceData, detect_device_type
from exceptions import AdvertisementKeyMissingError, UnknownDeviceError
from config import CONFIG


timeout_seconds = 10


logger = logging.getLogger(__name__)

# An ugly hack to print a class as JSON
class DeviceDataEncoder(json.JSONEncoder):
    def default(self, obj):
        if issubclass(obj.__class__, DeviceData):
            data = {}
            for name, method in inspect.getmembers(obj, predicate=inspect.ismethod):
                if name.startswith("get_"):
                    value = method()
                    if isinstance(value, Enum):
                        value = value.name.lower()
                    if value is not None:
                        data[name[4:]] = value
            return data


class VictronScanner:

    def __init__(self, onSuccess: Callable[..., str]):
        self._onSuccess = onSuccess

        # lowercase bluetooth addresses
        self._device_keys = dict((k.lower(), v) for k,v in CONFIG["devices"].items())
        self._known_devices: dict[str, Device] = {}

        self._scanner = BleakScanner()
        self._scanner: BleakScanner = BleakScanner(
            detection_callback=self.detection_callback
        )
        self._seen_data: Set[bytes] = set()

    def get_device(self, ble_device: BLEDevice, raw_data: bytes) -> Device:
        address = ble_device.address.lower()
        if address not in self._known_devices:
            advertisement_key = self.load_key(address)

            device_klass = detect_device_type(raw_data)
            if not device_klass:
                raise UnknownDeviceError(
                    f"Could not identify device type for {ble_device}"
                )

            self._known_devices[address] = device_klass(advertisement_key)
        return self._known_devices[address]

    def load_key(self, address: str) -> str:
        try:
            return self._device_keys[address]
        except KeyError:
            raise AdvertisementKeyMissingError(f"No key available for {address}")

    def detection_callback(self, ble_device, advertisement):
        # Filter for Victron devices and instant readout advertisements
        data = advertisement.manufacturer_data.get(0x02E1)
        if not data or not data.startswith(b"\x10") or data in self._seen_data:
            return

        # De-duplicate advertisements
        if len(self._seen_data) > 1000:
            self._seen_data = set()
        self._seen_data.add(data)

        try:
            device = self.get_device(ble_device, data)
        except AdvertisementKeyMissingError:
            return
        except UnknownDeviceError as e:
            logger.error(e)
            return
        
        self._onSuccess(ble_device, device.parse(data))

    async def start(self):
        await self._scanner.start()
    
    async def stop(self):
        await self._scanner.stop()