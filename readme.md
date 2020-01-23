# Gallup Downloader
A simple download tool which 1. downloads a team's reports, and 2. recreates the team grid functionality removed by Gallup in their latest website overhaul. 
## Getting Started
### Prerequisites
You will need Python 3.x, which you can download here: https://www.python.org/downloads/

You will also need the Selenium package, which you can install by following these instructions: https://selenium-python.readthedocs.io/installation.html

You will also need an installation of Firefox: https://www.mozilla.org/en-US/firefox/new/
### Running
Simply download the entire repository and then run gui.py with python.
## Usage
The downloader requires that you first download a 'used-codes.csv' file for the team whose strengths you need from Gallup.com. This is accessed under code management. Then choose the team you want, then under the used codes tab, choose export codes to file.

Once you have done this, simply run gui.py with Python, enter your username and password, select the 'used-codes.csv', and finally the folder where you want the reports downloaded to. Click download. The program will automatically fetch the reports of your team and generate a team grid with each members strengths.