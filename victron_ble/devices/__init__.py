from typing import Dict, Optional, Type

from construct import Int8ul, Int16ul

from devices.base import Device, DeviceData
from devices.battery_monitor import AuxMode, BatteryMonitor
from devices.battery_sense import BatterySense
from devices.dc_energy_meter import DcEnergyMeter
from devices.solar_charger import SolarCharger
from devices.smart_lithium import SmartLithium

__all__ = [
    "AuxMode",
    "Device",
    "DeviceData",
    "BatteryMonitor",
    "DcEnergyMeter",
    "SolarCharger",
]

# Add to this list if a device should be forced to use a particular implementation
# instead of relying on the identifier in the advertisement
MODEL_PARSER_OVERRIDE: Dict[int, Type[Device]] = {
    0xA3A4: BatterySense,  # Smart Battery Sense
    0xA3A5: BatterySense,  # Smart Battery Sense
}


def detect_device_type(data: bytes) -> Optional[Type[Device]]:
    model_id = Int16ul.parse(data[2:4])
    mode = Int8ul.parse(data[4:5])

    # Model ID-based preferences
    match = MODEL_PARSER_OVERRIDE.get(model_id)
    if match:
        return match

    # Defaults
    if mode == 0x2:  # BatteryMonitor
        return BatteryMonitor
    elif mode == 0xD:  # DcEnergyMeter
        return DcEnergyMeter
    elif mode == 0x8:  # AcCharger
        pass
    elif mode == 0x4:  # DcDcConverter
        pass
    elif mode == 0x3:  # Inverter
        pass
    elif mode == 0x6:  # InverterRS
        pass
    elif mode == 0xA:  # LynxSmartBMS
        pass
    elif mode == 0xB:  # MultiRS
        pass
    elif mode == 0x5:  # SmartLithium
        return SmartLithium
    elif mode == 0x1:  # SolarCharger
        return SolarCharger
    elif mode == 0xC:  # VE.Bus
        pass

    return None
