import kivy
kivy.require('1.0.6')

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.boxlayout import BoxLayout

import time
import json
import urllib.request
import operator
import subprocess
from datetime import datetime, timedelta

import schedule
from pyicloud import PyiCloudService

from config import getUsername, getPassword, getStocks, getWeatherLocale, getCalendarExceptions

class TimeWidget(RelativeLayout):

    def __init__(self, **kwargs):
        super(TimeWidget, self).__init__(**kwargs)

        # Initialize labels
        self.timeLabel = Label(text='12:34 AP', halign='center', valign='center', pos_hint={'x': 0, 'y': 0.5}, size_hint=(1, 0.5))
        self.dateLabel = Label(text='Month 12', halign='center', valign='center', pos_hint={'x': 0, 'y': 0}, size_hint=(1, 0.5))

        # Add labels to view
        self.add_widget(self.timeLabel)
        self.add_widget(self.dateLabel)

class QuoteWidget(RelativeLayout):

    def __init__(self, **kwargs):
        super(QuoteWidget, self).__init__(**kwargs)

        # Initialize label
        self.quoteLabel = Label(text='Quote here', halign='center', valign='center', pos_hint={'x': 0, 'y': 0}, size_hint=(1, 1))

        # Add label to view
        self.add_widget(self.quoteLabel)

class WeatherWidget(RelativeLayout):

    def __init__(self, **kwargs):
        super(WeatherWidget, self).__init__(**kwargs)

        # Initialize label
        self.weatherLabel = Label(text='Weather here', halign='center', valign='center', pos_hint={'x': 0, 'y': 0}, size_hint=(1, 1))

        # Add label to view
        self.add_widget(self.weatherLabel)

class StockWidget(RelativeLayout):

    def __init__(self, **kwargs):
        super(StockWidget, self).__init__(**kwargs)

        # Initialize label
        self.stockLabel = Label(text='Stocks here', halign='center', valign='center', pos_hint={'x': 0, 'y': 0}, size_hint=(1, 1))

        # Add label to view
        self.add_widget(self.stockLabel)

class DaySelector(BoxLayout):

    def __init__(self, **kwargs):
        super(DaySelector, self).__init__(**kwargs)

        # Configure DaySelector object
        self.orientation = 'horizontal'
        self.spacing = 2

        # Initialize data variables
        self.dayList = ['U', 'M', 'T', 'W', 'R', 'F', 'S']
        self.dayAdjustment = int(time.strftime("%w"))

        self.updateUI()

    def updateUI(self):
        # Remove all existing widgets
        for child in self.children:
            self.remove_widget(child)

        # Add and activate first button
        btn1 = ToggleButton(text=self.dayList[self.dayAdjustment % len(self.dayList)], group='daySelector', state='down')
        btn1.bind(on_press=self.dayChanged)
        self.add_widget(btn1)

        # Add all other buttons
        for i in range(1, len(self.dayList)):
            btn = ToggleButton(text=self.dayList[(i + self.dayAdjustment) % len(self.dayList)], group='daySelector')
            btn.bind(on_press=self.dayChanged)
            self.add_widget(btn)

    def dayChanged(self, pressedBtn):
        index = self.dayList.index(pressedBtn.text)

        # TODO: Update calendar data shown
        print(pressedBtn.text, index)

class CalendarEvent(RelativeLayout):

    def __init__(self, eventName, eventTime, eventLocation, **kwargs):
        super(CalendarEvent, self).__init__(**kwargs)

        # Initialize data variables
        self.eventName = eventName
        self.eventTime = eventTime
        self.eventLocation = eventLocation

        # Create labels
        self.nameLabel = Label(text=self.eventName, halign='center', valign='center', pos_hint={'x': 0, 'y': 0.5}, size_hint=(1, 0.5))
        self.timeLabel = Label(text=self.eventTime, halign='center', valign='center', pos_hint={'x': 0, 'y': 0}, size_hint=(0.5, 0.5))
        self.locationLabel = Label(text=self.eventLocation, halign='center', valign='center', pos_hint={'x': 0.5, 'y': 0}, size_hint=(0.5, 0.5))

        # Add labels to view
        self.add_widget(self.nameLabel)
        self.add_widget(self.timeLabel)
        self.add_widget(self.locationLabel)

class CalendarWidget(BoxLayout):

    def __init__(self, **kwargs):
        super(CalendarWidget, self).__init__(**kwargs)

        # Configure CalendarWidget object
        self.orientation = 'vertical'
        self.spacing = 5

        # Initialize data variable
        self.eventList = [CalendarEvent("Event Name 1", "12:34 AM", "Euler 201"),
                          CalendarEvent("Event Name 2", "12:34 PM", "Euler 201"),
                          CalendarEvent("Event Name 3", "12:34 AM", "Euler 201"),
                          CalendarEvent("Event Name 4", "12:34 PM", "Euler 201")]

        # Create DaySelector widget
        self.daySelector = DaySelector()

        # Add widgets to view
        self.updateUI()
        self.add_widget(self.daySelector)

    def updateEvents(self, eventList):
        # Clear event list
        self.eventList = []

        # Add new events to event list
        for event in eventList:
            self.eventList.append(event)

        self.updateUI()

    def updateUI(self):
        # Remove all existing widgets
        for child in self.children:
            self.remove_widget(child)

        # Add new widgets
        for event in self.eventList:
            self.add_widget(event)

    def showEventsForDay(self, dayNum):
        print(dayNum)

class BrightnessWidgets(BoxLayout):

    def __init__(self, **kwargs):
        super(BrightnessWidgets, self).__init__(**kwargs)

        # Configure BrightnessWidgets object
        self.orientation = 'vertical'
        self.spacing = 5

        # Create buttons
        self.darkScreenBtn = Button(text="Go Dark", halign='center', valign='center', pos_hint={'x': 0, 'y': 0}, size_hint=(1, 0.5))
        self.brightScreenBtn = Button(text="Turn It Up", halign='center', valign='center', pos_hint={'x': 0, 'y': 0.5}, size_hint=(1, 0.5))

        # Configure buttons
        self.darkScreenBtn.bind(on_press=self.darkScreen)
        self.brightScreenBtn.bind(on_press=self.brightScreen)

        # Add buttons to view
        self.add_widget(self.darkScreenBtn)
        self.add_widget(self.brightScreenBtn)

    def darkScreen(self, *args):
        self.modifyBrightness(11)

    def decrBrightness(self):
        brightness = self.getBrightness()

        # Display shuts off below 11 so we want to make sure we will not go below 11
        if brightness <= 26:
            self.modifyBrightness(11)
        else:
            self.modifyBrightness(brightness - 15)

    def incrBrightness(self):
        brightness = self.getBrightness()

        # Maximum value for brightness is 255, we want to ensure that we will not exceed it
        if brightness >= 240:
            self.modifyBrightness(255)
        else:
            self.modifyBrightness(brightness + 15)

    def brightScreen(self, *args):
        self.modifyBrightness(255)

    def getBrightness(self):
        # Open brightness file to read current value
        with open('/sys/class/backlight/rpi_backlight/brightness', 'r') as brightnessFile:
            return int(brightnessFile.read())

    def modifyBrightness(self, brightness):
        # Open brightness file to write modified brightness value to
        with open('/sys/class/backlight/rpi_backlight/brightness', 'w') as brightnessFile:
            subprocess.call(['echo',str(brightness)],stdout=brightnessFile)

class ControlWidgets(BoxLayout):

    def __init__(self, **kwargs):
        super(ControlWidgets, self).__init__(**kwargs)

        # Configure ControlWidgets object
        self.orientation = 'vertical'
        self.spacing = 10

        # Create widgets
        self.brightnessWidgets = BrightnessWidgets()
        self.exitButton = Button(text="Exit", halign='center', valign='center', pos_hint={'x': 0, 'y': 0}, size_hint=(1, 0.25))

        # Configure exit button
        self.exitButton.bind(on_press=exit)

        # Add widgets to view
        self.add_widget(self.brightnessWidgets)
        self.add_widget(self.exitButton)

class RightPane(BoxLayout):

    def __init__(self, **kwargs):
        super(RightPane, self).__init__(**kwargs)

        # Configure RightPane object
        self.orientation = 'vertical'
        self.spacing = 10

        # Create widgets
        self.controlWidgets = ControlWidgets()

        # Add widgets to view
        self.add_widget(self.controlWidgets)

class MiddlePane(BoxLayout):

    def __init__(self, **kwargs):
        super(MiddlePane, self).__init__(**kwargs)

        # Configure MiddlePane object
        self.orientation = 'vertical'
        self.spacing = 10

        # Create widget
        self.calendarWidget = CalendarWidget()

        # Add widget to view
        self.add_widget(self.calendarWidget)

class LeftPane(BoxLayout):
    def __init__(self, **kwargs):
        super(LeftPane, self).__init__(**kwargs)

        # Configure LeftPane object
        self.orientation = 'vertical'
        self.spacing = 10

        # Create widgets
        self.timeWidget = TimeWidget()
        self.quoteWidget = QuoteWidget()
        self.weatherWidget = WeatherWidget()
        self.stockWidget = StockWidget()

        # Add widgets to view
        self.add_widget(self.timeWidget)
        self.add_widget(self.quoteWidget)
        self.add_widget(self.weatherWidget)
        self.add_widget(self.stockWidget)

class RootLayout(RelativeLayout):

    def __init__(self, **kwargs):
        super(RootLayout, self).__init__(**kwargs)

        # Configure display panes
        self.leftPane = LeftPane(pos_hint={'x': 0, 'y': 0}, size_hint=(0.25, 1))
        self.middlePane = MiddlePane(pos_hint={'x': 0.25, 'y': 0}, size_hint=(0.6, 1))
        self.rightPane = RightPane(pos_hint={'x': 0.85, 'y': 0}, size_hint=(0.15, 1))

        # Add panes to view
        self.add_widget(self.leftPane)
        self.add_widget(self.middlePane)
        self.add_widget(self.rightPane)

class PiDay(App):

    def __init__(self, **kwargs):
        super(PiDay, self).__init__(**kwargs)

        # Log in to iCloud API session and set up calendar control sessions
        self.icloudApi = PyiCloudService(getUsername(), getPassword())

        # Initialize presentation manager
        self.rootLayout = RootLayout()

        # Start timer to update widgets at midnight
        now = datetime.now()
        tomorrow = datetime(now.year, now.month, now.day) + timedelta(1)
        timeUntilMidnight = abs(tomorrow - now).seconds * 1000 + 1000

        # TODO: ####################
        # Create midnight timer call

    def build(self):
        return self.rootLayout

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
        pass

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
        #  another item in that dictionary is 'main', that is a dictionary containing the weather statistics

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
            # If there is no location then remove the end of the string (… at …)
            if event['location'] == None:
                detailStr = detailStr[:-8]

            # TODO: ############
            # Update Calendar UI

        # If there are no events on this day then display a message instead of leaving the space blank
        if len(eventsOnSelectedDay) == 0:
            # TODO: ############
            # Update Calendar UI
            pass

        # Get screen control widget at bottom of pane since we destroyed it at the top of this function
        self.getScreenControlWidget()

    def getScreenControlWidget(self):
        # TODO: #########################
        # Create screen control widget UI
        pass

    def getDaySelectionWidget(self):
        # TODO: #################
        # Create day selection UI
        pass

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

    # Make an HTTP request and return the decoded string
    def makeHTTPRequest(self, url):
        r = urllib.request.urlopen(url)
        response = r.read().decode('utf-8')
        r.close()
        return response

# Start the program
if __name__ == "__main__":
    PiDay().run()

# Blue color: #45A9F5
# Background grey/black color: #302F37
# Dark background color: #242329
