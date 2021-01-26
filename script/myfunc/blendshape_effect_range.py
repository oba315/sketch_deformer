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

"""
頂点に対して，ブレンドシェイプの影響範囲を頂点カラーで示す
とりあえず，独立したスクリプトとして記述．
"""
myface = my_face.MyFace()


    
def set_color(myface, color) :

    start = time.time()
    pm.polyColorPerVertex(myface.obj, rgb=[0,0,0])
    print "time : ", time.time() - start 
    for i, v in enumerate( myface.obj.vtx ) :
        if color[i] != 0 :
            # ----- 0-1 を HSV(H:0.66-0 S:1 V:1) に変換 ---------
            h = 0.66 *(1 - color[i])
            command = "hsv_to_rgb <<" + str(h) + ",1,1>>;"
            #print command
            rgb = pm.mel.eval(command)    
            pm.polyColorPerVertex(v, rgb=(rgb), cdo = 1 )
        
    print "time : ", time.time() - start 

# 頂点ごとのブレンドシェイプベクトルの相関を見る
def serch_effect_range(myface, vindex) :
    jsonPath = myface.mesh_data_path
    with open(jsonPath,"r") as json_file:

        data  = json.load(json_file)

        nv    = len(data["base"]["vtx"])    # 頂点数
        nb     =  len(data["target"])      # ブレンドシェイプの数
        ni    = len(vindex)                 # 調べる頂点の数

        
        BT = np.zeros((nv,nb*3))
        for i in range(nv) :
            BT_v =np.zeros(nb*3)
            for j in range(nb) :
                for p in range(3) :
                    BT_v[j*3 + p] = data["target"][j][i][p]
            BT[i] = BT_v

        print (BT.shape)

        effect_range = np.zeros((ni,nv))    # 比較対象頂点ｘ全頂点
        for j, BT_v in enumerate( BT ) :
            for i, v in enumerate(vindex) :
                effect_range[i][j] = np.corrcoef( BT[v], BT_v )[0][1]   # 相関係数

        # 相関係数0.8以上のものを採用
        threshold = 0.8
        effect_range_cutoff = np.zeros((ni,nv))
        for i,ran in enumerate(effect_range) :
            for j,value in enumerate(ran) :
                if value > threshold :
                    effect_range_cutoff[i][j] = (value - threshold) / (1 - threshold)
                else :
                    effect_range_cutoff[i][j] = 0
        

        print effect_range_cutoff

        return effect_range_cutoff


# 一つの頂点で出力
set_color(myface, serch_effect_range(myface,[2834])[0] )

# 複数の頂点で出力


vindexLst = myface.parts_vertex[myface.context_parts]
vindexLst = [3654,4040,4038,4037,4044,4039,3659,3658,2863,3214,3218,3212,3213,3215,2862,2857,2858,2845,2846,3217,3216,4042,4041,4043,3638, 3637, 3650,3649,3654]
n = len(vindexLst)

soukan = serch_effect_range(myface,vindexLst)

color = []

# 平均を出力
for i in range(len(soukan[0])) :
    average = 0
    for j in range(len(vindexLst)) :
        average += soukan[j][i]
    # average /= n   
    color.append(average)

    #average *= 2
    

"""
# 掛け算を出力
for i in range(len(soukan[0])) :
    average = 1
    for j in range(len(vindexLst)) :
        average *= (1 - soukan[j][i])
    color.append((1-average) ** 4)
"""


# 閾値を設定
threshold_value = 3
for i, c in enumerate(color) :
    if c > threshold_value:
        color[i] = 1
    else :
        color[i] = 0


set_color(myface, color)


