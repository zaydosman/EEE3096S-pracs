import time
from threading import Thread
import blynklib
# Importing modules
import spidev # To communicate with SPI devices
from numpy import interp	# To scale values
from time import sleep	# To add delay
import RPi.GPIO as GPIO	# To use GPIO pins
from prettytable import PrettyTable
import os

GPIO.setmode(GPIO.BCM)

#blynk auth token and init

BLYNK_AUTH = 'YlDEykDXy-5CSGx_wkO_7DCmS96s82gu'
blynk = blynklib.Blynk(BLYNK_AUTH)

# Start SPI connection
spi = spidev.SpiDev() # Created an object
spi.open(0,0)	

GPIO.setup(5, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(6, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

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
cleartable=0
dacout=0
alarm=0
alarmreset=0


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

def resetCallback(channel):
  
  global cleartable
  global t0

  cleartable=1

  t0=time.time()
  

GPIO.add_event_detect(13, GPIO.RISING, callback=resetCallback, bouncetime=300)

def alarmResetCallback(channel):

  global alarm
  global alarmreset

  alarm = 0
  alarmreset = 1

GPIO.add_event_detect(26, GPIO.RISING, callback=alarmResetCallback, bouncetime=300)

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
  global dacout

  localtime = time.asctime( time.localtime(time.time()) )
  systime = time.strftime("%H:%M:%S", time.gmtime(time.time()-t0))


  while True:

    if monitoring==1:
      humidity = Volts(analogInput(0)) # Reading from CH0
      light = analogInput(1) #read from CH1
      temp = Temp(analogInput(2)) #read from CH2

    localtime = time.asctime( time.localtime(time.time()) )
    systime = time.strftime("%H:%M:%S", time.gmtime(time.time()-t0))

    dacout=(light/1023)*humidity
    dacout=round(dacout, 2)

    time.sleep(sampletime)

x = Thread(target = readADC)
x.setDaemon(True)
x.start()

def Alarm():

  sleep(1)
  global dacout
  global alarm
  global alarmreset

  while True:
    
    if dacout<0.65 or dacout>2.65:
      alarm=1

    if alarmreset == 1:
      alarmreset=0
      sleep(180)

  
y=Thread(target = Alarm)
y.setDaemon(True)
y.start()

@blynk.handle_event('read V0')
def read_virtual_pin_handler(pin):

  blynk.virtual_write(0, str(humidity))
  blynk.virtual_write(1, str(light))
  blynk.virtual_write(2, str(temp))

try:

  t=PrettyTable(['RTC Time', 'Sys Timer', 'Humidity', 'Temp', 'Light', 'DAC Out', 'Alarm'])

  while True:

    
    blynk.run()

    t.add_row([str(localtime[10:19]), str(systime), str(humidity), str(temp), str(light),str(dacout), str(alarm)])
    print(t)

    if cleartable ==1:
      t.clear_rows()
      cleartable=0
      os.system('clear')

    time.sleep(sampletime-0.1)

except KeyboardInterrupt:
  GPIO.cleanup()
       
