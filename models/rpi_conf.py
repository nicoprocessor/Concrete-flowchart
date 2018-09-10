import datetime
import time

import RPi.GPIO as GPIO

# import I2C_LCD_driver
import dht11

# delay between two readings if the first was not valid
retry_delay = 1

LED_status = {'r': False, 'y': False, 'g': False}  # False ->OFF, True -> ON
LED_colors = ['r', 'y', 'g']


class RPiConfigs(object):
    """Configuration class to call when initializing a session with RPi"""

    def __init__(self, green_LED_pin, yellow_LED_pin, red_LED_pin, moisture_temp_sensor_pin):
        self.moisture_temp_pin = moisture_temp_sensor_pin
        self.green_LED_pin = green_LED_pin
        self.yellow_LED_pin = yellow_LED_pin
        self.red_LED_pin = red_LED_pin
        self.moisture_sensor_instance = dht11.DHT11(pin=moisture_temp_sensor_pin)
        self.LED_mapping = {'r': red_LED_pin, 'g': green_LED_pin, 'y': yellow_LED_pin}
        # self.lcd = I2C_LCD_driver.lcd()

        # initialize GPIO
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.cleanup()

    # def clear_lcd(self):
    #     """Clears the lcd screen"""
    #     self.lcd.lcd_clear()

    # def write_lcd_for_time_interval(self, row1, row2, time_interval):
    #     """Displays the given strings at the given position, for the time interval"""
    #     self.lcd.lcd_display_string(row1, 1, 0)
    #     self.lcd.lcd_display_string(row2, 2, 0)
    #     time.sleep(time_interval)
    #     self.clear_lcd()

    def change_LED_status(self, action, LED_color='r'):
        """Changes a particular LED status according to specified action"""
        if LED_color not in LED_colors:
            print('No LED with the selected color')
        else:
            if action == 'OFF':
                GPIO.output(self.LED_mapping[LED_color], GPIO.LOW)
                LED_status[LED_color] = False
            else:
                GPIO.output(self.LED_mapping[LED_color], GPIO.HIGH)
                LED_status[LED_color] = True

    def switch_off_all(self):
        """Switches off all the LEDs connected"""
        for l in LED_colors:
            self.change_LED_status(action='OFF', LED_color=l)

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
