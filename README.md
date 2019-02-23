# homer
This repository contains the homer application designed to run on a Raspberry Pi 2/3 with the 7" touchscreen under Python 2.7.

It should run on a standard Linux desktop.

---
### Obtain repository:
If you're reading this, chances are you already have some access to it.

&nbsp;&nbsp;&nbsp;&nbsp;`cd ~/<project-dir>/`  
&nbsp;&nbsp;&nbsp;&nbsp;`git clone --recursive https://<github-user>@github.com/delaneymorgan/homer.git`

---
### Auto-Start:
A systemd service is provided for use with Raspbian.  Assuming you have installed homer under /home/pi/project/homer, this should run as is.  Modify as required.

&nbsp;&nbsp;&nbsp;&nbsp;`cd /lib/systemd/system/`  
&nbsp;&nbsp;&nbsp;&nbsp;`sudo ln -s ~/project/homer/homer.service homer.service`  

---
### Packages required:
* ???? - ?????

---
### Modules required:
* configparser - .ini file parsing module
* pyping - provides network ping service

&nbsp;&nbsp;&nbsp;&nbsp;`sudo pip install configparser`  
&nbsp;&nbsp;&nbsp;&nbsp;`sudo pip install kivy`  
&nbsp;&nbsp;&nbsp;&nbsp;`sudo pip install rpi_backlight`  
&nbsp;&nbsp;&nbsp;&nbsp;`sudo pip install pyowm`  
&nbsp;&nbsp;&nbsp;&nbsp;`sudo pip install untangle`  

---
### Usage:
You will need to create a manifest of all monitored & managed devices in your setup.  This is kept in manfest.json.  You will then need to modify config.ini to specify which devices are managed, and which are simply monitored.

-v option can be supplied to enable the (rather limited) console logging.

Most useful parameters can be set via the config.ini file.

---
