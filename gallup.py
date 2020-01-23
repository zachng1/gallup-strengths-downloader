from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as expected
from selenium.webdriver.support.wait import WebDriverWait
from pathlib import Path
from time import sleep
import sys
import os


cwd = Path.cwd()


def download_all(browser, attendees, grid, dlpath, output):
	for email, name in attendees:
		grid.write(name + ',')
		search(browser, "%s" % email, grid)
		sleep(2)
		#if dl fails, try again up to 5 times
		counter = 0
		while True:
			counter += 1
			sleep(2)
			if not (dlpath / ("%s.pdf" % name)).exists():
				try:
					list(dlpath.glob("signature-theme*.pdf"))[0].rename(dlpath / ("%s.pdf" % name))
				except:
					if counter < 6:
						download(browser, output, name, dlpath)
						#make sure we don't try rename before firefox has successfully downloaded file
						for i in dlpath.iterdir():
							if i.match("*.part"):
								sleep(5)
					else:
						print("Could not download %s\n" % name)
						break
				else:
					print("Success\n")
					break
			else:
				print("%s's top 5 report already exists in this folder\n" % name)
				break		

def login(browser, username, password):
	stitle = browser.title
	user = browser.find_element_by_name("Username")
	passw = browser.find_element_by_name("Password")
	user.clear()
	passw.clear()
	user.send_keys(username) 
	passw.send_keys(password) 
	#sometimes ENTER doesn't work and it gets stuck -- will send until page changes.
	while browser.title == stitle:
		passw.send_keys(Keys.RETURN)
		sleep(5)
		if browser.title == stitle:
			try:
				browser.find_element_by_css_selector(".alert-box.alert-box--error")
			except:
				continue
			else:
				raise
		else:
			break
		

def gallupslow(browser, link_text):	#necessary because gallup takes ages to load links and Selenium kept throwing " Element could not be scrolled into view error"
	link = WebDriverWait(browser, 20).until(expected.element_to_be_clickable((By.LINK_TEXT, link_text)))
	link.click()

def search(browser, name, grid):
	search = browser.find_element_by_name("SearchText")
	search.clear()
	search.send_keys(name)
	search.send_keys(Keys.RETURN)
	strengths = WebDriverWait(browser, 10).until(expected.presence_of_element_located((By.CSS_SELECTOR, "ol.c-team-cards__strengths")))
	#write to team grid.csv
	strengths = strengths.find_elements_by_tag_name("li")
	for i in strengths:
		grid.write(i.text + ',')
	grid.write('\n')
	menu = browser.find_element_by_class_name("dropdown-bubble")
	menu.click()
	
def download(browser, output, name, dlpath): #assumes you have already searched a name and are on Gallup community page -- assumes f is open as csv for team grid
	print("Trying to download %s" % name)
	gallupslow(browser, "Signature Theme Report")
	sleep(5)
	browser.switch_to.window(browser.window_handles[1])
	#wait until successful download before closing window
	while not list(dlpath.glob("signature-theme*.pdf")):
		sleep(2)
	browser.close()
	browser.switch_to.window(browser.window_handles[0])

#get names and emails from .csv, downloaded from code management page
def get_attendees(source):
	f = open(source, 'r')
	names = []
	emails = []
	f.readline()
	for i in f:
		li = i.split(',')
		names.append(li[0])
		emails.append(li[2])
	f.close()
	return zip(emails, names)

def load_browser(dlpath):
	options = Options()
	options.add_argument('-headless')
	ffp = webdriver.FirefoxProfile(cwd / "library/profile")
	#have to use str() here instead of Path object, selenium wasn't playing nice
	ffp.set_preference("browser.download.dir", str(dlpath))
	browser = webdriver.Firefox(firefox_profile = ffp, executable_path=cwd / "library/geckodriver-v0.26.0-win64/geckodriver.exe", options=options)
	browser.set_page_load_timeout(60)
	return browser

