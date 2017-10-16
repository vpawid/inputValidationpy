import sqlite3 as lite
import sys
import re

currencies = {
	"USD" : "Dollar",
	"EUR" : "Euro",
	"GBP" : "Pound"
	}

def main():
	while True:
		arg = raw_input("Enter a command :")
		reg = re.compile('^maint$|^quit$|^setup$|^convert$')
		regMaint = re.compile('^maint$')
		regQuit = re.compile('^quit$')
		regSetup = re.compile('^setup$')
		regCalc = re.compile('^convert$')
		lowarg = str(arg).lower()
		isMatch = reg.match(lowarg)
		if not isMatch:
			print str(arg) + " is not a valid command"
			print "Choose from: maint quit setup convert" 
			

		else:
			check = regQuit.match(lowarg)
			if check:
				break

			check = regMaint.match(lowarg)
			if check:
				maint()
			
			check = regSetup.match(lowarg)
			if check:
				setup()

			check = regCalc.match(lowarg)
			if check:
				calc()


def maint():
	if testdb():
		return False
	print "Currencies to choose from: "
	for key in currencies:
		print key + " : " + currencies[key]

	state = "Cancelled maintenance command"
	currencyFrom = checkCurrency("Enter a currency which you want to convert from")
	if not currencyFrom:
		print state
		return False
	currencyTo = checkCurrency("Enter a currency which you want to convert to") 
	if not currencyTo:
		print state
		return False
	rate = checkNumb("Enter the rate for this conversion", 'rate')
	if not rate:
		print state
		return false

	ifExist = queryDB('SELECT * FROM conversiontbl WHERE currencyFrom = ? AND currencyTo = ?',(currencyFrom, currencyTo), 'all')
	if ifExist:
		data =(rate, currencyFrom, currencyTo)
		sql ='''UPDATE conversiontbl SET rate = ? WHERE currencyFrom = ? AND currencyTO = ?'''		
	else:
	      	data = (currencyFrom, currencyTo, rate)
		sql = '''INSERT INTO conversiontbl(currencyFrom, currencyTo, rate) 
			Values(?,?,?)'''
	try:
		queryDB(sql, data, 'all')
		print "The conversion data was saved " + currencyFrom + " to " + currencyTo + " at a rate of: " + rate
	except:
		print "Something went wrong while saving data"


def calc():
	
	if testdb():
		return False
	print "Currencies to choose from: "
	for key in currencies:
		print key + " : " + currencies[key]

	state = "Cancelled calculate command"
	currencyFrom = checkCurrency("Enter a currency which you want to convert from")
	if not currencyFrom:
		print state
		return False
	currencyTo = checkCurrency("Enter a currency which you want to convert to") 
	if not currencyTo:
		print state
		return False
	cash = checkNumb("Enter amount to convert", 'cash')
	if not cash:
		print state
		return false

	ifExist = queryDB('SELECT * FROM conversiontbl WHERE currencyFrom = ? AND currencyTo = ?',(currencyFrom, currencyTo), 'all')
	if ifExist:
		data =(currencyFrom, currencyTo)
		sql ='''SELECT rate FROM conversiontbl WHERE currencyFrom = ? AND currencyTO = ?'''		
	else:
		print "There is no conversion rate for " + currencyFrom + " to " + currencyTo + "."
		print "Please use the maint command to update the database"
	try:
		rate = queryDB(sql, data,'one')
		calculate = float(cash) * rate
		calculated = str(calculate)
		print currencyFrom + " to " + currencyTo + " at a rate of " + str(rate) + " = " + calculated
	except:
		print "Something went wrong while retrieving data from database"


def queryDB(query, data, toAll):
	toReturn = False
	conn = lite.connect('convert.db')
	c = conn.cursor()
	c.execute(query, data)
	if toAll == 'all':
		row = c.fetchall()
		if row:
			toReturn = True
	elif toAll == 'one':
		row = c.fetchone()[0]
		if row:
			toReturn = row
	conn.commit()
	conn.close()
	return toReturn


def checkCurrency(statement):
	rege = re.compile('^usd$|^eur$|^gbp$', re.IGNORECASE)
	cancelReg = re.compile('^cancel$', re.IGNORECASE)
	while True:
		currency = raw_input(statement + " or type cancel:")
		match = rege.match(str(currency).lower())
		if match:
			break
		cancelmatch = cancelReg.match(str(currency).lower())
		if cancelmatch:
			currency = False
			break
		print "Please choose from currencies above"

	return currency

def checkNumb(statement, typeOf):
	cashReg = re.compile('^\d+$|^\d+\.\d{0,2}$|^\d{1,3}\,(\d{3}\,)*\d{3}$|^\d{1,3}\,(\d{3}\,)*\d{3}\.\d{0,2}$')
	rateReg = re.compile('^\d{1,7}\.\d{1,5}$|^\d{1,3}\,(\d{3}\,){0,1}\d{3}\.\d{1,5}$')
	cancelReg = re.compile('^cancel$', re.IGNORECASE)
	numb = 0
	while True:
		numb = raw_input(statement + " or type cancel:")
		if typeOf == 'rate':
			match = rateReg.match(numb)
			if match: 
				break
			print "Please format input as X.Y where X = a number from 1-9999999 and Y=a number from 1-99999"
		elif typeOf == 'cash':
			match = cashReg.match(numb)
			if match:
				break
			print "Please format cash as a whole number or float with two decimal places"
		cancelmatch = cancelReg.match(numb)
		if cancelmatch:
			numb = False
			break
		
	return numb
	

def setup():
	conn = lite.connect('convert.db')
	c = conn.cursor()
	sql = """create table if not exists conversiontbl (id integer primary key,
                                                        currencyFrom text not null,
                                                        currencyTo text not null,
                                                        rate float not null default 0
                                                         );"""
	c.execute(sql)
	
	conn.commit()
	conn.close()
	return True


def testdb():
	try:
		conn = lite.connect('convert.db')
		c = conn.cursor()
		sql = """Select * FROM conversiontbl"""
		c.execute(sql)
		conn.close()
		return False
	except:
		conn.close()
		print "Please execute the setup command before anything else"	
		return True


if __name__ == "__main__":
	main()
