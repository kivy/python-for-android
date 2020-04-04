print('importing numpy')
import numpy as np
print('imported numpy')

print('importing matplotlib')

import matplotlib
print('imported matplotlib')

print('importing pyplot')

from matplotlib import pyplot as plt

print('imported pyplot')

fig, ax = plt.subplots()

print('created fig and ax')

ax.plot(np.random.random(50))

print('plotted something')

ax.set_xlabel('test label')

print('set a label')

fig.set_size_inches((5, 4))
fig.savefig('test.png')

print('saved fig')

from kivy.app import App
from kivy.base import runTouchApp
from kivy.uix.image import Image
from kivy.lang import Builder

class MatplotlibApp(App):
    def build(self):
        root = Builder.load_string("""
BoxLayout:
    orientation: 'vertical'
    Image:
        id: the_image
        source: 'test.png'
        allow_stretch: True
    Button:
        size_hint_y: None
        height: dp(40)
        text: 'new plot'
        on_release: app.generate_new_plot()
        """)
        return root
        
    def generate_new_plot(self):
        fig, ax = plt.subplots()
        ax.set_xlabel('test xlabel')
        ax.set_ylabel('test ylabel')
        ax.plot(np.random.random(50))
        ax.plot(np.sin(np.linspace(0, 3*np.pi, 30)))

        ax.legend(['random numbers', 'sin'])

        fig.set_size_inches((5, 4))
        fig.tight_layout()

        fig.savefig('test.png', dpi=150)

        self.root.ids.the_image.reload()
        



MatplotlibApp().run()
runTouchApp(Image(source='test.png', allow_stretch=True))
