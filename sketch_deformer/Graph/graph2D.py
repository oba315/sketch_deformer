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
    

lst =  json_import("C:\\Users\\piedp\\OneDrive\\Labo\\Sketch\\Script\\BlendLap\\Graph\\image.test.json")
print lst

y = np.array(lst[0])
x = np.arange(0, len(y))

print "--"

plt.title("Exponential function to the base 4")
plt.xlabel("x")
plt.ylabel("y")

# グラフを描画
plt.plot(x, y) #破線のグラフを書く
plt.show()