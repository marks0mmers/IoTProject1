import time
import os
import RPi.GPIO as GPIO
import smbus
import Adafruit_MCP3008
import paho.mqtt.client as mqtt

# change these as desired - they're the pins connected from the
# SPI port on the ADC to the Cobbler
CLK = 11
MISO = 9
MOSI = 10
CS = 8
analogChannel = 0;

mcp = Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)

LIGHT_MAX = 1200
POTENT_MAX = 1023
THRESHOLD = .075

client = mqtt.Client('pi_a_client', clean_session = False)

def on_log(client, userdata, level, buf):
    test = 1

def on_disconnect(client, userdata, flags, rc=0):
    ret = client.publish("Status/RasberryPiA", "offline", qos = 2, retain = True)
    print("Publish ", ret) 
    print("Disconnected OK")
    
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        # Set flag that a client is connected
        print("Connected OK")
    else:
        print("Bad connection! Returned code = ", rc)
        client.loop_stop()

def on_message(client, userdata, message):
    print("message received " ,str(message.payload.decode("utf-8")))
    #print("message topic=",message.topic)
    #print("message qos=",message.qos)
    #print("message retain flag=",message.retain)

#setup function for some setup---custom function
def setup():
    #set the gpio modes to BCM numbering
    GPIO.setmode(GPIO.BCM)
    
    # set up the SPI interface pins
    GPIO.setup(MOSI, GPIO.OUT)
    GPIO.setup(MISO, GPIO.IN)
    GPIO.setup(CLK, GPIO.OUT)
    GPIO.setup(CS, GPIO.OUT)
    
    # Bind call backs
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_log = on_log
    client.on_message = on_message
    
    # Set last will message
    lwm = "offline"
    lastWillTopic = "Status/RaspberryPiA"
    client.will_set(lastWillTopic, lwm, qos = 2, retain = True)
    
    client.connect(host="10.153.3.190", port="1883")
    pass

def main():
    print('Reading MCP3008 values, press Ctrl-C to quit...')

    # Main program loop. 
    client.loop_start()
    prevLight = 0.0
    prevPotent = 0.0
        
    ret = client.publish("Status/RaspberryPiA", "online", qos = 2, retain = True)
    print("Publish ", ret)
    client.subscribe("lightSensor", 2)
    client.subscribe("threshold", 2)
    while True:
        # Read all the ADC channel values in a list.
        values = [0]*2
        # The read_adc function will get the value of the specified channel (0-7).
        values[0] = mcp.read_adc(0) * 1.0 / LIGHT_MAX
        values[1] = mcp.read_adc(1) * 1.0 / POTENT_MAX

        #compare values against threshold on whether or not to send the values
        
        if abs(values[0] - prevLight) > THRESHOLD or abs(values[1] - prevPotent) > THRESHOLD:
            prevLight = values[0]
            prevPotent = values[1]
            client.publish("lightSensor", values[0], qos = 2, retain = True)
            client.publish("threshold", values[1], qos = 2, retain = True)

        time.sleep(.1)

#define a destroy function for clean up everything after the script finished
def destroy():
    #release resource
    GPIO.cleanup()
    client.publish("Status/RaspberryPiA", "offline", qos=2, retain=True)    
    client.disconnect()
    
#
# if run this script directly ,do:
if __name__ == '__main__':
    setup()
    try:
            main()
    #when 'Ctrl+C' is pressed,child program destroy() will be executed.
    except KeyboardInterrupt:
        destroy()
        pass
