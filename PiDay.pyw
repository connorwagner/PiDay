import time
import json
import urllib.request
import operator
import subprocess
from datetime import datetime, timedelta

import schedule
from pyicloud import PyiCloudService

from config import getUsername, getPassword, getStocks, getWeatherLocale, getCalendarExceptions

class PiDay():
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

        # Log in to iCloud API session and set up calendar control sessions
        self.icloudApi = PyiCloudService(getUsername(), getPassword())
        self.days = ['U','M','T','W','R','F','S']
        self.dayAdjustment = int(time.strftime("%w"))
        self.selectedDay = tk.IntVar()

        # TODO: #########################
        # Initialize presentation manager

        # Create widgets
        self.getTimeWidget()
        self.getQuoteWidget()
        self.getWeatherWidget()
        self.getStocksWidget()
        self.getCalendarData()
        self.getDaySelectionWidget()

        # Start timer to update widgets at midnight
        now = datetime.now()
        tomorrow = datetime(now.year, now.month, now.day) + timedelta(1)
        timeUntilMidnight = abs(tomorrow - now).seconds * 1000 + 1000
        self.midnightRecursiveCall = self.after(timeUntilMidnight, self.updateWidgetsAtMidnight)

    def getTimeWidget(self):
        # TODO: ###############
        # Create time widget UI

        # Update data on widget
        self.updateTimeWidget()

    def updateTimeWidget(self):
        # TODO: ############################################################
        # Update text on both time and date widgets to reflect new time/date

        # TODO: ################################
        # Start timer to update data in 1 second

    def getQuoteWidget(self):
        # TODO: ################
        # Create quote widget UI

        # Update widget to display joke
        self.updateQuoteWidget()

    def updateQuoteWidget(self):
        # Get new quote from API and change label text to reflect it
        # Possibly change to http://tambal.azurewebsites.net/joke/random
        joke = self.makeHTTPRequest("http://ron-swanson-quotes.herokuapp.com/v2/quotes")
        joke = joke[1:-1] + "\n–Ron Swanson"

        # TODO: ############
        # Update quote label

    def getWeatherWidget(self):
        # TODO: ###########
        # Create Weather UI

        # Update data on widget
        self.updateWeatherWidget()

    def updateWeatherWidget(self):
        # API key: 533616ff356c7a5963e935e12fbb9306
        # Lat / long: 40.4644155 / -85.5111644
        # City ID for Upland: 4927510
        # City Query for Upland: Upland,IN,US
        # Sample URL: http://api.openweathermap.org/data/2.5/forecast?id=4927510&appid=533616ff356c7a5963e935e12fbb9306&units=imperial
        # JSON Structure: dictionary object 'list' is a list of dictionaries, each index increments by 3 hours
        #  one item in that dictionary is 'weather', that is a dictionary containing the weather conditions
        #  another itme in that dictionary is 'main', that is a dictionary containing the weather statistics

        # Get forecast data and convert to dictionary from JSON
        forecastJsonStr = self.makeHTTPRequest("http://api.openweathermap.org/data/2.5/forecast?q=%s&appid=533616ff356c7a5963e935e12fbb9306&units=imperial" % getWeatherLocale())
        forecastJsonDict = json.loads(forecastJsonStr)

        # Get current weather data and convert to dictionary from JSON
        currentJsonStr = self.makeHTTPRequest("http://api.openweathermap.org/data/2.5/weather?q=%s&appid=533616ff356c7a5963e935e12fbb9306&units=imperial" % getWeatherLocale())
        currentJsonDict = json.loads(currentJsonStr)

        # Get city name from dictionary
        city = currentJsonDict['name']

        # Get current weather data
        currentTemp = "%i°F" % int(round(currentJsonDict['main']['temp']))
        currentCond = currentJsonDict['weather'][0]['main']

        # Loop through all future weather conditions supplied to determine high and low temperatures for the day
        currentDateString = time.strftime("%Y-%m-%d")
        highTempsList = list()
        lowTempsList = list()
        weatherList = forecastJsonDict['list']
        for i in range(len(weatherList)):
            weatherDict = weatherList[i]
            tempsDict = weatherDict['main']
            if i == 0 and weatherDict['dt_txt'][:10] != currentDateString:
                currentDateString = weatherDict['dt_txt'][:10]
            if weatherDict['dt_txt'][:10] == currentDateString:
                lowTempsList.append(tempsDict['temp_min'])
                highTempsList.append(tempsDict['temp_max'])          
        highTemp = str(round(max(highTempsList))) + "°F"
        lowTemp = str(round(min(lowTempsList))) + "°F"

        # Create string to display data and set label to show new string
        weatherText = "Weather for " + city + "\n" + currentTemp + " and " + currentCond + "\nHigh: " + highTemp + "\nLow: " + lowTemp

        # TODO: ###########
        # Update weather UI
        self.weatherLabel.configure(text=weatherText)

        # TODO: #######################################
        # Start 30 minute timer to update weather again

    def getStocksWidget(self):
        # TODO: #################
        # Create stocks widget UI

        # Update data on widget
        self.updateStocksWidget()

    def updateStocksWidget(self):
        # Get list of stocks desired from config file
        stocksListOfLists = getStocks()
        pricesStr = str()
        for stockList in stocksListOfLists:
            # Get price for desired stock and add it to the string for the label
            price = self.makeHTTPRequest('http://finance.yahoo.com/d/quotes.csv?s=' + stockList[0] + '&f=l1')
            pricesStr += "%s: $%.2f\n" % (stockList[0], float(price))
        # Remove trailing newline character
        pricesStr = pricesStr[:-1]

        # TODO: ##########
        # Update stocks UI

        # TODO: ###############################
        # Start timer to update after 5 minutes

    def getCalendarData(self):        
        now = datetime.now()
        # Get list of exceptions from config
        exceptions = getCalendarExceptions()
        # Try to get calendar data, if an error is thrown then reauthenticate and try again
        events = None
        try:
            events = self.icloudApi.calendar.events(now, now + timedelta(days=6))
        except:
            self.icloudApi = PyiCloudService(getUsername(), getPassword())
            events = self.icloudApi.calendar.events(now, now + timedelta(days=6))
        # Separate events into a list of lists separated by day
        dateFormat = "%Y%m%d"
        today = time.strftime(dateFormat)
        self.daySeparatedEventList = [list(),list(),list(),list(),list(),list(),list()]
        for event in events:
            # Ensure that the event is not on a calendar that the user does not wish to see
            if event['pGuid'] not in exceptions:
                daysDiff = (datetime.strptime(str(event['localStartDate'][0]), dateFormat) - datetime.strptime(today, dateFormat)).days
                # Try statement needed because the API hands back a list of the next 7 days with events so if the current day has no events then it will hand back too many days and the number of days' difference will be 7, exceeding the length of our list
                try:
                    self.daySeparatedEventList[daysDiff].append(event)
                except:
                    pass
        # Sort each list of events by start time
        for listOfEvents in self.daySeparatedEventList:
            listOfEvents.sort(key=operator.itemgetter('localStartDate'))

        # Update widget to reflect new data
        self.getCalendarWidget()

        # TODO: ##############################
        # Set timer to update after 30 minutes

    def getCalendarWidget(self):
        # Loop through all events on the selected day and add them to the widget as individual labels so they are spaced nicely by the presentation manager
        eventsOnSelectedDay = self.daySeparatedEventList[self.selectedDay.get()]
        for event in eventsOnSelectedDay:
            # Sanitize edge cases
            startHour = event['localStartDate'][4]
            startHourAmPm = "AM"
            if startHour >= 12:
                startHour -= 12
                startHourAmPm = "PM"
            if startHour == 0:
                startHour = 12
            endHour = event['localEndDate'][4]
            endHourAmPm = "AM"
            if endHour >= 12:
                endHour -= 12
                endHourAmPm = "PM"
            if endHour == 0:
                endHour = 12
            # Create string to display
            detailStr = "%s: %i:%02i %s to %i:%02i %s at %s" % (event['title'], startHour, event['localStartDate'][5], startHourAmPm, endHour, event['localEndDate'][5], endHourAmPm, event['location'])
            # If there is no location then remove the end of the string ("… at …")
            if event['location'] == None:
                detailStr = detailStr[:-8]

            # TODO: ############
            # Update Calendar UI

        # If there are no events on this day then display a message instead of leaving the space blank
        if len(eventsOnSelectedDay) == 0:
            # TODO: ############
            # Update Calendar UI

        # Get screen control widget at bottom of pane since we destroyed it at the top of this function
        self.getScreenControlWidget()

    def getScreenControlWidget(self):
        # TODO: #########################
        # Create screen control widget UI
        pass

    def getDaySelectionWidget(self):
        # TODO: #################
        # Create day selection UI

    def updateWidgetsAtMidnight(self):
        # Update day ajuster and adjust day selection back one if necessary to maintain selected calendar day upon day change
        self.dayAdjustment = int(time.strftime("%w"))
        if self.selectedDay.get() > 0:
            self.selectedDay.set(self.selectedDay.get() - 1)

        # Update quote and day selection widgets
        self.updateQuoteWidget()
        self.getDaySelectionWidget()

        # TODO: ########################################################################################################
        # Cancel the recursive call that already existed to avoid duplicate calls and then call it again (for all below)

    def showStocksDetails(self):
        # Generate string to display on info popup
        stocksListOfLists = getStocks()
        stocksStr = str()
        for stockList in stocksListOfLists:
            stocksStr += stockList[0] + ": " + str(stockList[2]) + " owned, bought at $" + str(stockList[1]) + "\n"
        stocksStr = stocksStr[:-1]

        # TODO: ##########
        # Update Stocks UI

        # Cancel the existing recursive call if it exists to avoid duplicate calls
        try:
            self.after_cancel(self.stocksUpdateRecursiveCall)
        except:
            pass

        # TODO: ##############################################################        
        # Set a timer to restore normal text on stock button after 7.5 seconds

    def dayChanged(self):
        # Update calendar display to show new data
        self.getCalendarWidget()

    def darkScreen(self):
        self.modifyBrightness(11)

    def decrBrightness(self):
        brightness = self.getBrightness()
        if brightness <= 26:
            self.modifyBrightness(11)
        else:
            self.modifyBrightness(brightness - 15)

    def incrBrightness(self):
        brightness = self.getBrightness()
        if brightness >= 240:
            self.modifyBrightness(255)
        else:
            self.modifyBrightness(brightness + 15)

    def brightScreen(self):
        self.modifyBrightness(255)

    def getBrightness(self):
        with open('/sys/class/backlight/rpi_backlight/brightness', 'r') as brightnessFile:
            return int(brightnessFile.read())

    def modifyBrightness(self, brightness):
        # Open brightness file to write modified brightness value to
        with open('/sys/class/backlight/rpi_backlight/brightness', 'w') as brightnessFile:
            subprocess.call(['echo',str(brightness)],stdout=brightnessFile)

    # Make an HTTP request and return the decoded string
    def makeHTTPRequest(self, url):
        r = urllib.request.urlopen(url)
        response = r.read().decode('utf-8')
        r.close()
        return response

# Start the program
if __name__ == "__main__":
    # TODO: ###################
    # Launch the application UI

# Blue color: #45A9F5
# Background grey/black color: #302F37
# Dark background color: #242329
