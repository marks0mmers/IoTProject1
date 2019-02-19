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
client = mqtt.Client('pi_a_client')

#setup function for some setup---custom function
def setup():
    #set the gpio modes to BCM numbering
    GPIO.setmode(GPIO.BCM)
    # set up the SPI interface pins
    GPIO.setup(MOSI, GPIO.OUT)
    GPIO.setup(MISO, GPIO.IN)
    GPIO.setup(CLK, GPIO.OUT)
    GPIO.setup(CS, GPIO.OUT)
    client.connect(host='174.99.21.72', port="1883", keepalive="60", bind_address="")
    pass

def on_message(client, userdata, message):
    print("message received " ,str(message.payload.decode("utf-8")))
    print("message topic=",message.topic)
    print("message qos=",message.qos)
    print("message retain flag=",message.retain)

def main():
    print('Reading MCP3008 values, press Ctrl-C to quit...')
    client.on_message = on_message
    client.loop_start()
    # Print nice channel column headers.
    print('| {0:>4} | {1:>4} |'.format(*range(2)))
    print('-' * 57)
    # Main program loop.
    while True:
        # Read all the ADC channel values in a list.
        values = [0]*2
        # The read_adc function will get the value of the specified channel (0-7).
        values[0] = mcp.read_adc(0) * 1.0 / LIGHT_MAX
        values[1] = mcp.read_adc(1) * 1.0 / POTENT_MAX
        client.publish("lightSensor", values[0])
        client.publish("threshold", values[1])


        # Print the ADC values.
        print('| {0:>4} | {1:>4} |'.format(*values))
        time.sleep(1)


#define a destroy function for clean up everything after the script finished
def destroy():
    #release resource
    GPIO.cleanup()
    client.loop_stop()
    
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
