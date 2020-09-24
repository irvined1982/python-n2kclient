import logging

import j1939
from bitstring import BitArray, Bits

logger = logging.getLogger(__name__)


class NMEA2000PGN(j1939.PGN):
    @property
    def is_destination_specific(self):
        return False


class N2KMessage(object):
    field_config = {}

    def send(self, bus):
        bus.send(self.to_can())

    def __init__(self, sid=0x00, field_data=None, *args, **kwargs):
        self.sid = sid
        assert isinstance(field_data, list)
        self.field_data = field_data

    def to_can(self):
        p = NMEA2000PGN()
        p.value = self.field_config['PGN']

        data = self.get_payload()
        aid = j1939.ArbitrationID(pgn=p)
        pdu = j1939.PDU(timestamp=0.0, arbitration_id=aid, data=data, info_strings=None)
        return pdu

    def get_payload(self):
        payload_bits = BitArray(length=8 * 8)  # 8 Byte Message

        field_index = 0
        for fieldConfig in sorted(self.field_config['Fields'], key=lambda f: f['Order']):
            logger.debug(fieldConfig)
            length = fieldConfig['BitLength']
            offset = fieldConfig['BitOffset']
            signed = fieldConfig['Signed']
            start = fieldConfig['BitStart']

            if fieldConfig['BitStart'] == 0:
                if length < 8:
                    position = offset + 8 - length
                else:
                    position = offset
            else:
                position = offset - start

            logger.debug("Field {name} starts at: {position}".format(name=fieldConfig['Name'], position=position))
            logger.debug("Field {name} length is: {length}".format(name=fieldConfig['Name'], length=length))

            try:
                resolution = fieldConfig['Resolution']
            except KeyError:
                resolution = None

            value = self.field_data[field_index]
            logger.debug("Value before conversion is: %s" % value)

            if value is not None:
                if resolution is not None:
                    value = int(float(value) / float(resolution))

                if not signed:
                    logger.debug("Field {name} is unsigned".format(name=fieldConfig['Name']))
                    value = Bits(uint=value, length=length)
                else:
                    logger.debug("Field {name} is signed".format(name=fieldConfig['Name']))
                    value = Bits(int=value, length=length)
            else:
                value = BitArray(length=length)
                value.invert()
                if signed:
                    value[0] = False
                value = Bits(value)

            logger.debug(
                "Field {name} value post conversion: {value}".format(name=fieldConfig['Name'], value=value))

            if length % 8 == 0:
                value = Bits(bytes=reversed(value.bytes))
            payload_bits.overwrite(value, position)

            field_index += 1

        pad = 8 * 8 - len(payload_bits)
        if (pad > 0):
            payload_bits.append(Bits(length=pad))
        data = list(payload_bits.bytes)

        logger.debug("Payload data is: %s" % data)
        return data


class TemperatureMessage(N2KMessage):
    pgn = 0x1FD07
    field_config = {
        "PGN": 0x1FD07,
        "Id": "environmentalParameters",
        "Description": "Environmental Parameters",
        "Type": "Single",
        "Complete": True,
        "Length": 8,
        "RepeatingFields": 0,
        "Fields": [
            {
                "Order": 1,
                "Id": "sid",
                "Name": "SID",
                "BitLength": 8,
                "BitOffset": 0,
                "BitStart": 0,
                "Signed": False},
            {
                "Order": 2,
                "Id": "temperatureSource",
                "Name": "Temperature Source",
                "BitLength": 6,
                "BitOffset": 8,
                "BitStart": 0,
                "Type": "Lookup table",
                "Signed": False,
                "EnumValues": [
                    {"name": "Sea Temperature", "value": "0"},
                    {"name": "Outside Temperature", "value": "1"},
                    {"name": "Inside Temperature", "value": "2"},
                    {"name": "Engine Room Temperature", "value": "3"},
                    {"name": "Main Cabin Temperature", "value": "4"},
                    {"name": "Live Well Temperature", "value": "5"},
                    {"name": "Bait Well Temperature", "value": "6"},
                    {"name": "Refridgeration Temperature", "value": "7"},
                    {"name": "Heating System Temperature", "value": "8"},
                    {"name": "Dew Point Temperature", "value": "9"},
                    {"name": "Apparent Wind Chill Temperature", "value": "10"},
                    {"name": "Theoretical Wind Chill Temperature", "value": "11"},
                    {"name": "Heat Index Temperature", "value": "12"},
                    {"name": "Freezer Temperature", "value": "13"},
                    {"name": "Exhaust Gas Temperature", "value": "14"}]},
            {
                "Order": 3,
                "Id": "humiditySource",
                "Name": "Humidity Source",
                "BitLength": 2,
                "BitOffset": 14,
                "BitStart": 6,
                "Type": "Lookup table",
                "Signed": False,
                "EnumValues": [
                    {"name": "Inside", "value": "0"},
                    {"name": "Outside", "value": "1"}]},
            {
                "Order": 4,
                "Id": "temperature",
                "Name": "Temperature",
                "BitLength": 16,
                "BitOffset": 16,
                "BitStart": 0,
                "Units": "K",
                "Type": "Temperature",
                "Resolution": "0.01",
                "Signed": False},
            {
                "Order": 5,
                "Id": "humidity",
                "Name": "Humidity",
                "BitLength": 16,
                "BitOffset": 32,
                "BitStart": 0,
                "Units": "%",
                "Resolution": "0.004",
                "Signed": True},
            {
                "Order": 6,
                "Id": "atmosphericPressure",
                "Name": "Atmospheric Pressure",
                "BitLength": 16,
                "BitOffset": 48,
                "BitStart": 0,
                "Units": "hPa",
                "Type": "Pressure",
                "Signed": False
            }
        ]
    }

    TS_SEA_TEMPERATURE = 0
    TS_OUTSIDE_TEMPERATURE = 1
    TS_INSIDE_TEMPERATURE = 2
    TS_ENGINE_ROOM_TEMPERATURE = 3
    TS_MAIN_CABIN_TEMPERATURE = 4
    TS_LIVE_WELL_TEMPERATURE = 5
    TS_BAIT_WELL_TEMPERATURE = 6
    TS_REFRIGERATION_TEMPERATURE = 7
    TS_HEATING_SYSTEM_TEMPERATURE = 8
    TS_DEW_POINT_TEMPERATURE = 9
    TS_APPARENT_WIND_CHILL_TEMPERATURE = 10
    TS_THEORETICAL_WIND_CHILL_TEMPERATURE = 11
    TS_HEAT_INDEX_TEMPERATURE = 12
    TS_FREEZER_TEMPERATURE = 13
    TS_EXHAUST_GAS_TEMPERATURE = 14

    TS_DESCRIPTIONS = {
        TS_SEA_TEMPERATURE: 'Sea Temperature',
        TS_OUTSIDE_TEMPERATURE: 'Outside Temperature',
        TS_INSIDE_TEMPERATURE: 'Inside Temperature',
        TS_ENGINE_ROOM_TEMPERATURE: 'Engine Room Temperature',
        TS_MAIN_CABIN_TEMPERATURE: 'Main Cabin Temperature',
        TS_LIVE_WELL_TEMPERATURE: 'Live Well Temperature',
        TS_BAIT_WELL_TEMPERATURE: 'Bait Well Temperature',
        TS_REFRIGERATION_TEMPERATURE: 'Refrigeration Temperature',
        TS_HEATING_SYSTEM_TEMPERATURE: 'Heating System Temperature',
        TS_DEW_POINT_TEMPERATURE: 'Dew Point Temperature',
        TS_APPARENT_WIND_CHILL_TEMPERATURE: 'Apparent Wind Chill Temperature',
        TS_THEORETICAL_WIND_CHILL_TEMPERATURE: 'Theoretical Wind Chill Temperature',
        TS_HEAT_INDEX_TEMPERATURE: 'Heat Index Temperature',
        TS_FREEZER_TEMPERATURE: 'Freezer Temperature',
        TS_EXHAUST_GAS_TEMPERATURE: 'Exhaust Gas Temperature',
    }

    HS_INSIDE = 0
    HS_OUTSIDE = 1

    HS_DESCRIPTIONS = {
        HS_INSIDE: 'Inside Humidity',
        HS_OUTSIDE: 'Outside Humidity',
    }

    def __init__(self, sid, temperature_source=None, humidity_source=None, temperature_k=None, humidity_pct=None,
                 atmospheric_pressure_hpa=None, *args, **kwargs):
        if temperature_source is not None:
            assert temperature_source in self.TS_DESCRIPTIONS
        if humidity_source is not None:
            assert humidity_source in self.HS_DESCRIPTIONS
        if humidity_pct is not None:
            assert (humidity_pct >= 0)
            assert (humidity_pct <= 100)

        field_data = [sid, temperature_source, humidity_source, temperature_k, humidity_pct, atmospheric_pressure_hpa]

        super(TemperatureMessage, self).__init__(field_data=field_data, *args, **kwargs)
