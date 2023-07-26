from devices import BatteryMonitor, Device, DeviceData


class SmartLithiumData(DeviceData):
    def get_raw(self) -> dict:
        """
        Return the temperature in Celsius
        """
        return self._data

    # def get_temperature(self) -> float:
    #     """
    #     Return the temperature in Celsius
    #     """
    #     return self._data["temperature"]

    # def get_voltage(self) -> float:
    #     """
    #     Return the voltage in volts
    #     """
    #     return self._data["voltage"]


class SmartLithium(Device):
    def parse(self, data: bytes) -> SmartLithiumData:
        parsed = SmartLithium(self.advertisement_key).parse(data)

        return SmartLithiumData(
            self.get_model_id(data),
            {"raw": parsed}
            # {"temperature": parsed.get_temperature(), "voltage": parsed.get_voltage()},
        )
