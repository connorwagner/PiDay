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

# Return list of lists, each list containing the symbol for a stock, what price it was bought at, and how many are owned
def getStocks():
    return [['AAPL', 0, 0],
            ['GOOGL', 0, 0],
            ['NVDA', 0, 0]]

# Return weather locale string, in the format City,ST,CN
def getWeatherLocale():
    return 'Upland,IN'

# Return a list of pGuid's of calendars that should not be displayed
def getCalendarExceptions():
    return ['C7C9B5E0-3EB9-4549-8089-B84CAFD60B03']

# Return a curl command as a string
def getQuotaCurl():
    return "curl 'http://quota.taylor.edu/cgi-bin/graph.py?range=' -H 'Host: quota.taylor.edu' -H 'User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:51.0) Gecko/20100101 Firefox/51.0' -H 'Accept: */*' -H 'Accept-Language: en-US,en;q=0.5' --compressed -H 'Referer: http://quota.taylor.edu/?login=y' -H 'Cookie: visid_incap_321279=A6FcWS3AS16yv2G4U+cPjq4qklgAAAAAQUIPAAAAAABSOGLKYVCByrmhuuGgvz2K; __utma=43697952.1078009590.1494436041.1494436041.1494436041.1; __utmz=43697952.1494436041.1.1.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); PHPSESSID=ST-52609-ZmUT9IMIGJ2eUd9FEUMO-ssotayloredu; pycas=5ce720a01494617705:connor_wagner' -H 'Connection: keep-alive'"
