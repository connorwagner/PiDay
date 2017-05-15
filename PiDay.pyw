import kivy
kivy.require('1.0.6')

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.boxlayout import BoxLayout

import time
import json
import urllib.request
import subprocess
from datetime import datetime, timedelta

import operator
from pyicloud import PyiCloudService

from config import getUsername, getPassword, getStocks, getWeatherLocale, getCalendarExceptions

class TimeWidget(RelativeLayout):

    def __init__(self, **kwargs):
        super(TimeWidget, self).__init__(**kwargs)

        # Initialize labels
        self.timeLabel = Label(text='12:34 AP', font_size='42', halign='center', valign='center', pos_hint={'x': 0, 'y': 0.25}, size_hint=(1, 0.8))
        self.dateLabel = Label(text='Month 12', font_size='20', halign='center', valign='center', pos_hint={'x': 0, 'y': 0.2}, size_hint=(1, 0.2))

        # Update clock every 0.1 second
        Clock.schedule_interval(self.updateTime, 0.1)

        # Add labels to view
        self.add_widget(self.timeLabel)
        self.add_widget(self.dateLabel)

    def updateTime(self, *largs):
        self.timeLabel.text = time.strftime("%-I:%M %p")
        self.dateLabel.text = time.strftime("%B %-d")

class QuoteWidget(BoxLayout):

    def __init__(self, **kwargs):
        super(QuoteWidget, self).__init__(**kwargs)

        # Initialize label
        self.quoteLabel = Label(text='Quote here', halign='center', valign='center', max_lines=8)

        # Add label to view
        self.add_widget(self.quoteLabel)

        # Configure label to adjust height to fit text (can only be done after label has been added to a view)
        self.quoteLabel.size = (self.quoteLabel.parent.width * 1.85, self.quoteLabel.texture_size[1])
        self.quoteLabel.text_size = (self.quoteLabel.width, None)
        self.quoteLabel.size_hint = (1, None)

        self.updateUI()

        # Set timer to update quote at midnight
        Clock.schedule_once(self.updateUIFirstTime, getTimeToMidnight())

    def updateUIFirstTime(self, *largs):
        # Update quote every 24 hours (24 hours * 60 minutes * 60 seconds = 86400 seconds)
        Clock.schedule_interval(self.updateUI, 86400)
        self.updateUI()

    def updateUI(self, *largs):
        # Get quote from API call
        quote = makeHTTPRequest("http://ron-swanson-quotes.herokuapp.com/v2/quotes")
        quote = quote[1:-1] + "\n–Ron Swanson"

        # Update text on label
        self.quoteLabel.text = quote

        # Update label position
        self.quoteLabel.pos_hint = {'x': 0, 'y': self.quoteLabel.height + .5}
        self.size = (self.quoteLabel.width, self.quoteLabel.height)

class WeatherWidget(RelativeLayout):

    def __init__(self, **kwargs):
        super(WeatherWidget, self).__init__(**kwargs)

        # Initialize data variables
        self.weatherString = ""

        # Initialize label
        self.weatherLabel = Label(text='Weather here', halign='center', valign='center', pos_hint={'x': 0, 'y': 0}, size_hint=(1, 1))

        # Update weather every 15 minutes (15 minutes * 60 seconds = 900 seconds)
        Clock.schedule_interval(self.updateWeather, 900)

        self.updateWeather()

        # Add label to view
        self.add_widget(self.weatherLabel)

    def updateWeather(self, *largs):
        # API key: 533616ff356c7a5963e935e12fbb9306
        # Lat / long: 40.4644155 / -85.5111644
        # City ID for Upland: 4927510
        # City Query for Upland: Upland,IN,US
        # Sample URL: http://api.openweathermap.org/data/2.5/forecast?id=4927510&appid=533616ff356c7a5963e935e12fbb9306&units=imperial
        # JSON Structure: dictionary object 'list' is a list of dictionaries, each index increments by 3 hours
        #  one item in that dictionary is 'weather', that is a dictionary containing the weather conditions
        #  another item in that dictionary is 'main', that is a dictionary containing the weather statistics

        # Get forecast data and convert to dictionary from JSON
        forecastJsonStr = makeHTTPRequest("http://api.openweathermap.org/data/2.5/forecast?q=%s&appid=533616ff356c7a5963e935e12fbb9306&units=imperial" % getWeatherLocale())
        forecastJsonDict = json.loads(forecastJsonStr)

        # Get current weather data and convert to dictionary from JSON
        currentJsonStr = makeHTTPRequest("http://api.openweathermap.org/data/2.5/weather?q=%s&appid=533616ff356c7a5963e935e12fbb9306&units=imperial" % getWeatherLocale())
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
        self.weatherString = "Weather for " + city + "\n" + currentTemp + " and " + currentCond + "\nHigh: " + highTemp + "\nLow: " + lowTemp

        self.updateUI()

    def updateUI(self):
        self.weatherLabel.text = self.weatherString

class StockWidget(RelativeLayout):

    def __init__(self, **kwargs):
        super(StockWidget, self).__init__(**kwargs)

        # Initialize data variables
        self.stockString = ""

        # Initialize label
        self.stockLabel = Label(text='Stocks here', halign='center', valign='center', pos_hint={'x': 0, 'y': 0}, size_hint=(1, 1))

        # Update stock data every 5 minutes (5 minutes * 60 seconds = 300 seconds)
        Clock.schedule_interval(self.updateStocks, 300)

        self.updateStocks()

        # Add label to view
        self.add_widget(self.stockLabel)

    def updateStocks(self, *largs):
        # Get list of stocks desired from config file
        stocksListOfLists = getStocks()
        pricesStr = str()
        for stockList in stocksListOfLists:
            # Get price for desired stock and add it to the string for the label
            price = makeHTTPRequest('http://finance.yahoo.com/d/quotes.csv?s=' + stockList[0] + '&f=l1')
            pricesStr += "%s: $%.2f\n" % (stockList[0], float(price))

        # Remove trailing newline character
        self.stockString = pricesStr[:-1]

        self.updateUI()

    def updateUI(self):
        self.stockLabel.text = self.stockString

class DaySelector(BoxLayout):

    def __init__(self, calendarObject, **kwargs):
        super(DaySelector, self).__init__(**kwargs)

        # Configure DaySelector object
        self.orientation = 'horizontal'
        self.spacing = 2

        # Initialize data variables
        self.dayList = ['U', 'M', 'T', 'W', 'R', 'F', 'S']
        self.dayAdjustment = int(time.strftime("%w"))
        self.selectedDay = 0
        self.calendarObject = calendarObject

        # Set timer to update quote at midnight
        Clock.schedule_once(self.updateUIFirstTime, getTimeToMidnight())

        self.updateUI()

    def updateUIFirstTime(self, *largs):
        # Update widget every 24 hours (24 hours * 60 minutes * 60 seconds = 86400 seconds)
        Clock.schedule_interval(self.updateUI, 86400)

        self.updateUI()

    def updateUI(self, *largs):
        self.dayAdjustment = int(time.strftime("%w"))

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
        self.selectedDay = self.dayList.index(pressedBtn.text) - self.dayAdjustment
        self.calendarObject.updateUI()

    def getSelectedDay(self):
        return self.selectedDay

class CalendarEvent(RelativeLayout):

    def __init__(self, event, **kwargs):
        super(CalendarEvent, self).__init__(**kwargs)

        # Initialize data variables
        self.event = event
        self.displayString = ""

        # Generate string to display
        self.getDisplayString()

        # Create labels
        self.label = Label(text=self.displayString, halign='center', valign='center')

        # Add labels to view
        self.add_widget(self.label)

    def getDisplayString(self):
        # Sanitize edge cases
        startHour = self.event['localStartDate'][4]
        startHourAmPm = "AM"
        if startHour >= 12:
            startHour -= 12
            startHourAmPm = "PM"
        if startHour == 0:
            startHour = 12
        endHour = self.event['localEndDate'][4]
        endHourAmPm = "AM"
        if endHour >= 12:
            endHour -= 12
            endHourAmPm = "PM"
        if endHour == 0:
            endHour = 12

        # Create string to display
        self.displayString = "%s: %i:%02i %s to %i:%02i %s at %s" % (self.event['title'], startHour, self.event['localStartDate'][5], startHourAmPm, endHour, self.event['localEndDate'][5], endHourAmPm, self.event['location'])

        # If there is no location then remove the end of the string (… at …)
        if self.event['location'] is None:
            self.displayString = self.displayString[:-8]

class CalendarWidget(BoxLayout):

    def __init__(self, **kwargs):
        super(CalendarWidget, self).__init__(**kwargs)

        # Configure CalendarWidget object
        self.orientation = 'vertical'
        self.spacing = 5

        # Log in to iCloud API session and set up calendar control sessions
        self.icloudApi = PyiCloudService(getUsername(), getPassword())

        # Initialize data variables
        self.daySeparatedEventList = []

        # Create DaySelector widget
        self.daySelector = DaySelector(self, size=(0, 35), size_hint=(1, None))

        # Get calendar data
        self.getData()

        # Add widgets to view
        self.updateUI()
        self.add_widget(self.daySelector)

        # Set timer to update widget at midnight
        Clock.schedule_once(self.updateUIFirstTime, getTimeToMidnight())

    def updateUIFirstTime(self, *largs):
        # Update widget every 24 hours (24 hours * 60 minutes * 60 seconds = 86400 seconds)
        Clock.schedule_interval(self.getData, 86400, None)

        self.getData()

    def getData(self, *largs):
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
        self.daySeparatedEventList = [list(), list(), list(), list(), list(), list(), list()]
        for event in events:
            # Ensure that the event is not on a calendar that the user does not wish to see
            if event['pGuid'] not in exceptions:
                daysDiff = (datetime.strptime(str(event['localStartDate'][0]), dateFormat) - datetime.strptime(today, dateFormat)).days
                # Try statement needed because the API hands back a list of the next 7 days with events in them, so if the current day has no events then it will hand back too many days and the number of days' difference will be 7, exceeding the length of our list
                try:
                    self.daySeparatedEventList[daysDiff].append(event)
                except:
                    pass

        # Sort each list of events by start time
        for listOfEvents in self.daySeparatedEventList:
            listOfEvents.sort(key=operator.itemgetter('localStartDate'))

        self.updateUI()

    def updateUI(self, *largs):
        # Remove all existing widgets except for the day selector
        for child in self.children[:]:
            if child != self.daySelector:
                self.remove_widget(child)

        # Add new widgets
        for event in self.daySeparatedEventList[self.daySelector.getSelectedDay()]:
            # Add widgets at index 1 so they do not go below the day selector
            self.add_widget(CalendarEvent(event), index=1)

        if len(self.daySeparatedEventList[self.daySelector.getSelectedDay()]) == 0:
            self.add_widget(Label(text="There are no events on this day."), index=1)

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
        self.middlePane = MiddlePane(pos_hint={'x': 0.25, 'y': 0}, size_hint=(0.63, 1))
        self.rightPane = RightPane(pos_hint={'x': 0.88, 'y': 0}, size_hint=(0.12, 1))

        # Add panes to view
        self.add_widget(self.leftPane)
        self.add_widget(self.middlePane)
        self.add_widget(self.rightPane)

class PiDay(App):

    def __init__(self, **kwargs):
        super(PiDay, self).__init__(**kwargs)

        # Initialize presentation manager
        self.rootLayout = RootLayout()

    def build(self):
        return self.rootLayout

def getTimeToMidnight():
    now = datetime.now()
    tomorrow = datetime(now.year, now.month, now.day) + timedelta(1)
    return abs(tomorrow - now).seconds * 1000 + 1000

def makeHTTPRequest(url):
    response = ""
    try:
        r = urllib.request.urlopen(url)
        response = r.read().decode('utf-8')
        r.close()
    except:
        response = "Error retrieving data"
    return response

# Start the program
if __name__ == "__main__":
    PiDay().run()
