import kivy
kivy.require('1.0.6')

from kivy.app import App
from kivy.config import Config
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.boxlayout import BoxLayout

from ConnectFour import ConnectFour
from Simon import Simon
from Othello import Othello
from TicTacToe import TicTacToe

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

        # Update clock every 30 seconds
        Clock.schedule_interval(self.updateTime, 30)

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
        self.stockButton = Button(background_color=[0, 0, 0, 1], on_press=self.openStockDetailsWidget, text='Stocks here', halign='center', valign='center', pos_hint={'x': 0, 'y': 0}, size_hint=(1, 1))

        self.updateStocks()

        # Add label to view
        self.add_widget(self.stockButton)

    def startTimer(self):
        # Update stock data every 5 minutes (5 minutes * 60 seconds = 300 seconds)
        self.recur = Clock.schedule_interval(self.updateStocks, 300)

    def updateStocks(self, *largs):
        # Get list of stocks desired from config file
        stocksListOfLists = getStocks()
        pricesStr = str()
        for stockList in stocksListOfLists:
            # Get price for desired stock and add it to the string for the label
            jsonData = makeHTTPRequest('https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&interval=5min&outputsize=compact&symbol=' + stockList[0] + '&apikey=DBC2MS0TUABOLZ04')

            # If makeHTTPRequest returns False then there was an error, end the function
            if not jsonData:
                pricesStr = "Error retrieving data "
                break

            data = json.loads(jsonData)
            try:
                mostRecentUpdate = data['Meta Data']['3. Last Refreshed']
                price = data['Time Series (5min)'][mostRecentUpdate]['4. close']

                pricesStr += "%s: $%.2f\n" % (stockList[0], float(price))
            except:
                print("error retrieving stocks")

        # Remove trailing newline character
        self.stockString = pricesStr[:-1]

        self.updateUI()

    def updateUI(self):
        self.stockButton.text = self.stockString

    def openStockDetailsWidget(self, *largs):
        self.stockDetailsWidget = StockDetailsWidget()

        self.popup = Popup(title="Stock Details", content=self.stockDetailsWidget)
        self.stockDetailsWidget.closeButton.bind(on_press=self.popup.dismiss)
        self.popup.open()

class StockDetailsWidget(BoxLayout):
    def __init__(self, **kwargs):
        super(StockDetailsWidget, self).__init__(**kwargs)

        self.orientation = 'vertical'
        self.spacing = 10

        self.stockPriceList = []
        self.accountGainLoss = 0
        self.accountWorth = 0

        self.loadStocks()

        self.topContainer = BoxLayout(orientation='horizontal', spacing=10, size_hint=(1, 0.15))
        self.bottomContainer = BoxLayout(orientation='vertical', spacing=10, size_hint=(1, 0.70))
        self.closeButton = Button(text="Close", halign='center', valign='center', size_hint=(1, 0.15))

        if self.accountGainLoss < 0:
            self.accountGainLossLabel = Label(text="Account Loss: $ " + str("%.2f" % abs(self.accountGainLoss)))
        else:
            self.accountGainLossLabel = Label(text="Account Gain: $ " + str("%.2f" % abs(self.accountGainLoss)))

        if self.accountWorth < 0:
            self.accountWorthLabel = Label(text="Account Worth: - $ " + str("%.2f" % abs(self.accountWorth)))
        else:
            self.accountWorthLabel = Label(text="Account Worth: $ " + str("%.2f" % self.accountWorth))

        self.topContainer.add_widget(self.accountWorthLabel)
        self.topContainer.add_widget(self.accountGainLossLabel)

        self.tempContainer = BoxLayout(orientation='horizontal', spacing=10)
        self.tempContainer.add_widget(Label(text="Stock Symbol:"))
        self.tempContainer.add_widget(Label(text="Gain/Loss:"))
        self.tempContainer.add_widget(Label(text="Current Value:"))
        self.tempContainer.add_widget(Label(text="Bought at:"))
        self.tempContainer.add_widget(Label(text="Owned:"))
        self.bottomContainer.add_widget(self.tempContainer)

        for x in range(len(self.stockPriceList)):
            rowContainer = BoxLayout(orientation='horizontal', spacing=10)
            for y in range(5):
                rowContainer.add_widget(Label(text=self.stockPriceList[x][y]))
            self.bottomContainer.add_widget(rowContainer)

        self.add_widget(self.topContainer)
        self.add_widget(self.bottomContainer)
        self.add_widget(self.closeButton)

    def loadStocks(self, *largs):
        # Get list of stocks desired from config file
        stocksListOfLists = getStocks()
        for stockList in stocksListOfLists:
            # Get price for desired stock and add it to the string for the label
            jsonData = makeHTTPRequest(
                'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&interval=5min&outputsize=compact&symbol=' +
                stockList[0] + '&apikey=DBC2MS0TUABOLZ04')

            # If makeHTTPRequest returns False then there was an error, end the function
            if not jsonData:
                break

            data = json.loads(jsonData)
            mostRecentUpdate = data['Meta Data']['3. Last Refreshed']
            price = data['Time Series (5min)'][mostRecentUpdate]['4. close']

            # Append an extra 0 if bought at "50.0" for example, so it shows "50.00"
            boughtAtString = str(stockList[1])
            boughtAtInt = int(stockList[1])
            if float(boughtAtInt) == stockList[1]:
                boughtAtString += "0"

            gainLossString = ""
            gainLoss = (float(price) - float(stockList[1])) * stockList[2]
            if gainLoss < 0:
                gainLossString = "- $ " + str("%.2f" % abs(gainLoss))
            else:
                gainLossString = "+ $ " + str("%.2f" % abs(gainLoss))

            self.accountGainLoss += gainLoss

            self.accountWorth += float(price) * stockList[2]

            self.stockPriceList.append([str(stockList[0]), gainLossString, ("$ %.2f" % float(price)), "$ " + boughtAtString, str(stockList[2])])

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
        self.brightTitle = "Go Bright"

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

class GamesWidget(RelativeLayout):

    def __init__(self, **kwargs):
        super(GamesWidget, self).__init__(**kwargs)

        self.orientation = 'vertical'
        self.spacing = 10

        # Make the gameWidget containers (will hold rows of game buttons)
        self.containerTop = BoxLayout(orientation='horizontal', spacing=10, pos_hint={'x': 0, 'y': 0.60}, size_hint=(1, 0.40))
        self.containerBottom = BoxLayout(orientation='horizontal', spacing=10, pos_hint={'x': 0, 'y': 0.17}, size_hint=(1, 0.40))
        self.containerClose = BoxLayout(orientation='horizontal', spacing=10, pos_hint={'x': 0, 'y': 0})

        self.othelloButton = Button(text="Othello", halign='center', valign='center')
        self.connectFourButton = Button(text="Connect Four", halign='center', valign='center')
        self.tttButton = Button(text="TicTacToe", halign='center', valign='center')
        self.simonButton = Button(text="Simon", halign='center', valign='center')

        self.closeButton = Button(text="Close", halign='right', valign='center', size_hint=(1, 0.15))

        # Top row will contain TicTacToe, and Connect Four
        # Bottom row will contain Othello and Simon
        self.containerTop.add_widget(self.tttButton)
        self.containerTop.add_widget(self.connectFourButton)
        self.containerBottom.add_widget(self.othelloButton)
        self.containerBottom.add_widget(self.simonButton)
        self.containerClose.add_widget(self.closeButton)

        self.add_widget(self.containerTop)
        self.add_widget(self.containerBottom)
        self.add_widget(self.containerClose)

        # Bind game buttons to respective launcher functions
        self.tttButton.bind(on_press=self.openTicTacToe)
        self.othelloButton.bind(on_press=self.openOthello)
        self.simonButton.bind(on_press=self.openSimon)
        self.connectFourButton.bind(on_press=self.openConnectFour)

    # Opens the TicTacToe popup
    def openTicTacToe(self, *largs):
        self.tttWidget = TicTacToeWidget()
        self.tttPopup = Popup(title="Tic Tac Toe", content=self.tttWidget)
        self.tttWidget.exitButton.bind(on_press=self.tttPopup.dismiss)
        self.tttPopup.open()

    # Opens the Othello popup
    def openOthello(self, *largs):
        self.othelloWidget = OthelloWidget()
        self.othelloPopup = Popup(title="Othello", content=self.othelloWidget)
        self.othelloWidget.exitButton.bind(on_press=self.othelloPopup.dismiss)
        self.othelloPopup.open()

    # Opens the Simon Popup, and the Start popup (not totally functional)
    def openSimon(self, *largs):
        self.simonWidget = SimonWidget()
        self.simonPopup = Popup(title="Simon", content=self.simonWidget)
        self.simonPopup.open()
        self.simonWidget.startingPopUp()
        self.simonWidget.exitButton.bind(on_press=self.simonPopup.dismiss)

    # Opens the connect four popup
    def openConnectFour(self, *largs):
        self.connectFourWidget = ConnectFourWidget()
        self.connectFourPopup = Popup(title="Connect Four", content=self.connectFourWidget)
        self.connectFourPopup.open()
        self.connectFourWidget.exitButton.bind(on_press=self.connectFourPopup.dismiss)

class TicTacToeWidget(BoxLayout):
    def __init__(self, *largs, **kwargs):
        super(TicTacToeWidget, self).__init__(**kwargs)

        self.orientation = 'horizontal'
        self.spacing = 7

        # Create the containers for the popup
        self.boardContainer = BoxLayout(orientation='vertical', spacing=5, size_hint=(0.90, 1))
        self.leftSideContainer = BoxLayout(orientation='vertical', spacing=10, size_hint=(0.10, 1))

        self.ttt = TicTacToe()

        # Create control buttons to be put in the side container
        self.exitButton = Button(text="Exit", halign='right', valign='center')
        self.resetButton = Button(text="Reset", halign='right', valign='center', on_press=self.resetGame)

        self.containerList = []
        self.btnList = []

        # Add buttons to rows in rowsContainer
        for row in range(3):
            self.containerList.append(BoxLayout(orientation='horizontal', spacing=5))
            self.tempList = []
            for col in range(3):
                temp = Button(text='X', color=[192, 192, 192, 0.30], halign='right', valign='top', background_normal='atlas://data/images/defaulttheme/button_disabled', font_size=84, on_press=partial(self.playerMoveHelper, row, col))
                self.containerList[row].add_widget(temp)
                self.tempList.append(temp)
            self.btnList.append(self.tempList)

        for container in self.containerList:
            self.boardContainer.add_widget(container)

        # Add widgets to their respective containers
        self.leftSideContainer.add_widget(self.exitButton)
        self.leftSideContainer.add_widget(self.resetButton)
        self.add_widget(self.leftSideContainer)
        self.add_widget(self.boardContainer)

    # Helper function for playerMove() (called by pressing a button)
    def playerMoveHelper(self, row, col, *largs):
        state = self.ttt.whoseTurn()
        self.ttt.playerMove(row, col, state)

        # Disable the chosen spot, and set it's text properly
        self.btnList[row][col].disabled = True
        if state == 1:
            self.btnList[row][col].text = "X"
        else:
            self.btnList[row][col].text = "O"

        # Code below is used to show whose turn it is / possible moves
        for x in range(3):
            for y in range(3):
                if self.ttt.gameBoard[x][y] == 0:
                    if state == 2:
                        self.btnList[x][y].text = "X"
                    else:
                        self.btnList[x][y].text = "O"

        self.isWinner(row, col, state)

    # Determines if there is a winner, and displays an appropriate popup if there is
    def isWinner(self, row, col, state):
        if self.ttt.isWinner(row, col, state):
            for row in range(3):
                for col in range(3):
                    self.btnList[row][col].disabled = True
                    if self.ttt.gameBoard[row][col] == 0:
                        self.btnList[row][col].text = ""

            if state == 1:
                self.popupWinner = Popup(title="Game Over", content=Label(text="Player X Wins!!"), size_hint=(0.50, 0.50))
                self.popupWinner.open()
                return
            else:
                self.popupWinner = Popup(title="Game Over", content=Label(text="Player O Wins!!"), size_hint=(0.50, 0.50))
                self.popupWinner.open()
                return

        if self.ttt.getNumSpotsLeft() == 0:
            self.popupDraw = Popup(title="Game Over", content=Label(text="Draw!!"), size_hint=(0.50, 0.50))
            self.popupDraw.open()

    # Resets game board and visual board
    def resetGame(self, *largs):
        self.ttt.spotsUsed = 0
        self.ttt.recentState = 1
        self.ttt.recentCol = 0
        self.ttt.recentRow = 0
        self.ttt.winner = -1

        for row in range(3):
            for col in range(3):
                self.ttt.gameBoard[row][col] = 0
                self.btnList[row][col].text = "X"
                self.btnList[row][col].color = [192, 192, 192, 0.30]
                self.btnList[row][col].disabled = False

class OthelloWidget(BoxLayout):
    def __init__(self, *largs, **kwargs):
        super(OthelloWidget, self).__init__(**kwargs)

        self.orientation = 'horizontal'
        self.spacing = 7

        # Create containers to divide the othello popup
        self.boardContainer = BoxLayout(orientation='vertical', spacing=1, size_hint=(0.90, 1))
        self.leftSideContainer = BoxLayout(orientation='vertical', spacing=10, size_hint=(0.10, 1))
        self.rightSideContainer = BoxLayout(orientation='vertical', spacing=10, size_hint=(0.10, 1))

        self.othello = Othello()

        # Create exit & reset button for left side container
        self.exitButton = Button(text="Exit", halign='right', valign='center')
        self.resetButton = Button(text="Reset", halign='right', valign='center', on_press=self.resetGame)

        # Create buttons to track # of black and white tokens, as well as whose turn it is (for right side container)
        self.blackTokenButton = Button(text=str(self.othello.twoCtr), background_disabled_normal='atlas://data/images/defaulttheme/button', halign='right', valign='center', disabled=True, background_color=[0, 0, 0, 1])
        self.whiteTokenButton = Button(text=str(self.othello.oneCtr), color=[0, 0, 0, 1], background_disabled_normal='atlas://data/images/defaulttheme/button', halign='right', valign='center', disabled=True, background_color=[60, 179, 113, 1])
        self.whoseTurnButton = Button(text="Turn", halign='right', background_disabled_normal='atlas://data/images/defaulttheme/button', valign='center', disabled=True, background_color=[0, 0, 0, 1])

        self.containerList = []
        self.btnList = []

        # Add buttons to rows in rowsContainer
        for row in range(8):
            self.containerList.append(BoxLayout(orientation='horizontal', spacing=1))
            self.tempList = []
            for col in range(8):
                temp = Button(halign='right', valign='top', background_disabled_normal='atlas://data/images/defaulttheme/button', background_color=[0, 100, 0, 0.50], on_press=partial(self.playerMoveHelper, row, col, self.othello.whoseTurn()))
                self.containerList[row].add_widget(temp)
                self.tempList.append(temp)
            self.btnList.append(self.tempList)

        # Manually add the four center tokens (do this so whoseTurn() isn't messed up, as black must go first)
        self.othello.gameBoard[3][3] = 1
        self.othello.gameBoard[3][4] = 2
        self.othello.gameBoard[4][3] = 2
        self.othello.gameBoard[4][4] = 1
        self.btnList[3][3].background_color = [60, 179, 113, 1]
        self.btnList[3][4].background_color = [0, 0, 0, 1]
        self.btnList[4][3].background_color = [0, 0, 0, 1]
        self.btnList[4][4].background_color = [60, 179, 113, 1]
        self.btnList[3][3].disabled = True
        self.btnList[3][4].disabled = True
        self.btnList[4][3].disabled = True
        self.btnList[4][4].disabled = True

        # Add all the container rows to the row container
        for container in self.containerList:
            self.boardContainer.add_widget(container)

        # Add widgets to their respective containers
        self.rightSideContainer.add_widget(self.whiteTokenButton)
        self.rightSideContainer.add_widget(self.blackTokenButton)
        self.rightSideContainer.add_widget(self.whoseTurnButton)
        self.leftSideContainer.add_widget(self.exitButton)
        self.leftSideContainer.add_widget(self.resetButton)
        self.add_widget(self.leftSideContainer)
        self.add_widget(self.boardContainer)
        self.add_widget(self.rightSideContainer)

        for x in range(8):
            for y in range(8):
                if self.btnList[x][y].background_color == [0, 100, 0, 0.50]:
                    if self.othello.checkForSwaps(x, y, self.othello.whoseTurn()) == []:
                        self.btnList[x][y].disabled = True
                    else:
                        self.btnList[x][y].disabled = False

    # Function called by the reset button, resets the game
    def resetGame(self, *largs):

        self.othello.oneCtr = 2
        self.othello.twoCtr = 2
        self.othello.placeCtr = 4

        for row in range(8):
            for col in range(8):
                self.othello.gameBoard[row][col] = 0
                self.btnList[row][col].background_color = [0, 100, 0, 0.50]
                self.btnList[row][col].disabled = False

        # Manually add the four center tokens (do this so whoseTurn() isn't messed up, as black must go first)
        self.othello.gameBoard[3][3] = 1
        self.othello.gameBoard[3][4] = 2
        self.othello.gameBoard[4][3] = 2
        self.othello.gameBoard[4][4] = 1
        self.btnList[3][3].background_color = [60, 179, 113, 1]
        self.btnList[3][4].background_color = [0, 0, 0, 1]
        self.btnList[4][3].background_color = [0, 0, 0, 1]
        self.btnList[4][4].background_color = [60, 179, 113, 1]
        self.btnList[3][3].disabled = True
        self.btnList[3][4].disabled = True
        self.btnList[4][3].disabled = True
        self.btnList[4][4].disabled = True

        # Disable buttons for invalid moves
        for x in range(8):
            for y in range(8):
                if self.btnList[x][y].background_color == [0, 100, 0, 0.50]:
                    if self.othello.checkForSwaps(x, y, self.othello.whoseTurn()) == []:
                        self.btnList[x][y].disabled = True
                    else:
                        self.btnList[x][y].disabled = False

        # Update the display buttons
        self.blackTokenButton.text = str(self.othello.twoCtr)
        self.whiteTokenButton.text = str(self.othello.oneCtr)
        self.whoseTurnButton.background_color = [0, 0, 0, 1]
        self.whoseTurnButton.color = [60, 179, 113, 1]

    # Helper function called when a placeButton is pressed
    def playerMoveHelper(self, row, col, state, *largs):
        state = self.othello.whoseTurn()

        # Check for any swaps, if there are any, swap them
        self.allSwaps = self.othello.playerMove(row, col, state)
        if self.allSwaps != []:
            for item in self.allSwaps:
                if state == 2:
                    self.btnList[item[0]][item[1]].background_color = [0, 0, 0, 1]
                else:
                    self.btnList[item[0]][item[1]].background_color = [60, 179, 113, 1]

        # Disabled place button that was pressed
        self.btnList[row][col].disabled = True

        # Swap the whoseTurnButton, and the color of the pressed button
        if state == 2:
            self.whoseTurnButton.background_color = [60, 179, 113, 1]
            self.whoseTurnButton.color = [0, 0, 0, 1]
            self.btnList[row][col].background_color = [0, 0, 0, 1]
        else:
            self.whoseTurnButton.background_color = [0, 0, 0, 1]
            self.whoseTurnButton.color = [60, 179, 113, 1]
            self.btnList[row][col].background_color = [60, 179, 113, 1]

        # Update the # of tokens there are currently on the buttons
        self.blackTokenButton.text = str(self.othello.twoCtr)
        self.whiteTokenButton.text = str(self.othello.oneCtr)

        for x in range(8):
            for y in range(8):
                if self.btnList[x][y].background_color == [0, 100, 0, 0.50]:
                    if self.othello.checkForSwaps(x, y, self.othello.whoseTurn()) == []:
                        self.btnList[x][y].disabled = True
                    else:
                        self.btnList[x][y].disabled = False

        self.checkWinner()

    # Determines if there was a winner, and produces a popup for that winner
    def checkWinner(self):
        if self.othello.isWinner():
            if self.othello.twoCtr > self.othello.oneCtr:
                self.popupWinner = Popup(title="Game Over", content=Label(text="Black player wins!!"), size_hint=(0.50, 0.50))
                self.popupWinner.open()
            elif self.othello.oneCtr > self.othello.twoCtr:
                self.popupWinner = Popup(title="Game Over", content=Label(text="White player wins!!"), size_hint=(0.50, 0.50))
                self.popupWinner.open()
            else:
                self.popupWinner = Popup(title="Game Over", content=Label(text="Draw!!"), size_hint=(0.50, 0.50))
                self.popupWinner.open()

class SimonWidget(BoxLayout):
    def __init__(self, *largs, **kwargs):
        super(SimonWidget, self).__init__(**kwargs)

        self.orientation = 'horizontal'
        self.spacing = 7

        # Instantiate the buttons that will be in the side container
        self.exitButton = Button(text="Exit", halign='right', valign='center')
        self.resetButton = Button(text="Reset", halign='right', valign='center', on_press=self.resetGame)

        self.simon = Simon()

        # Main container will contain top and bot containers, which will contain the colored buttons
        self.sideContainer = BoxLayout(orientation='vertical', spacing=10, size_hint=(0.10, 1))
        self.mainContainer = BoxLayout(orientation='vertical', spacing=10, size_hint=(0.90, 1))
        self.topContainer = BoxLayout(orientation='horizontal', spacing=10)
        self.botContainer = BoxLayout(orientation='horizontal', spacing=10)

        # buttonList holds the color buttons
        self.buttonList = []

        # Holds the user inputted colors
        self.userColorList = []

        # Instantiate the color buttons, and bind them to add their respective color to the list
        self.greenButton = Button(halign='right', valign='center', disabled=True, background_color=[0, 1, 0, 0.20], on_press=partial(self.addToUserColorList, "G"))
        self.redButton = Button(halign='right', valign='center', disabled=True, background_color=[1, 0, 0, 0.20], on_press=partial(self.addToUserColorList, "R"))
        self.yellowButton = Button(halign='right', valign='center', disabled=True, background_color=[255, 255, 0, 0.20], on_press=partial(self.addToUserColorList, "Y"))
        self.blueButton = Button(halign='right', valign='center', disabled=True, background_color=[0, 0, 1, 0.20], on_press=partial(self.addToUserColorList, "B"))

        self.buttonList.append(self.greenButton)
        self.buttonList.append(self.redButton)
        self.buttonList.append(self.yellowButton)
        self.buttonList.append(self.blueButton)

        # Add all widgets in proper order
        self.topContainer.add_widget(self.greenButton)
        self.topContainer.add_widget(self.redButton)
        self.botContainer.add_widget(self.yellowButton)
        self.botContainer.add_widget(self.blueButton)

        self.sideContainer.add_widget(self.exitButton)
        self.sideContainer.add_widget(self.resetButton)

        self.mainContainer.add_widget(self.topContainer)
        self.mainContainer.add_widget(self.botContainer)

        self.add_widget(self.sideContainer)
        self.add_widget(self.mainContainer)

        # Create the start popup, which SHOULD start the game upon its dismissal, and has a 'Start' button that calls a function to dismiss itself
        self.popupStart = Popup(title="Simon", content=Button(text="Start Game", on_press=self.dismissPopup), on_dismiss=self.startGame, size_hint=(0.50, 0.50))

    def startingPopUp(self):
        self.popupStart.open()

    def dismissPopup(self, *largs):
        self.popupStart.dismiss()

    # Displays initial color, and allows for first userInput
    def startGame(self, *largs):
        self.simon.addColor()
        self.displayOrder()
        self.userInput()

    # Use for debugging currently, will fully reset the game later
    def resetGame(self, *largs):
        self.userColorList = []

    # If the user sequence was correctly, flash buttons green
    def displayCorrect(self):
        for button in self.buttonList:
            button.disabled = True
            button.background_color = [0, 1, 0, 1]

    # Adds color to the list, and determines whether to let user continue input, or to stop the game
    def addToUserColorList(self, color, *largs):
        self.userColorList.append(color)

        # If the user hasn't inputted enough colors, make sure their current input is correct, otherwise its game over
        if len(self.simon.colorList) > len(self.userColorList):
            if self.simon.colorList[0:len(self.userColorList)] == self.userColorList:
                return
            else:
                self.popupWinner = Popup(title="Game Over", content=Label(text="Incorrect Order!"), size_hint=(0.50, 0.50))
                self.popupWinner.open()
                return
        # If the user has inputted enough colors, check the userColors again the gameColors
        else:
            # If the user is correct, flash green, return the buttons to normal colors, add a color to list,
            # display current list, and await user input
            if self.simon.isCorrect(self.userColorList):
                self.displayCorrect()
                time.sleep(3)
                self.reAdjustColors()
                self.simon.addColor()
                self.displayOrder()
                self.userInput()
            else:
                self.popupWinner = Popup(title="Game Over", content=Label(text="Incorrect Order!"), size_hint=(0.50, 0.50))
                self.popupWinner.open()

    # Used to return buttons to normal colors after flashing green
    def reAdjustColors(self):
        for i in range(len(self.buttonList)):
            if i == 0:
                self.buttonList[0].background_color = [0, 1, 0, 0.20]
            elif i == 1:
                self.buttonList[1].background_color = [1, 0, 0, 0.20]
            elif i == 2:
                self.buttonList[2].background_color = [255, 255, 0, 0.20]
            elif i == 3:
                self.buttonList[3].background_color = [0, 0, 1, 0.20]

    # Enabled all buttons to enable input
    def userInput(self):
        self.buttonList[0].background_color = [0, 1, 0, 1]
        self.buttonList[0].disabled = False
        self.buttonList[1].background_color = [1, 0, 0, 1]
        self.buttonList[1].disabled = False
        self.buttonList[2].background_color = [255, 255, 0, 1]
        self.buttonList[2].disabled = False
        self.buttonList[3].background_color = [0, 0, 1, 1]
        self.buttonList[3].disabled = False

    # Iterates through gameColors, and displays each color in that order
    def displayOrder(self):
        print("displaying order of buttons")
        order = self.simon.colorList
        for i in range(len(order)):
            if order[i] == "G":
                #self.buttonList[0].background_color = [0, 1, 0, 1]
                time.sleep(3)
                self.buttonList[0].background_color = [255, 255, 255, 1]
                time.sleep(3)
                self.buttonList[0].background_color = [0, 1, 0, 0.20]
            elif order[i] == "R":
                time.sleep(3)
                #self.buttonList[1].background_color = [1, 0, 0, 1]
                self.buttonList[0].background_color = [255, 255, 255, 1]
                time.sleep(3)
                self.buttonList[1].background_color = [1, 0, 0, 0.20]
            elif order[i] == "Y":
                time.sleep(3)
                #self.buttonList[2].background_color = [255, 255, 0, 1]
                self.buttonList[0].background_color = [255, 255, 255, 1]
                time.sleep(3)
                self.buttonList[2].background_color = [255, 255, 0, 0.20]
            elif order[i] == "B":
                time.sleep(3)
                #self.buttonList[3].background_color = [0, 0, 1, 1]
                self.buttonList[0].background_color = [255, 255, 255, 1]
                time.sleep(3)
                self.buttonList[3].background_color = [0, 0, 1, 0.20]

class ConnectFourWidget(BoxLayout):
    def __init__(self, *largs,**kwargs):
        super(ConnectFourWidget, self).__init__(**kwargs)

        self.orientation = 'horizontal'
        self.spacing = 7

        # Create exit button for the pop up
        self.exitButton = Button(text="Exit", halign='right', valign='center')
        self.resetButton = Button(text="Reset", halign='right', valign='center', on_press=self.resetGame)

        # Create ConnectFour object, and list to hold the placement buttons
        self.connectFour = ConnectFour()
        self.btnList = []

        # Create buttons for each column, and place them in list
        for i in range(7):
            self.btnList.append(Button(text=str(i+1), halign='right', valign='top', on_press=partial(self.playerMoveHelper, i)))

        # Create containers for the connect four game layout
        self.boardContainer = BoxLayout(orientation='vertical', spacing=5, size_hint=(0.90, 1))
        self.topContainer = BoxLayout(orientation='horizontal', spacing=1, size_hint=(1, 0.10))
        self.rowsContainer = BoxLayout(orientation='vertical', spacing=1, size_hint=(1, 0.90))
        self.sideContainer = BoxLayout(orientation='vertical', spacing=10, size_hint=(0.10, 1))

        # Add each button in the list to the topContainer
        for button in self.btnList:
            self.topContainer.add_widget(button)

        # containerList will hold the rows of buttons, boardButtonList is a 2d list of all gameButtons
        self.containerList = []
        self.boardButtonList = []

        # Add labels to rows in rowsContainer
        for row in range(6):
            self.containerList.append(BoxLayout(orientation='horizontal', spacing=1))
            self.tempList = []
            for col in range(7):
                temp = Button(halign='right', valign='top', disabled=True)
                self.containerList[row].add_widget(temp)
                self.tempList.append(temp)
            self.boardButtonList.append(self.tempList)

        # Add all the container rows to the row container
        for container in self.containerList:
            self.rowsContainer.add_widget(container)

        # Determine which color to make the control buttons
        if self.connectFour.whoseTurn() == 1:
            for button in self.btnList:
                button.background_color = [0, 0, 1, 1]
        else:
            for button in self.btnList:
                button.background_color = [1, 0, 0, 1]

        # Add all of the containers and buttons
        self.boardContainer.add_widget(self.topContainer)
        self.boardContainer.add_widget(self.rowsContainer)
        self.sideContainer.add_widget(self.exitButton)
        self.sideContainer.add_widget(self.resetButton)
        self.add_widget(self.sideContainer)
        self.add_widget(self.boardContainer)

    # Function called by resetButton, resets all game boards and button colors for a new game
    def resetGame(self, *largs):
        for row in range(6):
            for col in range(7):
                self.boardButtonList[row][col].background_color = [169, 169, 169]

        self.connectFour.reset()

        for button in self.btnList:
            button.disabled = False
            if self.connectFour.whoseTurn() == 1:
                button.background_color = [0, 0, 1, 1]
            else:
                button.background_color = [1, 0, 0, 1]

    # Helper function for connectFour's playerMove() function
    def playerMoveHelper(self, col, *largs):

        # When pressing a control button, if it is the last button in the col, disable the respective control btn
        if self.connectFour.getSpotState(1, col) != 0:
            self.btnList[col].disabled = True
            self.btnList[col].background_color = [0, 0, 0, 1]

        x, y = self.connectFour.playerMove(col, self.connectFour.whoseTurn())

        self.checkWinner(col)
        self.buttonControl(x, y)

    # Disable all the control buttons (for use after a player wins)
    def disableControlButtons(self):
        for button in self.btnList:
            button.disabled = True

    # Determine who won, and display a popUp
    def checkWinner(self, col):
        if self.connectFour.isWinner(col, self.connectFour.recentState):
            if self.connectFour.recentState == 1:
                self.popupWinner = Popup(title="Game Over", content=Label(text="Blue player wins!!"), size_hint=(0.50, 0.50))
                self.popupWinner.open()
                self.disableControlButtons()
            else:
                self.popupWinner = Popup(title="Game Over", content=Label(text="Red player wins!!"), size_hint=(0.50, 0.50))
                self.popupWinner.open()
                self.disableControlButtons()

    # Determine which buttons to disable and change color of
    def buttonControl(self, x, y):
        if self.connectFour.whoseTurn() == 1:
            self.boardButtonList[x][y].background_color = [1, 0, 0, 1]
            for button in self.btnList:
                if not button.disabled:
                    button.background_color = [0, 0, 1, 1]
        else:
            self.boardButtonList[x][y].background_color = [0, 0, 1, 1]
            for button in self.btnList:
                if not button.disabled:
                    button.background_color = [1, 0, 0, 1]

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
        self.gameButton = Button(text="Games", halign='center', valign='center')
        self.quotaButton = Button(text="View Quota", halign='center', valign='center')
        self.exitButton = Button(text="Exit", halign='center', valign='center')

        # Configure buttons
        self.quotaButton.bind(on_press=self.openQuotaWidget)
        self.exitButton.bind(on_press=quitProg)
        self.gameButton.bind(on_press=self.openGamesWidget)

        # Add widgets to view
        self.add_widget(self.brightnessWidgets)
        self.add_widget(self.quotaButton)
        self.add_widget(self.gameButton)
        self.add_widget(self.exitButton)

    def openGamesWidget(self, *largs):
        self.gameWidget = GamesWidget()

        self.popup = Popup(title="Games Selection", content=self.gameWidget)
        self.gameWidget.closeButton.bind(on_press=self.popup.dismiss)
        self.popup.open()

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

def quitProg(*largs):
    workingDir = str(subprocess.check_output('pwd'))[2:-3]
    subprocess.call(['rm', '%s/dailyQuota.png' % workingDir, '%s/weeklyQuota.png' % workingDir])
    quit()

# Start the program
if __name__ == "__main__":
    subprocess.call(['sudo', 'chmod', '666', '/sys/class/backlight/rpi_backlight/brightness'])

    # We need to keep a reference to the PiDay object so it is not garbage collected
    # If the object is garbage collected then the schedule calls will not work
    app = PiDay()
    app.run()
