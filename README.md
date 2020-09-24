# python-n2kclient

High-level Python library to format messages and send them out via the NMEA 2000 bus using socket can.

## Usage
```python
# Uses J1939 CAN implementation from https://github.com/milhead2/python-j1939.git
import j1939

# Import the message types you want to use 
from n2kclient import TemperatureMessage

# Initialize the bus - it supports pretty much anything python can package supports.
bus = j1939.Bus(channel='can0', bustype='socketcan', timeout=0.01, broadcast=False)

# Create a message
p = TemperatureMessage(sid=0x00, temperature_k=300, temperature_source=TemperatureMessage.TS_SEA_TEMPERATURE)

# Send it.
bus.send(p.to_can())

```

## See Also

* PGN Definitions were supplied from the canboatjs project https://www.npmjs.com/package/@canboat/pgns (Many thanks!)

