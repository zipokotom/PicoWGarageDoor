# PicoWGarageDoor
A simple garage door opener, status checker &amp; Temperature Sensor using MQTT, the Pico W, and Home Assistant.  The code uses libraries from [mqtt_as](https://github.com/peterhinch/micropython-mqtt) for MQTT and Wifi connectivity and [micropython-bmp280](https://github.com/dafvid/micropython-bmp280/tree/master) for temperature readings from the BMP280.

## Hardware Requirements
This setup relies on an electric garage door opener that can take a single-button hardwired switch (i.e. each time the switch is closed, the door cycles between open, stop, and close).  This is connected to Pin 20 (`pin_imp`) on the Pico W via a 3.3V relay.

The temperature is provided by a BMP280/BME280 connected to Pins 0/1 (`i2c`).

Because the door uses a single button to control up/stop/down/stop, it is necessary to have an external sensor such as a "window security magnetic reed switch".  This is connected to Pin 13 (`door_sensor`).

## Home Assistant Setup
The code uses MQTT to connect and communicate with Home Assistant, which is used to see the status of the door, temperature, and control the opening/closing.

The `config['server']`, `config['user']`, `config['password']`, and `config['client_id']` variables should be updated with the values defined during the MQTT setup.  Sensors are then set up in MQTT to subscribe to the messages in `topic_pub` and `topic_pub_temp`, which display the door status & temperature.  A button is created in HA to publish the message defined in `topic_sub`, which controls the up/stop/down/stop cycle of the door.
