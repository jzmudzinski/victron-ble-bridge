import logging
import datetime
import inspect
from typing import Any, Dict
from enum import Enum
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from config import CONFIG
from bleak.backends.device import BLEDevice
from devices import Device

logger = logging.getLogger(__name__)

class FirebaseClient:

    def __init__(self):
        # read config file of service account for communicating with firestore API
        cred = credentials.Certificate('victron-ble-mgmt-bb846febdbca.json')
        app = firebase_admin.initialize_app(cred)
        self.db = firestore.client()

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
        self.db.collection(f'{CONFIG["uid"]}').document(f'{bleDevice.address}').set({'name': bleDevice.name})
        self.db.collection(f'{CONFIG["uid"]}').document(f'{bleDevice.address}').collection(f'{datetime.datetime.now()}').add(self.getDict(device)) 
  
