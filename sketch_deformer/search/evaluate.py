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
        p,      # ���[���h���W
        c,      # �J�����ʒu(���[���h)
        scr,    # �X�N���[�����S
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


# ����AB�Ɛ���CD�̌�_�����߂�֐�
def calc_cross_point(pointA, pointB, pointC, pointD):
    cross_points = (0,0)
    bunbo = (pointB[0] - pointA[0]) * (pointD[1] - pointC[1]) - (pointB[1] - pointA[1]) * (pointD[0] - pointC[0])

    # ���������s�ȏꍇ
    if (bunbo == 0):
        return False, cross_points

    vectorAC = ((pointC[0] - pointA[0]), (pointC[1] - pointA[1]))
    r = ((pointD[1] - pointC[1]) * vectorAC[0] - (pointD[0] - pointC[0]) * vectorAC[1]) / bunbo
    s = ((pointB[1] - pointA[1]) * vectorAC[0] - (pointB[0] - pointA[0]) * vectorAC[1]) / bunbo

    # ����AB�A����AC��ɑ��݂��Ȃ��ꍇ
    if (r <= 0) or (1 <= r) or (s <= 0) or (1 <= s):
        return False, cross_points

    # r���g�����v�Z�̏ꍇ
    distance = ((pointB[0] - pointA[0]) * r, (pointB[1] - pointA[1]) * r)
    cross_points = ((pointA[0] + distance[0]), (pointA[1] + distance[1]))

    # s���g�����v�Z�̏ꍇ
    # distance = ((pointD[0] - pointC[0]) * s, (pointD[1] - pointC[1]) * s)
    # cross_points = (int(pointC[0] + distance[0]), int(pointC[1] + distance[1]))

    return True, cross_points
# ------------------------------------------------------------------------------------



# ���̃A���O���ŁC�X�P�b�`�̃}�[�W���t���o�E���f�B�𐶐����āC���̒��Ō덷������s���D
# ��������񎟌��ɓ��e���āC�ʐς��v�Z�D
# ��̕��[�v�ɂ��āC�h�ǂ��炩����݂̂̓����h�ɂ���_�̐��𐔂���D
# ��������F�_����x�����ɕ�����L�΂��C�����񐔂���Ȃ�����D(�ڂ���ꍇ�̓~�X��)
def diff_2D(line1, line2, **kwargs) :
    width = kwargs.get('width', 2048)
    height = kwargs.get("height", 2048)

    debug = kwargs.get("debug", False)

    # line�̈ʒu�̍ő�(+-)
    x_max = kwargs.get('x_max', 10)
    y_max = kwargs.get('y_max', 10)

    if debug : print line1

    # �X�P�b�`�̃o�E���f�B�����߂�
    corner1 = line1[0]
    corner2 = line1[0]
    for p in line1 :
        corner1 = [min(p[0],corner1[0]), min(p[1],corner1[1])]
        corner2 = [max(p[0],corner2[0]), max(p[1],corner2[1])]
    
    margin = 3
    corner1 = [corner1[0]-margin,corner1[1]-margin]
    corner2 = [corner2[0]+margin,corner2[1]+margin]

    
    # ���C�����X�P�[�����O
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

    # �摜�o�͗p�ɏ����o��
    path = 'C:/Users/piedp/Documents/Resources/image/face/differ.json'
    json_file = open(path, 'w')
    dic = {}
    dic["pix"]     = pix
    dic["width"]   = width
    dic["height"]  = height
    json.dump(dic, json_file)
    json_file.close() 
                

    #print " "
    return S, float(S)/float(width*height)*100.  # �덷�̎��l�ƑS�̂ɑ΂��銄��(��)



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

    return dif, percent  # �덷�̎��l�ƑS�̂ɑ΂��銄��(��)
