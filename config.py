# Return iCloud username (email)
def getUsername():
    return ''

# Return iCloud password
def getPassword():
    password = ''
    for i in range(len(password)):
        ch = ord(password[i]) // 2
        password = password[:i] + chr(ch) + password[i+1:]
    ret = ''
    for ch in password:
        ret += ch
    return ret

# Helper function so that your possward isn't simply stored as plaintext
# call this and paste the result into the password field above
def encryptPassword(password):
    for i in range(len(password)):
        ch = ord(password[i]) * 2
        password = password[:i] + chr(ch) + password[i+1:]
    ret = ''
    for ch in password:
        ret += ch
    return ret

# Use this function call with your actual password, run the config file (`python3 config.py`), copy the output, then delete the function call
print(encryptPassword('yourPassword!'))

# Return list of lists, each list containing the symbol for a stock, what price it was bought at, and how many are owned
def getStocks():
    return [['AAPL', 0, 0],
            ['GOOGL', 0, 0],
            ['NVDA', 0, 0]]

# Return weather locale string, in the format City,ST,[CN]
def getWeatherLocale():
    return ''

# Return a list of pGuid's of calendars that should not be displayed
def getCalendarExceptions():
    return ['']

# Return a curl command as a string
def getQuotaCurl():
    return ""
