# coding:shift-JIS
# pylint: disable=F0401

# 制限なしブレンドシェイプ

import pymel.core as pm  
import sys
import numpy as np
import json
import time


from ..tool import tools
reload (tools)

from ..tool import my_face
reload (my_face)
from ..tool import curvetool
reload (curvetool)
from . import doDMP_constraint
reload(doDMP_constraint)
from . import limitLap
reload(limitLap)


def do(myface) :

    curPosall = []
    pinIDall  = []


    for partname in myface.parts_vertex :
        curvename = myface.projection_curve_name + "_" + partname
        if pm.objExists(curvename) :
            print "aaaaaaaaaaaaaa", curvename
            cur = pm.PyNode(curvename)
            # パラメータは使いまわし
            curPosall  += curvetool.getCurvePoint(cur, myface.param_list)
            pinIDall   += myface.parts_vertex[partname]

    doDMP_constraint.do_dmp( myface,
                        curPosall,
                        pinIndex = pinIDall, 
                        ap = True,
                        alpha= 0.5,
                        )

def lap(myface, area=8) :
    # ------- ブレンドシェイプをフリーズ ----------
    tools.freeze_blend_shape(
                    myface.obj, 
                    myface.blender, 
                    myface.defaultShape)  # 重い
    # --------------------------------------------
    
    # パラメータは使い回し
    params = myface.param_list

    for partname in myface.parts_vertex :
        curvename = myface.projection_curve_name + "_" + partname
        if pm.objExists(curvename) :
            cur = pm.PyNode(curvename)

            pinID = myface.parts_vertex[partname]

            # --------- ピンを補完 -----------------------
            pinID_comp, params_comp = tools.complete_pinIndenList(myface,pinID,params)
            curpos_comp = curvetool.getCurvePoint(cur,  params_comp, "curvature")

            # --------- ラプラシアンエディットを実行 -------
            limitLap.do_lap_limit(
                    myface,
                    pinID_comp,
                    area, 
                    curpos_comp, 
                    debug=False
                    )

    

