# coding:shift-JIS
# pylint: disable=F0401

import pymel.core as pm
import sys
import json
import numpy as np
import time

myfanc_path = ["C:/Users/piedp/OneDrive/Labo/Sketch/Script/BlendLap/myfanc",
               "C:/Users/piedp/OneDrive/Labo/Sketch/Script/BlendLap"]
for path in myfanc_path :
    if not path in sys.path :
        sys.path.append( path )

import my_face
reload (my_face)
import tools
reload (tools)
import curvetool
reload (curvetool)
import limitLap
reload (limitLap)
import doDMP_completed
reload (doDMP_completed)
import doDMP_constraint
reload (doDMP_constraint)
import difference
reload (difference)

"""
口角の位置をユーザーが指定して，上下中心を検索する．
"""


def preview_point(myface, param, view=True) :
    tools.deltemp("temp_preview_point")
    params = param if type(param)==list else [param]
    points  = curvetool.getCurvePoint(myface.curve, params, "normal")
    for i in range(len(params)) : print "param : ", params[i], "/", points[i]
    if view :
        for p in points :
            tools.makeSphere(p, 0.5, "temp_preview_point")
    return points

# -----------------------------------------------------------------------------------
# リストを与えられた範囲で正規化
def list_normalize(target, myrange=[0,1]) :
    d         = myrange[1] - myrange[0]
    target_d  = float(max(target) - min(target))
    nom = [ d * (i-min(target))/target_d + myrange[0] for i in target ]
    return(nom)
# -----------------------------------------------------------------------------------


def dmp_with_corner( 
            myface, 
            corner = [-1,-1],       # 口角の位置
            um = 0.5,               # 上部の中心
            lm = 0.5,               # 下部の中心
            ap = True,               # 変形を適用するかどうか
            log = True
            ) :

    c0 = corner[0]
    c1 = corner[1]

    if log : preview_point(myface,[c0,c1], True)
    if log : print "corner ::" , [c0,c1]

    # ピンの数
    nu = 5  # 両端を含む，上唇のピンの数
    nl = 5  # 両端を含む，下唇のピンの数
    
    
    index = myface.parts_vertex[myface.context_parts]
    
    upper_index = index[:nu]
    lower_index = index[-(nl-1):]
    lower_index.append(index[0])

    # 長さで配置せず，myface内のparamを使用
    params = myface.param_list
    upper_params = list_normalize(params[:5])
    lower_params = params[-4:]
    lower_params.append(params[0]+1)
    lower_params = list_normalize(lower_params)
    
    # 口角のparam，中心のparam(0-1)からカーブ上の位置を指定．
    # 二次関数で補完(修正前の中心位置のパラメータを0.5とする．) 
    # 時計回りの前提
    
    # 上下それぞれを0-1に配置
    # 上唇
    if nu%2 == 0 :
        print "ERROR : 頂点数が偶数です．"
    else :
        temp = []
        for i in upper_params :
            if i >= 0.5 :
                temp.append(i*um/0.5)
            else :
                temp.append( ((1-um)/0.5)*i + (um-0.5)/0.5 ) 
        upper_params = temp
    # 下唇
    if nl%2 == 0 :
        print "ERROR : 頂点数が偶数です．"
    else :
        temp = []
        for i in lower_params :
            if i >= 0.5 :
                temp.append(i*lm/0.5)
            else :
                temp.append( ((1-lm)/0.5)*i + (lm-0.5)/0.5 ) 
        lower_params = temp

    if log : print "upper_params", upper_params
    if log : print "lower_params", lower_params
    
    # 指定した口角の範囲で上下を結合
    if c1 < c0 : c1 += 1
    params = list_normalize(upper_params, [c0,c1])[:-1]
    c0 += 1
    params.extend( list_normalize(lower_params, [c1,c0])[:-1] )

    # １を超えたものを編集
    params = [i- int(i) for i in params]
    
    
    if log : print "params : ", params
    
    pinID_comp, params_comp = doDMP_completed.complete_pin(myface, params=params)
    curPosList_comp = curvetool.getCurvePoint(myface.curve, params_comp, "normal")
    doDMP_constraint.do_dmp( myface,
                             curPosList_comp,
                             pinIndex = pinID_comp, 
                             ap = ap,
                             )

    tools.deltemp("tempvec")

    return params

# ---------------------------------------------------------------------


def repeat(myface, corner = [0,0.5], sampling = 10) :

    print corner

    diff = [[None for _ in range(sampling)] for _ in range(sampling)]

    sp = [i / float(sampling) for i in range(sampling)]
    print sp
    for ii, i in enumerate(sp) :
        for jj, j in enumerate(sp) :
            params =  dmp_with_corner(myface, corner, um = i, lm = j, ap = True, log = False)
            #pm.refresh()
            #time.sleep(1) 
            print [ii,jj]
            # 誤差評価
            #diff[ii][jj] = difference.diff_3D(myface)
            #diff[ii][jj] = difference.diff_3D_max(myface)
            #diff[ii][jj] = difference.do_diff_2D(myface)
            diff[ii][jj] = difference.dist(myface, param_list=params)
            print "distance : ", diff[ii][jj]
            
    

    # 最適化
    d_min = 10000
    min_index = [-1,-1]
    for i,d in enumerate(diff) :
        for j,dd in enumerate(d) :
            if dd < d_min : 
                d_min = dd
                min_index = [i,j]

    print "min_index, ", min_index
    p = dmp_with_corner(myface, corner, um = sp[min_index[0]], lm = sp[min_index[1]], ap = True)

    return p
    

"""

calc = repeat_dmp(myface,30)
do_dmp_from_bwm(myface, 30,calc["diff3D"])

#do_dmp_from_bwm(myface, 30,calc["diff3D"], [1,13])

tools.json_export(calc["diff3D"], "C:\Users\piedp\OneDrive\Labo\Sketch\Script\BlendLap\Graph\image.test.json")

"""

#prev_p = myface.param_list
myface.param_list = prev_p
#new_p = dmp_with_corner(myface,[0.0,0.65], um = 0.5, lm = 0.5)
new_p = repeat(myface,[0,0.65], 10)


myface.param_list = new_p


