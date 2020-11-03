# Program to create a calculator 
	
# Program to Show how to create a switch 
# import kivy module	 
import kivy 
	
# base Class of your App inherits from the App class.	 
# app:always refers to the instance of your application 
from kivy.app import App 
	
# this restrict the kivy version i.e 
# below this kivy version you cannot 
# use the app or software 
kivy.require('1.9.0') 

# for making multiple bttons to arranging 
# them we are using this 
from kivy.uix.gridlayout import GridLayout 

# for the size of window 
from kivy.config import Config 

# Setting size to resizable 
Config.set('graphics', 'resizable', 1) 
## Config.set('graphics', 'width', '400') 
## Config.set('graphics', 'height', '400') 


# Creating Layout class 
class CalcGridLayout(GridLayout): 

	# Function called when equals is pressed 
	def calculate(self, calculation): 
		if calculation: 
			try: 
				# Solve formula and display it in entry 
				# which is pointed at by display 
				self.display.text = str(eval(calculation)) 
			except Exception: 
				self.display.text = "Error"

# Creating App class 
class CalculatorApp(App): 

	def build(self): 
		return CalcGridLayout() 

# creating object and running it 
calcApp = CalculatorApp() 
calcApp.run() 





#calculator.ky file code:


# Custom button 
<CustButton@Button>: 
	font_size: 32

# Define id so I can refer to the CalcGridLayout 
# class functions 
# Display points to the entry widget 
<CalcGridLayout>: 
	id: calculator 
	display: entry 
	rows: 6
	padding: 10
	spacing: 10

	

	# Where input is displayed 
	BoxLayout: 
		TextInput: 
			id: entry 
			font_size: 32
			multiline: False

	# When buttons are pressed update the entry 
	BoxLayout: 
		spacing: 10
		CustButton: 
			text: "7"
			on_press: entry.text += self.text 
		CustButton: 
			text: "8"
			on_press: entry.text += self.text 
		CustButton: 
			text: "9"
			on_press: entry.text += self.text 
		CustButton: 
			text: "+"
			on_press: entry.text += self.text 

	BoxLayout: 
		spacing: 10
		CustButton: 
			text: "4"
			on_press: entry.text += self.text 
		CustButton: 
			text: "5"
			on_press: entry.text += self.text 
		CustButton: 
			text: "6"
			on_press: entry.text += self.text 
		CustButton: 
			text: "-"
			on_press: entry.text += self.text 

	BoxLayout: 
		spacing: 10
		CustButton: 
			text: "1"
			on_press: entry.text += self.text 
		CustButton: 
			text: "2"
			on_press: entry.text += self.text 
		CustButton: 
			text: "3"
			on_press: entry.text += self.text 
		CustButton: 
			text: "*"
			on_press: entry.text += self.text 

	# When equals is pressed pass text in the entry 
	# to the calculate function 
	BoxLayout: 
		spacing: 10
		CustButton: 
			text: "AC"
			on_press: entry.text = "" 
		CustButton: 
			text: "0"
			on_press: entry.text += self.text 
		CustButton: 
			text: "="
			on_press: calculator.calculate(entry.text) 
		CustButton: 
			text: "/"
			on_press: entry.text += self.text 
	BoxLayout: 
		CustButton: 
			font_size: 20
			text: "Scientific calculator"
			on_press: entry.text = ""		 
