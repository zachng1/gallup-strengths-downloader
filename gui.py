from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from tkinter import scrolledtext
from gallup import *
from pathlib import Path
import threading

def main(attendeecsv, dlpath, output, username, password):
	lock = threading.Lock()
	def exit():
		global run
		with lock:
			run.config(state=NORMAL)

	if str(dlpath) == "Select...":
		messagebox.showerror(message="Please select a download path")
		exit()
		return	
	try:
		attendees = get_attendees(attendeecsv)
	except:
		messagebox.showerror(message="Could not read .csv")
		exit()
		return

	scrollprint("Connecting to Gallup.com. This will take up to a few minutes...\nGo make a cup of tea!\n")
	browser = load_browser(dlpath)
	try:
		browser.get("https://www.gallupstrengthscenter.com/sign-in/en-us/index")
	except:
		messagebox.showerror(message="Could not connect to Gallup.com, try again")
		browser.quit()
		exit()
		return
	try:	
		login(browser, username, password)
	except:
		messagebox.showerror(message="Incorrect Username or Password")
		browser.quit()
		exit()
		return

	#incase Gallup gets stuck on "Submit this form" page
	try:
		WebDriverWait(browser, 10).until(expected.title_is("Gallup | Analytics and Tools to Transform Your Workplace - GSS - Portal"))
	except:
			browser.refresh()

	try:
		menu = WebDriverWait(browser, 20).until(expected.element_to_be_clickable((By.ID, "btc-sidenav")))
	except:
		messagebox.showerror(message="Could not connect to menu, try again")
		browser.quit()
		exit()
		return
	else:
		menu.click()

	try:
		strengths = WebDriverWait(browser, 20).until(expected.element_to_be_clickable((By.CSS_SELECTOR, ".c-sidenav__section:nth-child(2) a")))
	except:
		messagebox.showerror(message="Could not connect to strengths, try again")
		browser.quit()
		exit()
		return
	else:
		strengths.send_keys(Keys.RETURN)


	try:
		community = WebDriverWait(browser, 20).until(expected.element_to_be_clickable((By.LINK_TEXT, "Community")))
	except:
		messagebox.showerror(message="Could not connect to community, try again")
		browser.quit()
		exit()
		return
	else:
		community.send_keys(Keys.RETURN)
		
	#grid for storing strengths, to be copied to template later (don't have time to learn python -> excel stuff, or even python -> indesign stuff)
	grid = open(dlpath / "Team Grid.csv", 'w')	
	grid.write("name,1,2,3,4,5\n")

	scrollprint("Connected!\n")
	download_all(browser, attendees, grid, dlpath, output)
	scrollprint("Finished.")
	grid.close()
	browser.quit()
	exit()

def open_file_csv():
	file = filedialog.askopenfilename(parent=root, filetypes=[("Comma Separated Values", "*.csv")])
	if file:
		return file
	else:
		return "Select..."
		
def open_dir():
	directory = filedialog.askdirectory(parent=root)
	if directory:
		return directory
	else:
		return "Select..."

def scrollprint(text):
	global output
	output.configure(state=NORMAL)
	output.insert(INSERT, text)
	output.configure(state=DISABLED)
	output.see(END)

class ScrolledTextFileIO(scrolledtext.ScrolledText):
	def write(self, text):
		self.configure(state=NORMAL)
		self.insert(INSERT, text)
		self.configure(state=DISABLED)
		self.see(END)

def run_main(attendeecsv, dlpath, output, username, password):
	run.config(state=DISABLED)
	x = threading.Thread(target=main, args=(attendeecsv, dlpath, output, username, password))
	x.start()

if __name__ == "__main__":
	root = Tk()
	root.title("Gallup Strengths Downloader")
	root.geometry("500x500")

	attendee_file, report_directory = StringVar(), StringVar() 
	attendee_file.set("Select...")
	report_directory.set("Select...")
	instructions = Label(root, bg="gold", relief=RIDGE, text="*****IMPORTANT*****\nPlease make sure Firefox is installed on your PC.\nPlease make sure Dropbox Sync is PAUSED if downloading to a Dropbox folder.")
	instructions.pack()

	login_top_container = Frame(root, relief=RIDGE)
	login_top_container.pack()
	login_container = Frame(login_top_container, relief=RIDGE)
	login_container.pack(side=LEFT)
	login_box_container = Frame(login_top_container, relief=RIDGE)
	login_box_container.pack(side=LEFT)
	username = Entry(login_box_container)
	username_l = Label(login_container, text="Username")
	password = Entry(login_box_container)
	password_l = Label(login_container, text="Password")
	username.pack()
	password.pack()
	username_l.pack()
	password_l.pack()

	attendee_select = Label(root, text="Select the .csv file of people who have taken the assessment (Downloaded from Gallup)")
	attendee_select.pack()
	open_attendees = Button(root, textvariable=attendee_file, command=lambda: attendee_file.set(open_file_csv()))
	open_attendees.pack()
	save_label = Label(root, text="Choose the directory to save reports to")
	save_label.pack()
	save_button = Button(root, textvariable=report_directory, command=lambda: report_directory.set(open_dir()))
	save_button.pack()
	run_label = Label(root, text="Download -- This might take a while")
	run_label.pack()
	output = ScrolledTextFileIO(root, width=50, height=15, state=DISABLED)
	output.pack(side=BOTTOM)
	run = Button(root)
	run.config(text="Download", command=lambda: run_main(attendee_file.get(), Path(report_directory.get()), output, username.get(), password.get()))
	run.pack()
	

	#write output to gui window instead of console
	stderr_ = sys.stderr
	stdout_ = sys.stdout
	sys.stdout = output
	sys.stderr = output
	root.mainloop()

	sys.stdout = stdout_
	sys.stderr = stderr_