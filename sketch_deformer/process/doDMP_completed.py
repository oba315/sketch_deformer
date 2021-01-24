# coding:shift-JIS
# pylint: disable=F0401

import pymel.core as pm  
import sys
import numpy as np
import json
import time


from ..tool import tools
reload (tools)
from . import doDMP_constraint
reload (doDMP_constraint)
from ..tool import my_face
reload (my_face)
from ..tool import curvetool
reload (curvetool) 


"""
mefaceに格納されたインデックスから，その間の頂点を補完してDMPを実行
"""


# --- 頂点とパラメータを補完 -------------------------------------------------------
def complete_pin(myface, **kwargs) :
    pinId_befor = kwargs.get( "pinIndex", myface.parts_vertex[myface.context_parts] )
    param_befor = kwargs.get( "params",   myface.param_list)

    pinId       = []      # 補完された頂点番号
    params      = []         # 補完されたカーブ上の位置パラメータ

    for i, p in enumerate( pinId_befor ) :
        
        # indexを更新
        p2    =  pinId_befor[i+1] if i != len(pinId_befor)-1 else pinId_befor[0]
        path  =  tools.path_search( myface.obj, int(p), int(p2) )
        pinId.extend(path[0][:-1])
        
        # params を更新
        param1 = param_befor[i]
        param2 = param_befor[i+1] if i != len(pinId_befor)-1 else param_befor[0]
        if param2 < param1 : param2+=1
        param_comp = [ param1 + (param2 - param1)*l for l in path[1] ]
        #print param1, "/", param2,"/",param_comp
        
        params.extend( param_comp[:-1] )
        
    for i in range(len(params)) :
        while params[i] > 1 :
            params[i] -= 1
    return pinId, params
# ----------------------------------------------------------------------------------

    

# ---- 頂点を補完してDMPを行う． --------------------------------------------------
def do(myface, pinMode, **kwargs) :
    applyBlendShape = kwargs.get( "applyBlednShape", True ) * \
                      kwargs.get( "ap", True)

    print u" --- 頂点を補完してDMPを行います ---"
    
    # ---------必要なデータ -----------------------------------------
    alpha = myface.alpha
 
    # ピンを補完

    pinId_comp, params_comp = complete_pin(myface)

    print "pin    : ", pinId_comp
    print "params : ", params_comp
    print len(pinId_comp), len(params_comp) 
    # --------------------------------------------------------------

    # ------ カーブ上の点を計算 ------------------------------------
    curPosList_comp = curvetool.getCurvePoint(myface.curve, params_comp, pinMode)
    
    # -------- DMPを計算 -------------------------------------------
    start = time.time()
    print u"\n - - - do_DMP  - - - \nalpha = ", alpha 
    w = doDMP_constraint.do_dmp(    myface,curPosList_comp, 
                                    alpha, 0.,1.,
                                    pinIndex = pinId_comp,
                                    ap = applyBlendShape     )
    # --------------------------------------------------------------
    
    # 一致度を算出
    #print "Bw-m : ", tools.calc_bwm(myface, pinIndexList_comp, curPosList_comp)

    print u"[time]  ", time.time() - start
    return w
# -----------------------------------------------------------------------------------
