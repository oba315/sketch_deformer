# coding:shift-JIS
# pylint: disable=F0401

import pymel.core as pm
import maya.api.OpenMaya as om2
import sys
import numpy as np
import json

import my_face
reload (my_face)
import tools
reload (tools)
import curvetool
reload (curvetool)


def projection_2D(
        p,      # ワールド座標
        c,      # カメラ位置(ワールド)
        scr,    # スクリーン中心
        scr_x,
        scr_y):
    
    k = ( (scr-c)*(scr-c) ) / ( (p-c)*(scr-c) )
    proj = k*(p-c) + c
    v = proj - scr
    alpha = v*scr_x
    beta  = v*scr_y
    
    #w = p[2]/10 + 1
    #alpha = p[0]/w
    #beta = p[1]/w
    return [alpha, beta]


# 線分ABと線分CDの交点を求める関数
def calc_cross_point(pointA, pointB, pointC, pointD):
    cross_points = (0,0)
    bunbo = (pointB[0] - pointA[0]) * (pointD[1] - pointC[1]) - (pointB[1] - pointA[1]) * (pointD[0] - pointC[0])

    # 直線が平行な場合
    if (bunbo == 0):
        return False, cross_points

    vectorAC = ((pointC[0] - pointA[0]), (pointC[1] - pointA[1]))
    r = ((pointD[1] - pointC[1]) * vectorAC[0] - (pointD[0] - pointC[0]) * vectorAC[1]) / bunbo
    s = ((pointB[1] - pointA[1]) * vectorAC[0] - (pointB[0] - pointA[0]) * vectorAC[1]) / bunbo

    # 線分AB、線分AC上に存在しない場合
    if (r <= 0) or (1 <= r) or (s <= 0) or (1 <= s):
        return False, cross_points

    # rを使った計算の場合
    distance = ((pointB[0] - pointA[0]) * r, (pointB[1] - pointA[1]) * r)
    cross_points = ((pointA[0] + distance[0]), (pointA[1] + distance[1]))

    # sを使った計算の場合
    # distance = ((pointD[0] - pointC[0]) * s, (pointD[1] - pointC[1]) * s)
    # cross_points = (int(pointC[0] + distance[0]), int(pointC[1] + distance[1]))

    return True, cross_points
# ------------------------------------------------------------------------------------



# そのアングルで，スケッチのマージン付きバウンディを生成して，その中で誤差判定を行う．
# いったん二次元に投影して，面積を計算．
# 二つの閉ループについて，”どちらか一方のみの内部”にいる点の数を数える．
# 内部判定：点からx方向に閉直線を伸ばし，交差回数が奇数なら内部．(接する場合はミスる)
def diff_2D(line1, line2, **kwargs) :
    width = kwargs.get('width', 2048)
    height = kwargs.get("height", 2048)

    debug = kwargs.get("debug", False)

    # lineの位置の最大(+-)
    x_max = kwargs.get('x_max', 10)
    y_max = kwargs.get('y_max', 10)

    if debug : print line1

    # スケッチのバウンディを求める
    corner1 = line1[0]
    corner2 = line1[0]
    for p in line1 :
        corner1 = [min(p[0],corner1[0]), min(p[1],corner1[1])]
        corner2 = [max(p[0],corner2[0]), max(p[1],corner2[1])]
    
    margin = 3
    corner1 = [corner1[0]-margin,corner1[1]-margin]
    corner2 = [corner2[0]+margin,corner2[1]+margin]

    
    # ラインをスケーリング
    for p in line1 :
        for i in range(2) :
            p[i] = (p[i]-corner1[i]) / (corner2[i]-corner1[i]) * height
    for p in line2 :
        for i in range(2) :
            p[i] = (p[i]-corner1[i]) / (corner2[i]-corner1[i]) * height
    
    
    S = 0
    pix = []

    for j in range(height):
        start = [0., j+0.5]
        end   = [float(width), j+0.5]

        cross_x_1 = []
        cross_x_2 = []
        for ii, v in enumerate( line1 ) :
            v2 = line1[ii+1] if ii != (len(line1)-1) else line1[0]
            cp = calc_cross_point(start, end, v, v2)
            if cp[0] :
                cross_x_1.append(cp[1][0])

        for ii, v in enumerate( line2 ) :
            v2 = line2[ii+1] if ii != (len(line2)-1) else line2[0]
            cp = calc_cross_point(start, end, v, v2)
            if cp[0] :
                cross_x_2.append(cp[1][0])

        #if cross_x_1 != [] : print  j, cross_x_1
        #if cross_x_2 != [] : print  j, cross_x_2
        

        for i in range(width) :
            inside1 = False
            inside2 = False
            for x in cross_x_1 :
                if x > i :
                    inside1 = not inside1
            for x in cross_x_2 :
                if x > i :
                    inside2 = not inside2

            if inside1 ^ inside2 :
                S += 1
                pix.append(1)
            else : pix.append(0)

        if debug and j%50 == 0 : print j, " ",

    # 画像出力用に書き出し
    path = 'C:/Users/piedp/Documents/Resources/image/face/differ.json'
    json_file = open(path, 'w')
    dic = {}
    dic["pix"]     = pix
    dic["width"]   = width
    dic["height"]  = height
    json.dump(dic, json_file)
    json_file.close() 
                

    #print " "
    return S, float(S)/float(width*height)*100.  # 誤差の実値と全体に対する割合(％)



def do_diff_2D(myface) :
    distance = 100

    #p = pm.pointPosition()
    #camName   =  tools.getCamFromModelPanel()
    cam       =  pm.PyNode("persp")
    c = pm.getAttr(cam.translate)

    pm.move(cam, -1,0,0,r = 1, os = 1, wd = 1)
    moved = pm.getAttr(cam.translate)
    pm.move(cam, 1,0,0,r = 1, os = 1, wd = 1)
    scr_x = moved - c

    pm.move(cam, 0,-1,0,r = 1, os = 1, wd = 1)
    moved = pm.getAttr(cam.translate)
    pm.move(cam, 0,1,0,r = 1, os = 1, wd = 1)
    scr_y = moved - c

    scr_z = scr_x.cross(scr_y)
    scr = c - (distance*scr_z)
    #print "axis " , scr_x, scr_y


    line1_3D = [pm.pointPosition(i) for i in myface.curve.cv]
    line1_2D = [projection_2D(i,c,scr,scr_x,scr_y) for i in line1_3D]

    pins = myface.parts_vertex["mouth"]
    pinss, params = tools.complete_pinIndenList(myface,pins)
    line2_3D = [pm.pointPosition(myface.obj.vtx[i]) for i in pinss]
    line2_2D = [projection_2D(i,c,scr,scr_x,scr_y) for i in line2_3D]

    #print "line1(",len(line1_2D),") ", line1_2D
    #print "line2(",len(line2_2D),") ", line2_2D

    dif, percent =  diff_2D(line1_2D,line2_2D)

    return dif, percent  # 誤差の実値と全体に対する割合(％)
