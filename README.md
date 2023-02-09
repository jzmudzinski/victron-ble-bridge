# victron-ble-bridge

A Python3 library to parse Instant Readout advertisement data from Victron devices and send them to a [web app](https://github.com/debueb/victron-ble-monitor) for visualization

Disclaimer: This software is not an officially supported interface by Victron and is provided entirely "as-is"

## Supported Devices:

* SmartShunt 500A/500mv and BMV-712/702:
    * Voltage
    * Alarm status
    * Current
    * Remaining time
    * State of charge (%)
    * Consumed amp hours
    * Auxilary input (temperature, midpoint voltage, or starter battery voltage)
* Solar Charger:
    * Charger State (Off, Bulk, Absorption, Float)
    * Battery Voltage (V)
    * Battery Charging Current (A)
    * Solar Power (W)
    * Yield Today (Wh)
    * External Device Load (A)

## Installation

- clone this repo
- install dependencies
```bash
pip -i requirements.txt
```
- create `victron_ble/config.py` and update with your environment data
```python
CONFIG = {
    "server_url": "http://localhost:6060",

    # timeout in seconds to scan for victron bluetooth instant advertisements. Program will exit when all devices are scanned or timeout has expired. Set to 0 to scan continously.
    "timeout": 0,

    # victron devices to scan for
    # format: "Device bluetooth address": "Encryption Key"
    "devices": {
        "address1": "advertisementKey1",
        "address2": "advertisementKey2"
    }
}
```

To be able to decrypt the contents of the advertisement, you'll need to first fetch the per-device encryption key from the official Victron application. The method to do this will vary per platform.

## Fetching Device Encryption Keys
 
**OSX**

1. Install the Victron app from the Mac App Store
2. Pair with your device at least once to transfer keys
3. Run the following from Terminal to dump the known keys (install `sqlite3` via Homebrew)
```bash
sqlite3 ~/Library/Containers/com.victronenergy.victronconnect.mac/Data/Library/Application\ Support/Victron\ Energy/Victron\ Connect/d25b6546b47ebb21a04ff86a2c4fbb76.sqlite 'select address,advertisementKey from advertisementKeys inner join macAddresses on advertisementKeys.macAddress == macAddresses.macAddress'
```

**Linux**

1. Download the Victron AppImage app from the Victron website.
2. Pair with your device at least once to transfer keys
3. Run the following from a terminal to dump the known keys (install `sqlite3` via your package manager)
```bash
sqlite3 ~/.local/share/Victron\ Energy/Victron\ Connect/d25b6546b47ebb21a04ff86a2c4fbb76.sqlite 'select address,advertisementKey from advertisementKeys inner join macAddresses on advertisementKeys.macAddress == macAddresses.macAddress'
```

**Windows**

Not supported yet. Please figure this out and contribute some
instructions.

## Developing

Set `"timeout": 0` in `config.py`

```bash
python victron_ble/cli.py scan
```

Start up the [web app](https://github.com/debueb/victron-ble-monitor)

## Automating

Set `"timeout": 10` in `config.py`

Add the following line in your `crontab` to update your server every  minute

```bash
*/1 * * * * python3 /path/to/project/victron_ble/cli.py scan`
```