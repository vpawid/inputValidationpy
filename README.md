# inputValidationpy
ICS 355

The repository contains the inputValidationpy which calculates conversions of currencies. It also stores exchange rates in a sqlite3 database. This data can be modified by a maint command. To convert currencies using the exchange rates recorded in the database use the convert command. Each input is matched against a regular expression to validate. If the prompt is given bad input it will continue to ask for valid input until given so. 

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.


### Prerequisites

First make a pull request from github or the command line to make a local copy of this repo. 


Then install python:

>For windows users [click here](http://docs.python-guide.org/en/latest/starting/install/win/).

>For mac [click here](http://docs.python-guide.org/en/latest/starting/install/osx/).


### Running

Through the terminal or command prompt, locate to the repo directory with the convert.py file. 

Run the program by simply typing: **python convert.py** You should be prompted:
```
Enter a command :
```
There are currently four commands to choose from: 

#### 1. maint

The maintence command is for reading in conversion data to the database to be used to calculate currency exchange. If the database is not initialized it will prompt the user to set it up with the setup command. Once the maint command is passed it will show which currencies are currently avaliable and then continue to ask for other information. The currencies must be input in their three letter symbols:
>usd eur gbp
Then input the exchange rate, which must be a float and be a maximum of 7 digits big left of the decimal and a maximum of 5 digits big right of the decimal. 
```
Enter a command :maint
Currencies to choose from:
USD : Dollar
GBP : Pound
EUR : Euro
Enter a currency which you want to convert from or type cancel:usd
Enter a currency which you want to convert to or type cancel:eur
Enter the rate for this conversion or type cancel:0.85
The conversion data was saved usd to eur at a rate of: 0.85
```
#### 2. quit

The program will save the data and exit.

#### 3. setup

Initializes the sqlite3 database and table in a file **convert.db** which is located in the same directory as the program.

#### 4. convert

Similar to the maint command this command prompts the user for currencies. The amount to convert should also be a float, its format should be at the maximum seven digits left of the decimal and two digits to the right of it.

```
Enter a command :convert
Currencies to choose from:
USD : Dollar
GBP : Pound
EUR : Euro
Enter a currency which you want to convert from or type cancel:usd
Enter a currency which you want to convert to or type cancel:eur
Enter amount to convert or type cancel:1200.00
usd to eur at a rate of 0.85 = 1020.0
```

## Author

* **Victor Pawid** 
