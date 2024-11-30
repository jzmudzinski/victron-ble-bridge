from devices import BatteryMonitor, Device, DeviceData
from construct import (
    GreedyBytes,
    Int16ul,
    Int32ul,
    Struct,
    BitStruct,
    BitsInteger,
    Padding
)

class SmartLithiumData(DeviceData):
    def get_battery_voltage(self) -> float:
        """
        Return battery voltage in Volts
        """
        return self._data["battery"]["voltage"]
    
    def get_battery_temperature(self) -> float:
        """
        Return the temperature in Celsius
        """
        return self._data["battery"]["temperature"]

class SmartLithium(Device):

    PACKET = Struct(
        # "bms_flags" / Int32ul,
        # "errors" / Int16ul,
        # "cell_voltage" / 
        # BitStruct(
        #     "cell_1" / BitsInteger(7),
        #     "cell_2" / BitsInteger(7),
        #     "cell_3" / BitsInteger(7),
        #     "cell_4" / BitsInteger(7),
        #     "cell_5" / BitsInteger(7),
        #     "cell_6" / BitsInteger(7),
        #     "cell_7" / BitsInteger(7),
        #     "cell_8" / BitsInteger(7),
        # ),
        Padding(13),
        "battery" / 
        BitStruct(
            "voltage" / BitsInteger(12),
            "balancer_status" / BitsInteger(4),
            "temperature" / BitsInteger(7),
            Padding(1),
        ),
    )

    def parse(self, data: bytes) -> SmartLithiumData:
        decrypted = self.decrypt(data)
        pkt = self.PACKET.parse(decrypted)

        parsed = {
            "battery_voltage": pkt.battery.voltage / 100,
            "battery_temperature": pkt.battery.temperature - 40,
        }

        return SmartLithiumData(self.get_model_id(data), parsed)