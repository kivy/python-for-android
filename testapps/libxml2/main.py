from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.uix.popup import Popup

import libxml2


Builder.load_string('''
<PopupScreen>:
    orientation: 'vertical'
    Button:
        text: "Show Story"
        on_press: root.detail()
        size_hint_y: None
        height: '40dp'
    Label:
        id: head
        font_size: 30
        size_hint_y: None
        height: '50dp'
    ScrollView:
        Label:
            id: str_doc
            font_size: 20
            text_size: self.width, None
            size_hint_y: None
            height: self.texture_size[1]
''')


class PopupScreen(BoxLayout):

    def detail(self):
        DOC = """<?xml version="1.0" encoding="UTF-8"?>

        <verse>

          <attribution>Christopher Okibgo</attribution>

          <line>For he was a shrub among the poplars,</line>

          <line>Needing more roots</line>

          <line>More sap to grow to sunlight,</line>

          <line>Thirsting for sunlight</line>

        </verse>

        """

        doc = libxml2.parseDoc(DOC)

        root = doc.children

        # print root
        lbl = self.ids.str_doc
        head = self.ids.head

        head.text = "Here is the string version of the children of doc"

        lbl.text = str(root)
        doc.freeDoc()


class MovieApp(App):
    def build(self):
        return PopupScreen()

MovieApp().run()