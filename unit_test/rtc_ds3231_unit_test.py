import time
import board
import busio
import adafruit_ds3231
import unittest

class TestDS3231(unittest.TestCase):

    def setUp(self):
        # Initialize I2C and DS3231
        i2c = busio.I2C(board.SCL, board.SDA)
        self.ds3231 = adafruit_ds3231.DS3231(i2c)

    def test_read_time(self):
        # Read the current time from the DS3231
        current_time = self.ds3231.datetime
        print(f"Current RTC time: {current_time}")

        # Check if the time is a valid datetime object
        self.assertIsInstance(current_time, type(time.localtime()), "Failed to read time from DS3231")

        # Optional: Check if the year is realistic (not the default value)
        self.assertGreater(current_time.tm_year, 2023, "RTC seems to have an incorrect year set.")

    def tearDown(self):
        # Clean up if necessary
        pass

if __name__ == '__main__':
    unittest.main()