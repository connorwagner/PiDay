import kivy
kivy.require('1.0.6')

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.boxlayout import BoxLayout

import time
import json
import urllib.request
import subprocess
from datetime import datetime, timedelta
from functools import partial

import operator
from pyicloud import PyiCloudService

from config import getUsername, getPassword, getStocks, getWeatherLocale, getCalendarExceptions, getQuotaCurl

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

        # Initialize data variables
        self.recur = None

        # Initialize label
        self.quoteLabel = Label(text='Quote here', halign='center', valign='center', max_lines=8)

        # Add label to view
        self.add_widget(self.quoteLabel)

        # Configure label to adjust height to fit text (can only be done after label has been added to a view)
        self.quoteLabel.size = (self.quoteLabel.parent.width * 1.85, self.quoteLabel.texture_size[1])
        self.quoteLabel.text_size = (self.quoteLabel.width, None)
        self.quoteLabel.size_hint = (1, None)

        self.updateUI()

    def startTimer(self):
        # Set timer to update quote at midnight
        self.recur = Clock.schedule_once(self.updateUIFirstTime, getTimeToMidnight())

    def updateUIFirstTime(self, *largs):
        # Update quote every 24 hours (24 hours * 60 minutes * 60 seconds = 86400 seconds)
        self.recur = Clock.schedule_interval(self.updateUI, 86400)
        self.updateUI()

    def updateUI(self, *largs):
        # Get quote from API call
        quote = makeHTTPRequest("http://ron-swanson-quotes.herokuapp.com/v2/quotes")

        # If makeHTTPRequest returned False then there was an error, end the function
        if not quote:
            return

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
        self.recur = None

        # Initialize label
        self.weatherLabel = Label(text='Weather here', halign='center', valign='center', pos_hint={'x': 0, 'y': 0}, size_hint=(1, 1))

        self.updateWeather()

        # Add label to view
        self.add_widget(self.weatherLabel)

    def startTimer(self):
        # Update weather every 15 minutes (15 minutes * 60 seconds = 900 seconds)
        self.recur = Clock.schedule_interval(self.updateWeather, 900)

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

        # Get current weather data and convert to dictionary from JSON
        currentJsonStr = makeHTTPRequest("http://api.openweathermap.org/data/2.5/weather?q=%s&appid=533616ff356c7a5963e935e12fbb9306&units=imperial" % getWeatherLocale())

        # If makeHTTPRequest returned False then there was an error, end the function
        if not forecastJsonStr or not forecastJsonStr:
            return

        forecastJsonDict = json.loads(forecastJsonStr)
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
        self.recur = None

        # Initialize label
        self.stockLabel = Label(text='Stocks here', halign='center', valign='center', pos_hint={'x': 0, 'y': 0}, size_hint=(1, 1))

        self.updateStocks()

        # Add label to view
        self.add_widget(self.stockLabel)

    def startTimer(self):
        # Update stock data every 5 minutes (5 minutes * 60 seconds = 300 seconds)
        self.recur = Clock.schedule_interval(self.updateStocks, 300)

    def updateStocks(self, *largs):
        # Get list of stocks desired from config file
        stocksListOfLists = getStocks()
        pricesStr = str()
        for stockList in stocksListOfLists:
            # Get price for desired stock and add it to the string for the label
            price = makeHTTPRequest('http://finance.yahoo.com/d/quotes.csv?s=' + stockList[0] + '&f=l1')

            # If makeHTTPRequest returns False then there was an error, end the function
            if not price:
                return

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
        self.recur = None

        self.updateUI()

    def startTimer(self):
        # Set timer to update quote at midnight
        self.recur = Clock.schedule_once(self.updateUIFirstTime, getTimeToMidnight())

    def updateUIFirstTime(self, *largs):
        # Update widget every 24 hours (24 hours * 60 minutes * 60 seconds = 86400 seconds)
        self.recur = Clock.schedule_interval(self.updateUI, 86400)

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

        # Create auth variables
        self.twoFactorDone = False
        self.twoFactorScreen = None
        self.icloudApi = None
        self.recur = None

        # Initialize data variables
        self.daySeparatedEventList = []

        # Create DaySelector widget
        self.daySelector = DaySelector(self, size=(0, 35), size_hint=(1, None))
        self.add_widget(self.daySelector)

    def finishInitSetup(self):
        # Get calendar data
        self.getData()

        # Add widgets to view
        self.updateUI()

    def startTimer(self):
        # Set timer to update widget at midnight
        self.recur = Clock.schedule_once(self.updateUIFirstTime, getTimeToMidnight())

    def authenticate(self):
        self.icloudApi = PyiCloudService(getUsername(), getPassword())
        if self.icloudApi.requires_2fa:
            self.twoFactorScreen = TwoFactorAuthScreen(self)
        else:
            self.finishInitSetup()

    def updateUIFirstTime(self, *largs):
        # Update widget every 30 minutes (30 minutes * 60 seconds = 1800 seconds)
        self.recur = Clock.schedule_interval(self.getData, 1800)
        self.daySelector.startTimer()

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

        # Initialize variables
        self.isDark = False
        self.darkTitle = "Go Dark"
        self.brightTitle = "Turn It Up"

        # Create button
        self.button = Button(text=self.darkTitle, halign='center', valign='center')

        # Configure button
        self.button.bind(on_press=self.switchBrightness)

        # Add button to view
        self.add_widget(self.button)

    def switchBrightness(self, *largs):
        if self.isDark:
            self.isDark = False
            self.brightScreen()
            self.button.text = self.darkTitle
        else:
            self.isDark = True
            self.darkScreen()
            self.button.text = self.brightTitle

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

class QuotaWidget(BoxLayout):

    def __init__(self, **kwargs):
        super(QuotaWidget, self).__init__(**kwargs)

        # Configure QuotaWidget object
        self.orientation = 'vertical'
        self.spacing = 10

        # Create container object so pictures are displayed side by side
        self.container = BoxLayout(orientation='horizontal', spacing=15)
        self.add_widget(self.container)

        # Create variables for later use
        self.curlCall = []
        curlStr = getQuotaCurl()
        inQuotes = False
        lastIndex = 0
        for i in range(len(curlStr)):
            if curlStr[i] == ' ':
                if not inQuotes:
                    newStr = curlStr[lastIndex:i].replace("'",'').strip()
                    if len(newStr) > 0:
                        self.curlCall.append(newStr)
                    lastIndex = i + 1
            if curlStr[i] == "'":
                if inQuotes:
                    inQuotes = False
                    newStr = curlStr[lastIndex:i].replace("'",'').strip()
                    if len(newStr) > 0:
                        self.curlCall.append(newStr)
                    lastIndex = i + 1
                else:
                    inQuotes = True
                    lastIndex = i + 1
        lastStr = curlStr[lastIndex:].strip()
        if len(lastStr) > 0:
            self.curlCall.append(lastStr)
        self.workingDir = str(subprocess.check_output('pwd'))[2:-3]
        self.dailyImage = None
        self.weeklyImage = None
        self.popup = None

        # Add close button for popup
        self.closeButton = Button(text="Close", halign='center', valign='center', size_hint=(1, 0.15))
        self.add_widget(self.closeButton)

    def updateImageDisplays(self):
        self.dailyImage = Image(source='%s/dailyQuota.png' % self.workingDir)
        self.weeklyImage = Image(source='%s/weeklyQuota.png' % self.workingDir)

        self.container.add_widget(self.dailyImage)
        self.container.add_widget(self.weeklyImage)

    def loadDailyImage(self, *largs):
        dailyCurl = self.curlCall[:]
        dailyCurl[1] += "daily"
        with open('%s/dailyQuota.png' % self.workingDir, 'w') as file:
            subprocess.call(dailyCurl, stdout=file)

    def loadWeeklyImage(self, *largs):
        weeklyCurl = self.curlCall[:]
        weeklyCurl[1] += "weekly"
        with open('%s/weeklyQuota.png' % self.workingDir, 'w') as file:
            subprocess.call(weeklyCurl, stdout=file)

class ControlWidgets(BoxLayout):

    def __init__(self, **kwargs):
        super(ControlWidgets, self).__init__(**kwargs)

        # Configure ControlWidgets object
        self.orientation = 'vertical'
        self.spacing = 10

        # Define variables for later use
        self.quotaWidget = None
        self.popup = None

        # Create widgets
        self.brightnessWidgets = BrightnessWidgets()
        self.quotaButton = Button(text="View Quota", halign='center', valign='center')
        self.exitButton = Button(text="Exit", halign='center', valign='center')

        # Configure buttons
        self.quotaButton.bind(on_press=self.openQuotaWidget)
        self.exitButton.bind(on_press=exit)

        # Add widgets to view
        self.add_widget(self.brightnessWidgets)
        self.add_widget(self.quotaButton)
        self.add_widget(self.exitButton)

    def openQuotaWidget(self, *largs):
        # Create QuotaWidget object to display
        self.quotaWidget = QuotaWidget()

        self.quotaWidget.loadDailyImage()
        self.quotaWidget.loadWeeklyImage()

        # Display popup
        self.popup = Popup(title="Quota Usage", content=self.quotaWidget)
        self.quotaWidget.closeButton.bind(on_press=self.popup.dismiss)
        self.popup.open()

        self.quotaWidget.updateImageDisplays()

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

    def on_start(self):
        self.rootLayout.middlePane.calendarWidget.authenticate()

        self.root_window.bind(on_show=self.startMidnightTimers)

    def startMidnightTimers(self):
        print("Running")
        self.rootLayout.leftPane.stockWidget.startTimer()
        self.rootLayout.leftPane.weatherWidget.startTimer()
        self.rootLayout.leftPane.quoteWidget.startTimer()

# Helper classes and functions
# TODO: Make this work
class LoadingIndicator(Popup):

    def __init__(self, **kwargs):
        super(LoadingIndicator, self).__init__(**kwargs)

        self.progressBar = ProgressBar(max=1, value=0)
        self.add_widget(self.progressBar)

    def update(self, value):
        self.progressBar.value = value

class TwoFactorAuthScreen(Popup):

    def __init__(self, calendarWidgetObject, **kwargs):
        super(TwoFactorAuthScreen, self).__init__(**kwargs)

        self.title = "Two Factor Authentication"

        # Initialize variables
        self.calendarWidgetObject = calendarWidgetObject
        self.device = None

        self.container = BoxLayout(orientation='vertical', spacing=15)
        self.add_widget(self.container)

        self.numberString = ""
        self.numberDisplay = Label(text=self.numberString, halign='center', valign='center')
        self.container.add_widget(self.numberDisplay)

        # Configure each row of buttons
        self.firstRow = BoxLayout(orientation='horizontal', spacing=15)

        self.oneButton = Button(text='1', valign='center', halign='center')
        self.oneButton.bind(on_press=partial(self.numberPressed, 1))
        self.firstRow.add_widget(self.oneButton)

        self.twoButton = Button(text='2', valign='center', halign='center')
        self.twoButton.bind(on_press=partial(self.numberPressed, 2))
        self.firstRow.add_widget(self.twoButton)

        self.threeButton = Button(text='3', valign='center', halign='center')
        self.threeButton.bind(on_press=partial(self.numberPressed, 3))
        self.firstRow.add_widget(self.threeButton)

        self.secondRow = BoxLayout(orientation='horizontal', spacing=15)

        self.fourButton = Button(text='4', valign='center', halign='center')
        self.fourButton.bind(on_press=partial(self.numberPressed, 4))
        self.secondRow.add_widget(self.fourButton)

        self.fiveButton = Button(text='5', valign='center', halign='center')
        self.fiveButton.bind(on_press=partial(self.numberPressed, 5))
        self.secondRow.add_widget(self.fiveButton)

        self.sixButton = Button(text='6', valign='center', halign='center')
        self.sixButton.bind(on_press=partial(self.numberPressed, 6))
        self.secondRow.add_widget(self.sixButton)

        self.thirdRow = BoxLayout(orientation='horizontal', spacing=15)

        self.sevenButton = Button(text='7', valign='center', halign='center')
        self.sevenButton.bind(on_press=partial(self.numberPressed, 7))
        self.thirdRow.add_widget(self.sevenButton)

        self.eightButton = Button(text='8', valign='center', halign='center')
        self.eightButton.bind(on_press=partial(self.numberPressed, 8))
        self.thirdRow.add_widget(self.eightButton)

        self.nineButton = Button(text='9', valign='center', halign='center')
        self.nineButton.bind(on_press=partial(self.numberPressed, 9))
        self.thirdRow.add_widget(self.nineButton)

        self.fourthRow = BoxLayout(orientation='horizontal', spacing=15)

        self.enterButton = Button(text='Enter', valign='center', halign='center')
        self.enterButton.bind(on_press=self.enterButtonPress)
        self.fourthRow.add_widget(self.enterButton)

        self.zeroButton = Button(text='0', valign='center', halign='center')
        self.zeroButton.bind(on_press=partial(self.numberPressed, 0))
        self.fourthRow.add_widget(self.zeroButton)

        self.deleteButton = Button(text='Delete', valign='center', halign='center')
        self.deleteButton.bind(on_press=self.deleteButtonPress)
        self.fourthRow.add_widget(self.deleteButton)

        self.container.add_widget(self.firstRow)
        self.container.add_widget(self.secondRow)
        self.container.add_widget(self.thirdRow)
        self.container.add_widget(self.fourthRow)

        self.open()

        self.promptForDevice()

    def promptForDevice(self):
        devicePrompt = "Your trusted devices are:\n"
        devices = self.calendarWidgetObject.icloudApi.trusted_devices
        for i, device in enumerate(devices):
            devicePrompt += "[%d] %s\n" % (i, device.get('deviceName', "SMS to %s" % device.get('phoneNumber')))
        devicePrompt += "Which device would you like to use?"
        self.displayMessage(devicePrompt)

        deviceNum = 0
        self.device = devices[deviceNum]
        if not self.calendarWidgetObject.icloudApi.send_verification_code(self.device):
            self.displayMessage("Failed to send verification code")
            time.sleep(3)
            exit()

        self.displayMessage('Please enter validation code')

    def displayMessage(self, message):
        self.numberDisplay.text = message

    def numberPressed(self, num, *largs):
        self.addDigitToString(num)

    def enterButtonPress(self, *largs):
        if not self.calendarWidgetObject.icloudApi.validate_verification_code(self.device, self.numberString):
            self.displayMessage("Failed to verify verification code")
            time.sleep(3)
            exit()
        self.calendarWidgetObject.finishInitSetup()
        self.dismiss()

    def deleteButtonPress(self, *largs):
        self.numberString = self.numberString[:-1]
        self.numberDisplay.text = self.numberString

    def addDigitToString(self, digit):
        self.numberString += str(digit)
        self.numberDisplay.text = self.numberString

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
        response = False
    return response

# Start the program
if __name__ == "__main__":
    # We need to keep a reference to the PiDay object so it is not garbage collected
    # If the object is garbage collected then the schedule calls will not work
    app = PiDay()
    app.run()
