# coding:shift-JIS
# pylint: disable=F0401

from scipy import optimize
import pymel.core as pm
import sys

myfanc_path = ["C:/Users/piedp/OneDrive/Labo/Sketch/Script/BlendLap/myfanc",
               "C:/Users/piedp/OneDrive/Labo/Sketch/Script/BlendLap",
               "C:/Users/piedp/OneDrive/Labo/Sketch/Script/BlendLap/myfanc/kensaku"]
for path in myfanc_path :
    if not path in sys.path :
        sys.path.append( path )

import tools
reload (tools)
import curvetool
reload (curvetool)


def func(x,*args) :
    for i in range(len(x)):
        while(1):
            if(x[i] < 0) :
                print " aaaa" , x[i]
                x[i] += 1
            elif(x[i] > max) :
                x[i] -= 1
            else : break
    print x
    
    pos_list = curvetool.getCurvePoint(args[0], x, pinModes = "normal", debug = False)
    tools.makeSphere(pos_list = pos_list)
    return 1 - (pos_list[0] - pos_list[1]).length()



cur = pm.PyNode("courveshow")
args = (cur)
x0 = [0.95,0.5]

pp = optimize.minimize(func,x0, args, "Nelder-Mead", options = {"maxiter" : 200})
print pp
print "ans : ",pp["x"]

#tools.deltemp()

