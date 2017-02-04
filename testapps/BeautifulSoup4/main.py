from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.uix.popup import Popup

import requests
from bs4 import BeautifulSoup

Builder.load_string('''
<PopupScreen>:
    orientation: 'vertical'
    Button:
        text: "Show Story"
        on_press: root.detail()
        size_hint_y: None
        height: '40dp'
    Label:
        id: title
        font_size: 30
        size_hint_y: None
        height: '50dp'
    ScrollView:
        Label:
            id: story  
            font_size: 20
            text_size: self.width, None
            size_hint_y: None
            height: self.texture_size[1]
''')


class PopupScreen(BoxLayout):
    def error(self):
        popup = Popup(title="ERROR",
            content=Label(text="Check Your Network Connection"),
            size_hint=(0.8, 0.8))
        popup.open()

    def detail(self):

        f_url = 'https://httpbin.org/html'
        title = self.ids.title
        story = self.ids.story
        try:
            var = requests.get(f_url)

            soup = BeautifulSoup(var.content)

            title_find = soup.find("h1")
            story_find = soup.find("p")

            for x in title_find:
                title.text = x
            for x in story_find:
                story.text = x

        except Exception:
            self.error()


class MovieApp(App):
    def build(self):
        return PopupScreen()

MovieApp().run()