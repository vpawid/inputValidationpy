import sqlite3 as lite
import sys
import re
import hashlib
import os

currencies = {
	"USD" : "Dollar",
	"EUR" : "Euro",
	"GBP" : "Pound"
	}

currentUser = False
loggedIn = False

#main function for the interface
def main():
	while True:
		arg = raw_input("login, admin, quit : ")
		reg = re.compile('^login$|^admin$|^quit$')
		regLogin = re.compile('^login$')
		regAdmin = re.compile('^admin$')
		regQuit = re.compile('^quit$')
		isMatch = reg.match(str(arg).lower())
		if not isMatch:
			print str(arg) + " is not a valid commant"	
			print "Choose from: login, admin, quit"
		else:
			check = regLogin.match(str(arg).lower())
			if check:
				login()
				
			check = regAdmin.match(str(arg).lower())
			if check:
				admin()
				
			check = regQuit.match(str(arg).lower())
			if check:
				break
		
		#commands for user level access
		if loggedIn and currentUser:
			while True:
				arg = raw_input("Enter a command :")
				reg2 = re.compile('^transfer$|^quit$')
				isMatch = reg2.match(str(arg).lower())
				regTran = re.compile('^transfer$')
				if not isMatch:
					print str(arg) + " is not a valid command"
					print "Choose from: transfer quit"
				else:
					check = regQuit.match(str(arg).lower())
					if check:
						break	
					
					check = regTran.match(str(arg).lower())
					if check:
						trans()
		#commands only for admin level access		
		if loggedIn and not currentUser:			
			while True:
				arg = raw_input("Enter a command :")
				reg3 = re.compile('^maint$|^quit$|^setup$|^convert$|^adduser$|^deleteuser$|^add$|^sub$')
				regMaint = re.compile('^maint$')
				regSetup = re.compile('^setup$')
				regCalc = re.compile('^convert$')
				regAddUser = re.compile('^adduser$')
				regDel = re.compile('^deleteuser$')
				regAddMoney = re.compile('^add$')
				regSub = re.compile('^sub$')
				lowarg = str(arg).lower()
				isMatch = reg3.match(lowarg)
				if not isMatch:
					print str(arg) + " is not a valid command"
					print "Choose from: maint quit setup convert login adduser deleteuser add sub" 
				

				else:
					check = regQuit.match(lowarg)
					if check:
						break

					check = regAddUser.match(lowarg)
					if check:
						addUser()

					check = regDel.match(lowarg)	
					if check:
						delUser()
					
					check = regAddMoney.match(lowarg)
					if check:
						editFunds('add',False)
					
					check = regSub.match(lowarg)
					if check:
						editFunds('sub',False)

					check = regMaint.match(lowarg)
					if check:
						maint()
					
					check = regSetup.match(lowarg)
					if check:
						setup()

					check = regCalc.match(lowarg)
					if check:
						calc(False,False,False)


#checks password and user
#uses global variable to change state of program
def login():
	user = raw_input("username :")
	ps = raw_input("pasword : ")
	while not checkUser(user) or not checkPs(ps, user):
		print "username or password is invalid please try again"
		user = raw_input("username :")
		ps = raw_input("password :")
	print "welcome " + user
	global currentUser
	currentUser = user
	global loggedIn
	loggedIn = True
	return

#check password 
#creates a new admin if there doesnt exist one
#uses global variabes to change state of program
def admin():
	#if there is no admin account give option to make one
	isDbEmpty = queryDB('SELECT * FROM usertbl WHERE username = ?',('admin',),'all') 
	if not isDbEmpty:
		print "No current admin account please create one"
		ps = raw_input("new password :")
		salt = os.urandom(32)
		hashword = createHash(ps,salt)
		sql = '''INSERT INTO usertbl (username, salt, balance, currencypref, ps) Values(?,?,?,?,?)'''
		data = ('admin',salt,0,'usd',hashword)
		created = queryDB(sql,data,'all')
		if created:
			print "account created"
	ps = raw_input("password :")
	if checkPs(ps,'admin'):
		global currentUser
		currentUser = False
		global loggedIn
		loggedIn = True
		print "Welcome Admin"

	
#remove user from usertbl
def delUser():
	user = autoCheckUser("Which user to delete : ","Invalid user please enter a valid username",False)
	if user:
		queryDB('DELETE FROM usertbl WHERE username = ?',(user,),'all')	
		print "Deleted " + user
	return

#add user to usertbl
def addUser():
	#check to see if the user exists
	print" wtf"
	user = autoCheckUser("username : ","User already exist please enter another username",True)
	if not user:
		return
	salt = os.urandom(32)
	ps = raw_input("password : ")
	hashword = createHash(ps,salt)
	balance = raw_input(user + "\'s current balance : ")
	for key in currencies:
		print key + " : " + currencies[key]
	currency = checkCurrency("in which currency")
	# login was cancelled at currency preference phase
	if not currency:
		return
	sql = '''INSERT INTO usertbl (username, salt, balance, currencypref, ps) Values(?,?,?,?,?)'''
	data = (user,salt, balance, currency, hashword)
	queryDB(sql,data,'all')
	return

#promtp : first message to ask for an input
#errorMsg : looping message if the input given is invalid
#autoCheckUser queries the database to find if a user is present in the database
def autoCheckUser(prompt, errorMsg,shouldNotExist):
	user = raw_input(prompt)
	reg = re.compile('^cancel$')
	if shouldNotExist:
		while queryDB('SELECT * FROM usertbl WHERE username = ?',(user,),'all'):
			user = raw_input(errorMsg + " or type cancel : ")
			user = str(user).lower()
			if reg.match(user):
				print "Cancelled"
				return False
	else:
		while not queryDB('SELECT * FROM usertbl WHERE username = ?',(user,),'all'):
			user = raw_input(errorMsg + " or type cancel : ")
			user = str(user).lower()
			if reg.match(user):
				print "Cancelled"
				return False	
	return user

#see if user already exist in the database
def checkUser(user):
	return queryDB('SELECT * FROM usertbl WHERE username = ?', (user,),'all')

#generate hash from given parameter with salt from database of user
def checkPs(ps, user):
	unisalt = queryDB('SELECT salt FROM usertbl WHERE username = ?',(user,),'one')
	correctHash = queryDB('SELECT ps FROM usertbl WHERE username = ?',(user,),'one')
	toAuthHash = createHash(ps,unisalt)
	if toAuthHash == correctHash :
		return True
	return False

#transfers money between user accounts
#calls the editFunds() to calculate and edit data
def trans():
	reg = re.compile('^into$|^out$')

	addOrSub = raw_input("Did you want to move funds \'into\' your account from another  or \'out\' of your account to another : ")
	isMatch = reg.match(str(addOrSub).lower())
	if not isMatch:
		addOrSub = raw_input("Choose to transfer: \'into\' or \'out\' ")
	if addOrSub == 'out':
		editFunds('add',True)			
	if addOrSub == 'into':
		editFunds('sub',True)

#add and subtract functions
def editFunds(addOrSub, transfer):
	global currentUser
	user = autoCheckUser("Which user were you thinking of : ","Invalid user please enter another username", False)	
	if not user:
		return False
	amount = checkNumb("How much money are we talking", 'cash')
		
	currencyFrom = checkCurrency("Which currency should this amount be in")
	if not currencyFrom:
		return False
	
	currencyTo = queryDB('SELECT currencypref FROM usertbl WHERE username = ?',(user,),'one')
	# convert if needed
	if (currencyFrom != currencyTo):
		amountToCalc = calc(currencyFrom, currencyTo, amount)
		
	else:
		amountToCalc = amount
	balance = queryDB('SELECT balance FROM usertbl WHERE username = ?', (user,),'one')
	if addOrSub == 'add':
		if transfer:
			currentUserBalance = queryDB('SELECT balance FROM usertbl WHERE username = ?', (currentUser,),'one')
			while float(amount) >= float(currentUserBalance):
				amount = checkNumb(str(amount) + " is more than you have, please enter an amount less than " + str(currentUserBalance), 'cash')
			currentUserCurrency = queryDB('SELECT currencyPref FROM usertbl WHERE username = ?', (currentUser,), 'one')
			if currentUserCurrency != currencyFrom:
				amount = calc(currencyFrom, currentUserCurrency, amount)
			currentUserNewBalance = (float(currentUserBalance) - float(amount))
			print currentUserNewBalance
			holder = queryDB('UPDATE usertbl SET balance = ? WHERE username = ?', (currentUserNewBalance, currentUser,),'all')
		newBalance = float(amountToCalc) + balance
	else:
		if transfer:
			currentUserCurrency = queryDB('SELECT currencyPref FROM usertbl WHERE username = ?', (currentUser,),'one')
			currentUserBalance = queryDB('SELECT balance FROM usertbl WHERE username = ?', (currentUser,),'one')
			if currentUserCurrency != currencyTo:
				amount = calc(currencyUserCurrency, currencyTo, amount)
			currentUserNewBalance = (float(currentUserBalance) + float(amount))
			holder = queryDB('UPDATE usertbl SET balance = ? WHERE username = ?',(currentUserNewBalance, currentUser,),'all')
		while float(amountToCalc) >= float(balance):
			amountToCalc = checkNumb("Amount given to subtract is more than the current balance of",'cash')
			if (currencyFrom != currencyTo):
				amountToCalc = calc(currencyFrom, currencyTo,(checkNumb("Amount given to subtract is more than the current balance of",'cash')))
		newBalance = balance - float(amountToCalc)
		
		
	addedToDB = queryDB('UPDATE usertbl SET balance = ? WHERE username = ? ',(newBalance, user),'all')
	print user + "'s new balance is : " + str(newBalance)
		
	return	
		

def maint():
	if testdb():
		return False

	currencyFrom = checkCurrency("Enter a currency which you want to convert from")
	if not currencyFrom:
		return False
	currencyTo = checkCurrency("Enter a currency which you want to convert to") 
	if not currencyTo:
		return False
	rate = checkNumb("Enter the rate for this conversion", 'rate')
	if not rate:
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


def calc(cfrom, cto, amount):
	
	if testdb():
		return False
	if not cfrom:
		currencyFrom = checkCurrency("Enter a currency which you want to convert from")
		if not currencyFrom:
			return False
	else:
		currencyFrom = cfrom
	
	if not cto:
		currencyTo = checkCurrency("Enter a currency which you want to convert to") 
		if not currencyTo:
			return False
	else:
		currencyTo = cto
	
	if not amount:
		cash = checkNumb("Enter amount to convert", 'cash')
		if not cash:
			return false
	else:
		cash = amount

	ifExist = queryDB('SELECT * FROM conversiontbl WHERE currencyFrom = ? AND currencyTo = ?',(currencyFrom, currencyTo), 'all')
	if ifExist:
		data =(currencyFrom, currencyTo)
		sql ='''SELECT rate FROM conversiontbl WHERE currencyFrom = ? AND currencyTO = ?'''		
		try:
			rate = queryDB(sql, data,'one')
			calculate = float(cash) * rate
			calculated = str(calculate)
			print str(cash) + " " +currencyFrom + " to " + currencyTo + " at a rate of " + str(rate) + " = " + calculated
			return calculated
		except:
			print "Something went wrong while retrieving data from database"
	else:
		print "There is no conversion rate from " + currencyFrom + " to " + currencyTo + "."
		print "Please use the maint command to update the database"

def queryDB(query, data, toAll):
	toReturn = False
	conn = lite.connect('convert.db')
	#conn.text_factory = lambda x: unicode(x,'utf-8', 'ignore')
	conn.text_factory = bytes
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
	print "Currencies to choose from :"
	for key in currencies:
		print currencies[key] + "= " + key	
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
			print "Cancelled"
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
			print "Cancelled"
			numb = False
			break
		
	return numb
	

def setup():
	conn = lite.connect('convert.db')
	c = conn.cursor()
	#query to create the table to hold the conversion rates
	sql = """create table if not exists conversiontbl (id integer primary key,
                                                        currencyFrom text not null,
                                                        currencyTo text not null,
                                                        rate float not null default 0
                                                         );"""
	c.execute(sql)
	#query to create the username table with balance information
	sql2 = """create table if not exists usertbl (username text not null,
							salt text not null,
							balance float not null default 0,
							currencypref text not null,
							ps text not null);"""
	c.execute(sql2)
	conn.commit()
	conn.close()
	return True


def testdb():
	try:
		conn = lite.connect('convert.db')
		conn.text_factory = bytes
		c = conn.cursor()
		sql = """Select * FROM conversiontbl"""
		sql1 = """Select * FROM usertbl"""
		c.execute(sql)
		c.execute(sql1)
		conn.close()
		return False
	except:
		conn.close()
		print "Please execute the setup command before anything else"	
		return True


#creates a hash given a ps string and a salt as a parameter out put hash
def createHash(pString, salt):
	toBeHashed = pString + salt
	hashword = hashlib.sha256(toBeHashed).hexdigest()
	return hashword
	


if __name__ == "__main__":
	main()
