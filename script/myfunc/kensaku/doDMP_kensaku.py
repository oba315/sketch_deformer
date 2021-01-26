# coding:shift-JIS
# pylint: disable=F0401

import pymel.core as pm
import sys
import json
import numpy as np
import cvxopt
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
import doDMP_constraint
reload (doDMP_constraint)


"""
ピンを等間隔で配置し，その始点の位置をカーブ上をスライドして全通り試すことで，
もっとも所望に近くなるような形状を検索．

メモ：
w^2で検索する場合
    ウエイトに制限をかけて行った場合，うまく最適な位置を選ばない
    場合がある．
    ウエイトに制限をかけないで検索した場合，おおむね良好
Bw-mで検索する場合．
    重いが概ね良好
"""

"""
条件：カーブ検索は時計周り

"""


# 解像度の分だけ始点を変えて計算を行い，必要な数値を書き出す．
def repeat_dmp(myface, sample = 8) :
    
    # ピンの数
    n = len(myface.parts_vertex[myface.context_parts])
    
    # 検索の解像度
    starting_point = [ i * (1. / sample) for i in range(sample)]

    cost = []
    w2   = []
    count = 0
    bwm = []
    for st in starting_point :
        
        # 検索するパラメータ
        params = [( st+(float(i)/n) ) - int( st+(float(i)/n) ) for i in range(n)]
        print "params", params
        curPosList =  curvetool.getCurvePoint(myface.curve, params, "normal")
        
        calc = doDMP_constraint.do_dmp(myface, curPosList, ap = False, smi = True)
        

        cost.append(calc["cost"])
        w2.append(calc["w^2"])
        bwm.append(calc["Bw-m"])
        #pm.refresh()

        count += 1
        print count 

    ret = {}
    ret["sample"] = sample
    ret["cost"]   = cost
    ret["w2"]     = w2
    ret["Bw-m"]   = bwm

    tools.deltemp("tempvec")

    print ret["Bw-m"]
    return ret
        

#　最終的に適切なIDでdmpを実行する．
def do_dmp_with_id(myface, sample, id):
    # ピンの数
    n = len(myface.parts_vertex[myface.context_parts])
    starting_point = float(id) / float(sample)
    
    # 検索するパラメータ
    params = []
    for i in range(n) :
        param = starting_point + (float(i)/n)
        param = param - int(param)
        params.append(param)
    print "params", params
    
    curPosList =  curvetool.getCurvePoint(myface.curve, params, "normal")
    calc = doDMP_constraint.do_dmp(myface, curPosList, ap = True)
    
    # 得られたウエイトでblendshapeを設定
    for i, weight in enumerate(myface.blender.w):
        pm.setAttr(weight,calc["w"][i])

    tools.deltemp("tempvec")



"""
# Bw-mがもっとも小さいブレンドシェイプを適用する．
cal = repeat_dmp(myface, 30)
id = cal["Bw-m"].index(min(cal["Bw-m"]))
print id
do_dmp_with_id(myface, 30, id)
"""