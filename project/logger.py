import time
from threading import Thread
import blynklib
# Importing modules
import spidev # To communicate with SPI devices
from numpy import interp	# To scale values
from time import sleep	# To add delay
import RPi.GPIO as GPIO	# To use GPIO pins
from prettytable import PrettyTable

GPIO.setmode(GPIO.BCM)

#blynk auth token and init

BLYNK_AUTH = 'YlDEykDXy-5CSGx_wkO_7DCmS96s82gu'
blynk = blynklib.Blynk(BLYNK_AUTH)

# Start SPI connection
spi = spidev.SpiDev() # Created an object
spi.open(0,0)	

GPIO.setup(5, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(6, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

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
sampletime=1
localtime=0
systime=0
t0=time.time()
monitoring=1

def sampleCallback(channel):
  
  global sampletime

  if sampletime==1:
    sampletime=2
  elif sampletime==2:
    sampletime=5
  elif sampletime==5:
    sampletime=1

GPIO.add_event_detect(5, GPIO.RISING, callback=sampleCallback, bouncetime=300)

def monitoringCallback(channel):

  global monitoring

  if monitoring==1:
    monitoring=0
  elif monitoring==0:
    monitoring=1

GPIO.add_event_detect(6, GPIO.RISING, callback=monitoringCallback, bouncetime=300)

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


def readADC():

  global humidity
  global light
  global temp
  global sampletime
  global localtime
  global systime
  global t0
  global monitoring

  localtime = time.asctime( time.localtime(time.time()) )
  systime = time.strftime("%H:%M:%S", time.gmtime(time.time()-t0))


  while True:

    if monitoring==1:
      humidity = Volts(analogInput(0)) # Reading from CH0
      light = analogInput(1) #read from CH1
      temp = Temp(analogInput(2)) #read from CH2

    localtime = time.asctime( time.localtime(time.time()) )
    systime = time.strftime("%H:%M:%S", time.gmtime(time.time()-t0))
    time.sleep(sampletime)

x = Thread(target = readADC)
x.setDaemon(True)
x.start()

@blynk.handle_event('read V0')
def read_virtual_pin_handler(pin):

  blynk.virtual_write(0, str(humidity))
  blynk.virtual_write(1, str(light))
  blynk.virtual_write(2, str(temp))

try:

  t=PrettyTable(['RTC Time', 'Sys Timer', 'Humidity', 'Temp', 'Light', 'DAC Out', 'Alarm'])

  while True:

    
    blynk.run()

    t.add_row([str(localtime[10:19]), str(systime), str(humidity), str(temp), str(light),' ', ' '])
    print(t)

    time.sleep(0.9)

except KeyboardInterrupt:
  GPIO.cleanup()
       
