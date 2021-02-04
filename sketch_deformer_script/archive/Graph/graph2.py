from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
import matplotlib.pyplot as plt
import numpy as np
import sys
import json


def json_import(path) :
    
    json_file    = open(path, 'r')
    data         = json.load(json_file)
    json_file.close()
    
    return data
    

lst =  json_import('C:/Users/piedp/Documents/Resources/image/face/differ.json')
print lst

x = np.arange(0, 30, 1)
y = np.arange(0, 30, 1)

X, Y = np.meshgrid(x, y)
Z = np.array(lst)
print Z.shape
print "--"

fig = plt.figure()
ax = Axes3D(fig)

ax.set_xlabel("x")
ax.set_ylabel("y")
ax.set_zlabel("f(x, y)")

ax.plot_wireframe(X, Y, Z)
ax.plot_surface(X, Y, Z, rstride=1, cstride=1, cmap=cm.coolwarm, vmin = 0, vmax = 10)
plt.show()