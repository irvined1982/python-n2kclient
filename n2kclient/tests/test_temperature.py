from unittest import TestCase
from n2kclient import TemperatureMessage
import logging

logging.basicConfig(level=logging.DEBUG)


class TestTemperature(TestCase):
    def test_temp(self):
        # Multi byte numbers should be encoded big endian.
        values = [
            (
                300, (0x30, 0x75)
            ),
            (
                400, (0x40, 0x9C),
            )
        ]
        for temp, output in values:
            b1, b2 = output
            a = TemperatureMessage(sid=0x00, temperature_k=temp)

            msg = a.get_payload()

            self.assertEqual(msg[0], 0x00)
            self.assertEqual(msg[1], 0xFF)
            self.assertEqual(msg[2], b1)
            self.assertEqual(msg[3], b2)
            self.assertEqual(msg[4], 0xFF)
            self.assertEqual(msg[5], 0x7F)
            self.assertEqual(msg[6], 0xFF)
            self.assertEqual(msg[7], 0xFF)

    def test_enums(self):
        logging.getLogger("n2kclient").setLevel(logging.DEBUG)
        for ts in TemperatureMessage.TS_DESCRIPTIONS.keys():
            for hs in TemperatureMessage.HS_DESCRIPTIONS.keys():
                hs_s = hs << 6

                expected = hs_s | ts
                a = TemperatureMessage(sid=0x00, temperature_k=300, temperature_source=ts, humidity_source=hs)

                msg = a.get_payload()
                self.assertEqual(msg[0], 0x00)
                self.assertEqual(msg[1], expected)
                self.assertEqual(msg[2], 0x30)
                self.assertEqual(msg[3], 0x75)
                self.assertEqual(msg[4], 0xFF)
                self.assertEqual(msg[5], 0x7F)
                self.assertEqual(msg[6], 0xFF)
                self.assertEqual(msg[7], 0xFF)
