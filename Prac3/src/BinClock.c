/*
 * BinClock.c
 * Jarrod Olivier
 * Modified for EEE3095S/3096S by Keegan Crankshaw
 * August 2019
 * 
 * <OSMMOH020> <BLCDEV001>
 * Date
*/


//this comment is checking if u can merge my repo again
#include <wiringPi.h>
#include <wiringPiI2C.h>
#include <stdio.h> //For printf functions
#include <stdlib.h> // For system functions
#include <signal.h>
#include <unistd.h>
#include <math.h>
#include <string.h>

#include "BinClock.h"
#include "CurrentTime.h"

//Global variables
int hours, mins, secs;
long lastInterruptTime = 0; //Used for button debounce
int RTC; //Holds the RTC instance
int HH,MM,SS;
int initosc = 0x80;
void initGPIO(void){
	/* 
	 * Sets GPIO using wiringPi pins. see pinout.xyz for specific wiringPi pins
	 * You can also use "gpio readall" in the command line to get the pins
	 * Note: wiringPi does not use GPIO or board pin numbers (unless specifically set to that mode)
	 */
	printf("Setting up\n");
	wiringPiSetup(); //This is the default mode. If you want to change pinouts, be aware
	RTC = wiringPiI2CSetup(RTCAddr); //Set up the RTC
	wiringPiI2CWriteReg8(RTC, HOUR, 0x00);
	wiringPiI2CWriteReg8(RTC, SEC, 0b10000000);
	//Set up the LEDS
	for(int i; i < sizeof(LEDS)/sizeof(LEDS[0]); i++){
	    pinMode(LEDS[i], OUTPUT);
	}
	
	//Set Up the Seconds LED for PWM
	softPwmCreate(SECS, 0, 60);
	//Write your logic here
	
	printf("LEDS done\n");
	
	//Set up the Buttons
	for(int j; j < 3; j++){
		pinMode(BTNS[j], INPUT);
		pullUpDnControl(BTNS[j], PUD_UP);
	}
	
	//Attach interrupts to Buttons
	//Write your logic here
	wiringPiISR (BTNS[0], INT_EDGE_RISING, &hourInc); //Interrupt for hour increment button
	wiringPiISR (BTNS[1], INT_EDGE_RISING, &minInc); //Interrupt for minute increment button
	
	printf("BTNS done\n");
	printf("Setup done\n");
}
void GPIO_cleanup(void){

	for(int i; i < sizeof(LEDS)/sizeof(LEDS[0]); i++){
            pinMode(LEDS[i], INPUT);
        }

}

static void sig_handler(int signo, siginfo_t *siginfo, void *context){

	if(signo == SIGINT){
		GPIO_cleanup();
		exit(0);
		printf("flag");
	}

}

int toHex(int dec){
	printf("\n dec before hex conversion: %d", dec);
        int hex;
	int remainder;
	int count=0;

	for(count=0; dec>1; count++){

	remainder=dec%16;
	hex = hex + remainder * pow(10, count);
	dec=dec/16;

	}
	printf("\n dec after hex conversion: %d", hex);
	return hex;

}

int toDec(int hex){

	char hexVal[2];
	sprintf(hexVal, "%x", hex);
	printf("\n char array is:%s", hexVal);
	int len = strlen(hexVal);

	int base =1;

	int dec = 0;

	for (int i = len-1; i>=0; i--){

		if(hexVal[i]>='0' && hexVal[i]<='9'){

			dec+=(hexVal[i]-48)*base;

			base=base*16;

		}

		else if(hexVal[i]>='A' && hexVal[i]<='F'){

			dec+=(hexVal[i]-55)*base;
			base=base*16;

		}

	}

	printf("\nhex after dec conversion: %d", dec);
	return dec+1;

}


/*
 * The main function
 * This function is called, and calls all relevant functions we've written
 */
int main(void){

	struct sigaction act;
	memset(&act, '\0', sizeof(act));
	act.sa_sigaction=&sig_handler;
	act.sa_flags = SA_SIGINFO;

	if(sigaction(SIGINT, &act, NULL)<0){
                        perror("sigaction");
                        return 1;
                }

	initGPIO();
	toggleTime();

	//Set random time (3:04PM)
	//You can comment this file out later

	wiringPiI2CWriteReg8(RTC, HOUR,0x13+TIMEZONE);
	wiringPiI2CWriteReg8(RTC, MIN, 0x4);
	//wiringPiI2CWriteReg8(RTC, SEC, initosc);

	// Repeat this until we shut down
	for (;;){

		//Fetch the time from the RTC
		//Write your logic here
		HH = wiringPiI2CReadReg8(RTC, HOUR);
		MM = wiringPiI2CReadReg8(RTC, MIN);
		SS = wiringPiI2CReadReg8(RTC, SEC);

		hours = HH;
		mins = MM;
		secs = SS;

		secs&=0b01111111;

		//Function calls to toggle LEDs
		//Write your logic here
		lightHours(0);
		lightMins(0);
		// Print out the time we have stored on our RTC
		printf("The current time is: %x:%x:%x\n", hours, mins, secs);

		//using a delay to make our program "less CPU hungry"
		delay(1000); //milliseconds
	}
	return 0;
}


char* Dec2RadixN(int dec, int rad){ //define function for Radix n conversion

	int index=0; //initialize variables 
	int counter = 0; 
	int numDigits; 
	char *outstring;

	if(dec==0){ //returns the converted number as 0 if the number to be converted is 0 
		outstring=malloc(1); 
		outstring[0]='0'; 
		return outstring;

	}else{

		numDigits = ceil(log(dec)/log(rad)); //calculates the number of digits required in the converted number

		if (dec == rad||dec==1||dec==pow(rad,2)){ //increases the number of digits by one for these special cases
			numDigits++;

		}
		outstring=malloc(numDigits+1); //allocates memory for the string to be returned 
	}

	int output[numDigits]; //integer array to store the numeric values of the converted number(note that it will be in the reverse order) 
	char digits[16] = {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F'}; //array to store digits required for radixes 2-16 

	while (dec!= 0){ //loop that will repeat the process for each digit 
		output[index] = dec % rad; //stores the converted digit in the output array, in the form of the remainder of the division of the decimal number by the new radix 
		dec = dec / rad; //the decimal number is set to the integer result of the division of the decimal number by the new radix 
		index++; //the index is incremented for the next position in the array to store the next converted digit 
	}
 
	index--; 
	counter=0;
 
	for ( ;index>=0;index--){ //loop to reverse the output array while simultaneously converting it to the correct digits and storing it in a character array 
		outstring[counter]=digits[output[index]]; 
		counter++; 
	} 

	outstring[numDigits]='\0'; //sets null terminating position in the array to indicate that there are no more characters 
	return outstring; //returns the converted number as a character array 

} 



/*
 * Change the hour format to 12 hours
 */
int hFormat(int hours){
	/*formats to 12h*/
	if (hours >= 24){
		hours = 0;
	}
	else if (hours > 12){
		hours -= 12;
	}
	return (int)hours;
}

/*
 * Turns on corresponding LED's for hours
 */
void lightHours(int units){
	// Write your logic to light up the hour LEDs here


	char* binHours = Dec2RadixN(hFormat(hexCompensation(hours)), 2);
	printf("binhours output: %s",binHours);
	for(int i=strlen(binHours)-1;i>=0;i--){

		int binHoursIndex = binHours[i] - '0';

		digitalWrite (LEDS[i+(4-strlen(binHours))], binHoursIndex);
	}
}

/*
 * Turn on the Minute LEDs
 */
void lightMins(int units){
	//Write your logic to light up the minute LEDs here
	char* binMins = Dec2RadixN(mins, 2);
	for(int i=4;i<11;i++){
		digitalWrite(LEDS[i] , binMins[i]);
	}
}

/*
 * PWM on the Seconds LED
 * The LED should have 60 brightness levels
 * The LED should be "off" at 0 seconds, and fully bright at 59 seconds
 */
void secPWM(int units){
	// Write your logic here
}

/*
 * hexCompensation
 * This function may not be necessary if you use bit-shifting rather than decimal checking for writing out time values
 */
int hexCompensation(int units){
	/*Convert HEX or BCD value to DEC where 0x45 == 0d45 
	  This was created as the lighXXX functions which determine what GPIO pin to set HIGH/LOW
	  perform operations which work in base10 and not base16 (incorrect logic) 
	*/
	int unitsU = units%0x10;

	if (units >= 0x50){
		units = 50 + unitsU;
	}
	else if (units >= 0x40){
		units = 40 + unitsU;
	}
	else if (units >= 0x30){
		units = 30 + unitsU;
	}
	else if (units >= 0x20){
		units = 20 + unitsU;
	}
	else if (units >= 0x10){
		units = 10 + unitsU;
	}
	return units;
}


/*
 * decCompensation
 * This function "undoes" hexCompensation in order to write the correct base 16 value through I2C
 */
int decCompensation(int units){
	int unitsU = units%10;

	if (units >= 50){
		units = 0x50 + unitsU;
	}
	else if (units >= 40){
		units = 0x40 + unitsU;
	}
	else if (units >= 30){
		units = 0x30 + unitsU;
	}
	else if (units >= 20){
		units = 0x20 + unitsU;
	}
	else if (units >= 10){
		units = 0x10 + unitsU;
	}
	return units;
}


/*
 * hourInc
 * Fetch the hour value off the RTC, increase it by 1, and write back
 * Be sure to cater for there only being 23 hours in a day
 * Software Debouncing should be used
 */
void hourInc(void){
	//Debounce
	long interruptTime = millis();
	//Increase hours by 1, ensuring not to overflow
	if (interruptTime - lastInterruptTime>200){
		printf("Interrupt 1 triggered, %x\n", hours);
		if(hours == 0x24){
			hours = 0x00;
		}

		else if(hours==0x09){

			hours=0x10;

		}

		else if(hours==0x19){

			hours=0x20;

		}

		else{
			hours=hours+0x01;
		}
		//Write hours back to RTC

		wiringPiI2CWriteReg8(RTC, HOUR, hours);
	}
	lastInterruptTime = interruptTime;
}

/* 
 * minInc
 * Fetch the minute value off the RTC, increase it by 1, and write back
 * Be sure to cater for there only being 60 minutes in an hour
 * Software Debouncing should be used
 */
void minInc(void){
	long interruptTime = millis();

	if (interruptTime - lastInterruptTime>200){
		printf("Interrupt 2 triggered, %x\n", mins);
		//Increase minutes by 1, ensuring not to overflow
		 if(mins == 0x59){
			mins = 0x00;
		}

		else if(mins==0x49){
			mins=0x50;
		}

		else if(mins==0x39){
                        mins=0x40;
                }

		else if(mins==0x29){
                        mins=0x30;
                }

		else if(mins==0x19){
			mins=0x20;
		}
		else if(mins==0x9){
                        mins=0x10;
                }

		else{
			mins=mins+0x01;
		}
		//Write minutes back to RTC
		wiringPiI2CWriteReg8(RTC, MIN, mins);
	}
	lastInterruptTime = interruptTime;
}

//This interrupt will fetch current time from another script and write it to the clock registers
//This functions will toggle a flag that is checked in main
void toggleTime(void){
	long interruptTime = millis();

	if (interruptTime - lastInterruptTime>200){
		HH = getHours();
		MM = getMins();
		SS = getSecs();

		HH = hFormat(HH);
		HH = decCompensation(HH);
		wiringPiI2CWriteReg8(RTC, HOUR, HH);

		MM = decCompensation(MM);
		wiringPiI2CWriteReg8(RTC, MIN, MM);

		SS = decCompensation(SS);
		wiringPiI2CWriteReg8(RTC, SEC, 0b10000000+SS);
		printf("The current toggle time is: %x:%x:%x\n", HH, MM, SS);
	}
	lastInterruptTime = interruptTime;
}
