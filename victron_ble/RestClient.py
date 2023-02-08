import logging
from time import time
import inspect
from typing import Any, Dict
from enum import Enum
from config import CONFIG
from bleak.backends.device import BLEDevice
from devices import Device
from requests import post
import json

logger = logging.getLogger(__name__)

class RestClient:

    def __init__(self):
        self.url = CONFIG["server_url"]

    def getDict(self, device: Device) -> dict:
        data = {}
        for name, method in inspect.getmembers(device, predicate=inspect.ismethod):
            if name.startswith("get_"):
                value = method()
                if isinstance(value, Enum):
                    value = value.name.lower()
                if value is not None:
                    data[name[4:]] = value
        return data    

    def send(self, bleDevice: BLEDevice, device: Device):
        # send data to backend
        data = self.getDict(device)
        data['timestamp'] = int(time()*1000)
        if "voltage" in data and "current" in data:
            data['power'] = round(data["voltage"]*data["current"])
        blob = {
            "name": bleDevice.name,
            "address": bleDevice.address,
            "rssi": bleDevice.rssi,
            "data": data,
        }
        print(json.dumps(blob, indent=2));
        post(f"{self.url}/api/device", json=blob)
