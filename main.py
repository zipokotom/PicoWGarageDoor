from mqtt_as import MQTTClient, config
from bmp280 import BMP280
import uasyncio as asyncio
from machine import Pin, I2C
from time import sleep

# Hardware definitions
led = Pin("LED", Pin.OUT)
led.value(1)
#pin_imp = Pin(20, Pin.OUT, Pin.PULL_DOWN)
pin_imp = Pin(20, Pin.OUT, Pin.PULL_DOWN)
door_sensor = Pin(13, Pin.IN, Pin.PULL_DOWN)
i2c=I2C(0,sda=Pin(0), scl=Pin(1), freq=400000)


# Configure MQTT

topic_sub = b'custom/garage/command'
topic_pub = b'custom/garage/status'
topic_pub_temp = b'custom/garage/temperature'

config['server'] = '192.168.1.1'  # Your MQTT Server ID
config['user'] = '' # Your MQTT Username
config['password'] = '' # Your MQTT Password
config['client_id'] = '' # Your MQTT Client ID

# Not sure what this does
config['will'] = ('notsure', 'Goodbye cruel world!', False, 0)
config['keepalive'] = 120
config["queue_len"] = 1  # Use event interface with default queue

# Wifi config
config['ssid'] = '' # Wifi SSID
config['wifi_pw'] = '' # Wifi Password


outages = 0
    
async def pulse():  # Pulses the onboard LED
    led.on()
    await asyncio.sleep(1)
    led.off()

async def messages(client): # Respond to incoming messages
    async for topic, msg, retained in client.queue:
        print(f'Topic: "{topic.decode()}" Message: "{msg.decode()}" Retained: {retained}')
        if msg.decode() == "imp":
            control_door()


async def down(client):
    global outages
    while True:
        await client.down.wait()  # Pause until connectivity changes
        client.down.clear()
        outages += 1
        print('WiFi or broker is down.')

async def up(client):
    while True:
        await client.up.wait()
        client.up.clear()
        print('We are connected to broker.')
        await client.subscribe(topic_sub, 1)

def control_door():
    pin_imp.on()
    sleep(0.5)
    pin_imp.off()
    asyncio.create_task(pulse())

# Configure Door Status Check

state = 0

async def door_status():
    global state
    global client
    
    if state == 0 and door_sensor.value() == 0: # door_sensor.value() == 0 is door open, 1 is door closed
        
        state = 1
        
        status = "Door Open"
        
        await client.publish(topic_pub, status)
        
        print(status)
    
    elif state == 1 and door_sensor.value() == 1:
        
        state = 0
        
        status = "Door Closed"
        
        await client.publish(topic_pub, status)
        
        print(status)
    
    asyncio.sleep_ms(200)

# Configure Temperature Sensor
async def temp():
    
    while True:
        bmp = BMP280(i2c)
        
        await client.publish(topic_pub_temp, str(bmp.temperature))
        
        print(bmp.temperature)


        await asyncio.sleep(60) # Check every 10 minutes


# Set up the main code
async def main(client):
    try:
        await client.connect()
        asyncio.create_task(pulse())
    except OSError:
        print('Connection failed.')
        return
    for task in (up, down, messages):
        asyncio.create_task(task(client))

    asyncio.create_task(temp())

    
    while True:
        await asyncio.sleep(5)
    
        
        asyncio.create_task(door_status())
        
    
# Run it
client = MQTTClient(config)

try:
    asyncio.run(main(client))
finally:  # Prevent LmacRxBlk:1 errors.
    client.close()
    asyncio.new_event_loop()


    
    
    
    
    
