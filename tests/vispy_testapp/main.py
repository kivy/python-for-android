"""
Demonstration of Tube
"""

print('testing!')
import ctypes
print('imported ctypes')
print(ctypes.__dict__)
print('dict done')
import ctypes.util
print('imported util')
print(ctypes.util.find_library)

import vispy
# vispy.set_log_level('debug')

import sys
from vispy import scene
from vispy.geometry.torusknot import TorusKnot

from colorsys import hsv_to_rgb
import numpy as np

canvas = scene.SceneCanvas(keys='interactive', bgcolor='white')
canvas.unfreeze()
canvas.view = canvas.central_widget.add_view()

points1 = TorusKnot(5, 3).first_component[:-1]
points1[:, 0] -= 20.
points1[:, 2] -= 15.

points2 = points1.copy()
points2[:, 2] += 30.

points3 = points1.copy()
points3[:, 0] += 41.
points3[:, 2] += 30

points4 = points1.copy()
points4[:, 0] += 41.

colors = np.linspace(0, 1, len(points1))
colors = np.array([hsv_to_rgb(c, 1, 1) for c in colors])

vertex_colors = np.random.random(8 * len(points1))
vertex_colors = np.array([hsv_to_rgb(c, 1, 1) for c in vertex_colors])

l1 = scene.visuals.Tube(points1,
                        shading='flat',
                        color=colors,  # this is overridden by
                                       # the vertex_colors argument
                        vertex_colors=vertex_colors,
                        tube_points=8)

l2 = scene.visuals.Tube(points2,
                        color=['red', 'green', 'blue'],
                        shading='smooth',
                        tube_points=8)

l3 = scene.visuals.Tube(points3,
                        color=colors,
                        shading='flat',
                        tube_points=8,
                        closed=True)

l4 = scene.visuals.Tube(points4,
                        color=colors,
                        shading='flat',
                        tube_points=8,
                        mode='lines')

canvas.view.add(l1)
canvas.view.add(l2)
canvas.view.add(l3)
canvas.view.add(l4)
canvas.view.camera = scene.TurntableCamera()
# tube does not expose its limits yet
canvas.view.camera.set_range((-20, 20), (-20, 20), (-20, 20))
canvas.show()

if __name__ == '__main__':
    if sys.flags.interactive != 1:
        canvas.app.run()
