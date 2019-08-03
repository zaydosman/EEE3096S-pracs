#!/usr/bin/python3
"""
Python Practical Template
Keegan Crankshaw
Readjust this Docstring as follows:
Names: Zayd Osman
Student Number: OSMMOH020
Prac: 1
Date: <22/07/2019>
"""

# import Relevant Librares
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)
GPIO.setup(32, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(12, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(18, GPIO.OUT, initial=GPIO.LOW)

GPIO.setwarnings(False)
GPIO.setup(7, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

x=0
b="......"

def button_callback(channel):

    global x
    global b

    if x==8:
      x=0
    #GPIO.output(32,1)
    x+=1
    b=str(bin(x))
    print(b)
   # time.sleep(2)

def button_callback2(channel):

    global x
    global b

    if x==0:
        x=8

    x-=1
    b=str(bin(x))
    print(b)
   # time.sleep(2)

GPIO.add_event_detect(7,GPIO.RISING,callback=button_callback,bouncetime=300)
GPIO.add_event_detect(16,GPIO.RISING,callback=button_callback2,bouncetime=300)
# Logic that you write
def main():

    global x
    global b

    if b[-1]=="1":
        GPIO.output(32,1)
    else:
        GPIO.output(32,0)

    if b[-2]=="1":
        GPIO.output(12,1)
    else:
        GPIO.output(12,0)

    if b[-3]=="1":
        GPIO.output(18,1)
    else:
        GPIO.output(18,0)

   #GPIO.cleanup()
# Only run the functions if 
if __name__ == "__main__":
    # Make sure the GPIO is stopped correctly
    try: 
        while True:
            main()
    except KeyboardInterrupt:
        print("Exiting gracefully")
        # Turn off your GPIOs here
        GPIO.cleanup()
    except Exception as e:
        GPIO.cleanup()
        print("Some other error occurred")
        print(e.message)
