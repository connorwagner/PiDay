import tkinter as tk
import time
import json
import urllib.request
import operator
from datetime import datetime, timedelta

import schedule
from pyicloud import PyiCloudService

from config import getUsername, getPassword, getStocks, getWeatherLocale, getCalendarExceptions

# Create custom class to manage presentation
class CustomPanedWindow(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.configure(bg='#242329')
        self.panes = []

    def add(self, widget, weight=1):
        # Add a pane with the given weight
        self.panes.append({"widget": widget, "weight": weight})
        self.layout()

    def layout(self):
        # Delete all current children
        for child in self.place_slaves():
            child.place_forget()

        total_weight = sum([pane["weight"] for pane in self.panes])
        relx= 0

        for i, pane in enumerate(self.panes):
            relwidth = pane["weight"]/float(total_weight)
            # Note: relative and absolute heights are additive; thus, for 
            # something like 'relheight=.5, height=-1`, that means it's half
            # the height of its parent, minus one pixel. 
            if i == 0:
                pane["widget"].place(x=0, y=0, relheight=1.0, relwidth=relwidth)
            else:
                pane["widget"].place(relx=relx, y=0, relheight=1.0, relwidth=relwidth, 
                                     width=-2, x=2)
            relx = relx + relwidth


class PiDay(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

        # Log in to iCloud API session and set up calendar control sessions
        self.icloudApi = PyiCloudService(getUsername(), getPassword())
        self.days = ['U','M','T','W','R','F','S']
        self.dayAdjustment = int(time.strftime("%w"))
        self.selectedDay = tk.IntVar()

        # Initialize presentation manager
        paned = CustomPanedWindow(self)
        paned.pack(side="top", fill="both", expand=True)

        # Create panes to use in presentation manager
        self.firstPane = tk.Frame(self, width=200, height=200, bg='#302F37')
        self.calendarFrame = tk.Frame(self, width=200, height=200, bg='#302F37')
        self.daySelectionFrame = tk.Frame(self, width=200, height=200, bg='#302F37')

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

        # Add panes to presentation manager
        paned.add(self.firstPane, 3)
        paned.add(self.calendarFrame, 10)
        paned.add(self.daySelectionFrame, 1)

    def getTimeWidget(self):
        # Create a frame to contain the time and date labels in so that they are seen as one item when the presentation manager spaces the widgets
        group = tk.LabelFrame(self.firstPane, borderwidth='0', bg='#302F37', fg='#45A9F5')
        self.timeLabel = tk.Label(group, text="TIME", wraplength="150", justify=tk.CENTER, font=('times new roman', 24, 'bold'), bg='#302F37', fg='#45A9F5')
        self.timeLabel.pack(fill=tk.BOTH, expand=True)
        self.dateLabel = tk.Label(group, text="DATE", wraplength="150", justify=tk.CENTER, font=('times new roman', 14, 'bold'), bg='#302F37', fg='#45A9F5')
        self.dateLabel.pack(fill=tk.BOTH, expand=True)
        group.pack(fill=tk.X, expand=True)

        # Update data on widget
        self.updateTimeWidget()

    def updateTimeWidget(self):
        # Update text on both time and date widgets to reflect new time/date
        self.timeLabel.configure(text=time.strftime("%-I:%M %p"))
        self.dateLabel.configure(text=time.strftime("%B %-d"))

        # Start timer to update data in 1 second
        self.after(1000, self.updateTimeWidget)

    def getQuoteWidget(self):
        # Create a label to display the quote on
        self.quoteLabel = tk.Label(self.firstPane, text="JOKE", wraplength="150", justify=tk.CENTER, bg='#302F37', fg='#45A9F5')
        self.quoteLabel.pack(fill=tk.BOTH, expand=True)

        # Update widget to display joke
        self.updateQuoteWidget()

    def updateQuoteWidget(self):
        # Get new quote from API and change label text to reflect it
        # Possibly change to http://tambal.azurewebsites.net/joke/random
        joke = self.makeHTTPRequest("http://ron-swanson-quotes.herokuapp.com/v2/quotes")
        joke = joke[1:-1] + "\n–Ron Swanson"
        self.quoteLabel.configure(text=joke)

    def getWeatherWidget(self):
        # Create a label to display the weather
        self.weatherLabel = tk.Label(self.firstPane, text="WEATHER", wraplength="150", justify=tk.CENTER, bg='#302F37', fg='#45A9F5')
        self.weatherLabel.pack(fill=tk.BOTH, expand=True)

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
        self.weatherLabel.configure(text=weatherText)

        # Start 30 minute timer to update weather again
        self.weatherRecursiveCall = self.after(900000, self.updateWeatherWidget)

    def getStocksWidget(self):
        # Create a label to display stocks data
        self.stocksLabel = tk.Label(self.firstPane, text="STOCKS", wraplength="150", justify=tk.CENTER, bg='#302F37', fg='#45A9F5')
        self.stocksLabel.pack(fill=tk.BOTH, expand=True)

        # Update data on widget
        self.updateStocksWidget()

    def updateStocksWidget(self):
        # Get list of stocks desired from config file
        stocksList = getStocks()
        pricesStr = str()
        for stock in stocksList:
            # Get price for desired stock and add it to the string for the label
            price = self.makeHTTPRequest('http://finance.yahoo.com/d/quotes.csv?s=' + stock + '&f=l1')
            pricesStr += "%s: $%.2f\n" % (stock, float(price))
        # Remove trailing newline character
        pricesStr = pricesStr[:-1]
        # Update text on label
        self.stocksLabel.configure(text=pricesStr)

        # Start timer to update after 15 minutes
        self.stocksRecursiveCall = self.after(600000, self.updateStocksWidget)

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
                daysDiff = (datetime.strptime(str(event['startDate'][0]), dateFormat) - datetime.strptime(today, dateFormat)).days
                # Try statement needed because the API hands back a list of the next 7 days with events so if the current day has no events then it will hand back too many days and the number of days' difference will be 7, exceeding the length of our list
                try:
                    self.daySeparatedEventList[daysDiff].append(event)
                except:
                    pass
        # Sort each list of events by start time
        for listOfEvents in self.daySeparatedEventList:
            listOfEvents.sort(key=operator.itemgetter('startDate'))

        # Update widget to reflect new data
        self.getCalendarWidget()

        # Set timer to update after 30 minutes
        self.calendarRecursiveCall = self.after(1800000, self.getCalendarData)

    def getCalendarWidget(self):
        # Destroy all current children
        for child in self.calendarFrame.winfo_children():
            child.destroy()

        # Loop through all events on the selected day and add them to the widget as individual labels so they are spaced nicely by the presentation manager
        eventsOnSelectedDay = self.daySeparatedEventList[self.selectedDay.get()]
        for event in eventsOnSelectedDay:
            # Sanitize edge cases
            startHour = event['startDate'][4]
            startHourAmPm = "AM"
            if startHour >= 12:
                startHour -= 12
                startHourAmPm = "PM"
            if startHour == 0:
                startHour = 12
            endHour = event['endDate'][4]
            endHourAmPm = "AM"
            if endHour >= 12:
                endHour -= 12
                endHourAmPm = "PM"
            if endHour == 0:
                endHour = 12
            # Create string to display
            detailStr = "%s: %i:%02i %s to %i:%02i %s at %s" % (event['title'], startHour, event['startDate'][5], startHourAmPm, endHour, event['endDate'][5], endHourAmPm, event['location'])
            # If there is no location then remove the end of the string ("… at …")
            if event['location'] == None:
                detailStr = detailStr[:-8]
            # Create a label to show data
            lbl = tk.Label(self.calendarFrame, text=detailStr, wraplength="1000", justify=tk.CENTER, bg='#302F37', fg='#45A9F5')
            lbl.pack(fill=tk.BOTH, expand=True)

        # If there are no events on this day then display a message instead of leaving the space blank
        if len(eventsOnSelectedDay) == 0:
            # Create a label to show message
            lbl = tk.Label(self.calendarFrame, text="There are no scheduled events on this day", wraplength="1000", justify=tk.CENTER, bg='#302F37', fg='#45A9F5')
            lbl.pack(fill=tk.BOTH, expand=True)

    def getDaySelectionWidget(self):
        # Destroy all current children
        for child in self.daySelectionFrame.winfo_children():
            child.destroy()
        # Add new buttons in the proper order
        for i in range(7):
            btn = tk.Radiobutton(self.daySelectionFrame, text=self.days[(i + self.dayAdjustment) % len(self.days)], variable=self.selectedDay, value=i, command=self.dayChanged, indicatoron=False, borderwidth='0', selectcolor='#242329', activeforeground='#45A9F5', bg='#302F37', fg='#45A9F5')
            btn.pack(fill=tk.BOTH, expand=True)

    def updateWidgetsAtMidnight(self):
        # Update day ajuster and adjust day selection back one if necessary to maintain selected calendar day upon day change
        self.dayAdjustment = int(time.strftime("%w"))
        if self.selectedDay.get() > 0:
            self.selectedDay.set(self.selectedDay.get() - 1)

        # Update quote and day selection widgets
        self.updateQuoteWidget()
        self.getDaySelectionWidget()

        # Cancel the recursive call that already existed to avoid duplicate calls and then call it again (for all below)
        self.after_cancel(self.calendarRecursiveCall)
        self.getCalendarData()

        self.after_cancel(self.weatherRecursiveCall)
        self.updateWeatherWidget()

        self.after_cancel(self.stocksRecursiveCall)
        self.updateStocksWidget()

        self.after_cancel(self.midnightRecursiveCall)
        self.after(86400000, self.updateWidgetsAtMidnight)

    def dayChanged(self):
        # Update calendar display to show new data
        self.getCalendarWidget()

    def makeHTTPRequest(self, url):
        r = urllib.request.urlopen(url)
        response = r.read().decode('utf-8')
        r.close()
        return response

if __name__ == "__main__":
    root = tk.Tk()
    PiDay(root).pack(fill=tk.BOTH, expand=True)
    root.geometry("800x480")
    root.configure(cursor='none')
    root.attributes("-fullscreen", True)
    root.title("PiDay")
    root.mainloop()

# Blue color: #45A9F5
# Background grey/black color: #302F37
# Dard background color: #242329
