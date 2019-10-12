import time
from threading import Thread
import blynklib
# Importing modules
import spidev # To communicate with SPI devices
from numpy import interp	# To scale values
from time import sleep	# To add delay
import RPi.GPIO as GPIO	# To use GPIO pins

#blynk auth token and init

BLYNK_AUTH = 'YlDEykDXy-5CSGx_wkO_7DCmS96s82gu'
blynk = blynklib.Blynk(BLYNK_AUTH)

# Start SPI connection
spi = spidev.SpiDev() # Created an object
spi.open(0,0)	

# Initializing LED pin as OUTPUT pin
#led_pin = 20
#GPIO.setmode(GPIO.BCM)
#GPIO.setup(led_pin, GPIO.OUT)
# Creating a PWM channel at 100Hz frequency
#pwm = GPIO.PWM(led_pin, 100)
#pwm.start(0)

temp=0
humidity=0
light=0

# Read MCP3008 data
def analogInput(channel):
  spi.max_speed_hz = 1350000
  adc = spi.xfer2([1,(8+channel)<<4,0])
  data = ((adc[1]&3) << 8) + adc[2]
  return data
  	
def Volts(data):
  volts = (data * 3.3) / float(1023)
  volts = round(volts, 2) # Round off to 2 decimal places
  return volts

def Temp(volts):
  temperature = (volts-0.5)/10
  return temperature

localtime = time.asctime( time.localtime(time.time()) )
oldsec = int((localtime[17:19]))
newsec = 0

def readADC():

  while True:
    global humidity
    global light
    global temp

    humidity = Volts(analogInput(0)) # Reading from CH0
    light = analogInput(1) #read from CH1
    temp = Temp(analogInput(2)) #read from CH2

x = Thread(target = readADC)
x.setDaemon(True)
x.start()

@blynk.handle_event('read V0')
def read_virtual_pin_handler(pin):

  blynk.virtual_write(0, str(humidity))
  blynk.virtual_write(1, str(light))
  blynk.virtual_write(2, str(temp))


while True:

    localtime = time.asctime( time.localtime(time.time()) )
    newsec = int((localtime[17:19]))
    blynk.run()

    if newsec==oldsec+1:
              
        print("newsec: "+str(newsec))
        print("oldsec: "+str(oldsec))
        
        print("humidity reading: " + str(humidity))
        print("light reading: " + str(light))
        print("temperature reading: " + str(temp))

        oldsec=newsec

        if oldsec==59:
            oldsec=0
            time.sleep(0.1)
       
