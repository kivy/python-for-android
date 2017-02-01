from kivy.app import App
from kivy.uix.button import Button 
from kivy.uix.textinput import TextInput 
from kivy.uix.label import Label 
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivy.uix.image import AsyncImage 

import requests
from bs4 import BeautifulSoup 

Builder.load_string(
'''
<PopupScreen>:
	orientation: 'vertical'
	Label:
		text: "Enter Your movie name buddy"
	TextInput:
		id: name
		font_size: 40
		multiline: False
	Button:
		text: "show details"
		on_press: root.detail(name.text)

''')
global writer
writer = "Writers:"
global actor
actor = "Actors:"
global director
director = "Directors:"
class PopupScreen(BoxLayout):
	def error(self):
		popup = Popup(title="ERROR",content=Label(text="Bro, Check your movie name"),size_hint=(0.8,0.8))
		popup.open()

	def Pop(self,movie,imdb,actor,director,writer,url):
		wid1 = GridLayout(cols=2,rows=1)
		lb = AsyncImage(source=url)
		wid1.add_widget(lb)
		wid2 = GridLayout(rows=4)
		lb = Label(text=imdb)
		wid2.add_widget(lb)
		
		lb = Label(text=actor)
		wid2.add_widget(lb)
		lb = Label(text=director)
		wid2.add_widget(lb)
		lb = Label(text=writer)
		wid2.add_widget(lb)

		wid1.add_widget(wid2)		
		popup = Popup(title=movie,content=wid1,size_hint=(0.8,0.8))
		popup.open()

	def detail(self, title):

		global writer
		writer = "Writers:"
		global actor
		actor = "Actors:"
		global director
		director = "Directors:"

		s="+".join(title.split())


		f_url = 'http://www.imdb.com/find?q='
		url=f_url+s+'&s=all'
		try:
			var = requests.get(url)
			soup = BeautifulSoup(var.content)

			x = soup.find("td", {"class": "result_text"})
			m = x.find("a")['href']
				
			new_url = 'http://www.imdb.com' + m 
			content = requests.get(new_url)
			soup = BeautifulSoup(content.content)

			img = soup.find("div", {"class":"poster"})
			url = img.findChildren()[1]['src']

			x = soup.find("div", {"class": "title_wrapper"})
			
			c = x.findChildren()[0]
			
			movie = c.text 

			c = soup.find("div", {"class":"ratingValue"})
			
			imdb = c.text 


			
			for tag in soup.find_all("span", {"itemprop":"director"}):
				
				
				director += tag.text 

			
			for tag in soup.find_all("span", {"itemprop":"creator"}):
			
				writer += tag.text


			
			for tag in soup.find_all("span", {"itemprop":"actors"}):
			
				actor += tag.text 
				
				

			self.Pop(movie,imdb,actor,director,writer,url)

		except Exception:
			
			self.error()

	
class MovieApp(App):
	def build(self):
		return PopupScreen()

MovieApp().run()