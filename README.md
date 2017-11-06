# PiDay

## There are really only a few things to know about this application; I will keep this document as short as possible.

1. Install the pyicloud and schedule modules
	* `pip3 install pyicloud`
	* `pip3 install schedule`
	* `sudo apt install -y python-pip build-essential git python python-dev ffmpeg libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev zlib1g-dev`
    * `sudo apt install -y python3-kivy`
2. All necessary modifications will be made within config.py
	* `getUsername` should be modified to return your iCloud login email
	* `getPassword` should be modified to return your iCloud login password
	* `getStocks` should be modified to be a list containing all the stocks you are interested in tracking
	* `getWeatherLocale` should be modified to fit the format of "City,ST,CN", where ST is the two letter designation for your state or territory and CN is the two letter designation for your country (make sure there are no spaces)
	* `getCalendarExceptions` will probably not require any modification, but in the case that you do want to exclude some calendars from your application you can add a string containing that calendar's pGuid value to the list
3. Run `PiDay.pyw` as a Python application
