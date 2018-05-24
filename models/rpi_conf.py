import datetime
import time

import RPi.GPIO as GPIO

import dht11

# delay between two readings if the first was not valid
retry_delay = 1

led_status = {'r': False, 'y': False, 'g': False}  # False ->OFF, True -> ON


class RPiConfigs(object):
    """Configuration class to call when initializing a session with RPi"""

    def __init__(self, LCD_output, green_led_pin, yellow_led_pin, red_led_pin, moisture_temp_sensor_pin=17):
        self.moisture_temp_pin = moisture_temp_sensor_pin
        self.green_led_pin = green_led_pin
        self.yellow_led_pin = yellow_led_pin
        self.red_led_pin = red_led_pin
        self.moisture_sensor_instance = dht11.DHT11(pin=moisture_temp_sensor_pin)
        self.led_mapping = {'r': red_led_pin, 'g': green_led_pin, 'y': yellow_led_pin}

        # initialize GPIO
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.cleanup()

    def change_LED_status(self, action, led_color='r'):
        """Change LED status according to specified action"""
        if led_color not in led_status.keys():
            print('No LED with the selected color')
        else:
            if action == 'OFF':
                GPIO.output(self.led_mapping[led_color], GPIO.LOW)
                led_status[led_color] = False
            else:
                GPIO.output(self.led_mapping[led_color], GPIO.HIGH)
                led_status[led_color] = True

    @property
    def read_temperature(self):
        """Read temperature in Celsius degrees from the sensor"""
        while True:
            result = self.moisture_sensor_instance.read()
            if result.is_valid():
                return str(datetime.datetime.now()), self.moisture_sensor_instance.read().temperature
            else:
                time.sleep(retry_delay)

    @property
    def read_humidity(self):
        """Read relative humidity from the sensor"""
        while True:
            result = self.moisture_sensor_instance.read()
            if result.is_valid():
                return str(datetime.datetime.now()), self.moisture_sensor_instance.read().humidity
            else:
                time.sleep(retry_delay)
