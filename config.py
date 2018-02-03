# Return iCloud username (email)
def getUsername():
    return 'connorawagner531@gmail.com'

# Return iCloud password
def getPassword():
    password = 'bdÆäÌdj`¤B'
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
    return 'Upland,IN,US'

# Return a list of pGuid's of calendars that should not be displayed
def getCalendarExceptions():
    return ['C7C9B5E0-3EB9-4549-8089-B84CAFD60B03', 'e4de89917d71f7aaa39b44ec86f1525344c98f6ff0d50fc7ba264311f2d357f5', '181b9ea99546df14b5b6e193cd4249d01043c401e2d5b82f715381c5a926323b']

# Return a curl command as a string
def getQuotaCurl():
    return "curl 'http://quota.taylor.edu/cgi-bin/graph.py?range=' -H 'Host: quota.taylor.edu' -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:56.0) Gecko/20100101 Firefox/56.0' -H 'Accept: */*' -H 'Accept-Language: en-US,en;q=0.5' --compressed -H 'Referer: http://quota.taylor.edu/?login=y' -H 'Cookie: PHPSESSID=ST-54539-e4jNnrWfEYJUzkYOVVGS-ssotayloredu; pycas=fba5adcc1516224183:connor_wagner' -H 'Connection: keep-alive' -H 'Cache-Control: max-age=0'"
