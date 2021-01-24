# coding:shift-JIS
# pylint: disable=F0401

import pymel.core as pm
import maya.api.OpenMaya as om2
import sys
import numpy as np
import json

from ..tool import my_face
reload (my_face)
from ..tool import tools
reload (tools)
from ..tool import curvetool
reload (curvetool)

"""
���݂̌`��ƁC�J�[�u�Ƃ̍����v�Z����֐��Q
"""


# �P���ɑΉ��_�ł̈ʒu���r
def diff_pos(myface, pinIndexList = -1, vpos = -1, params = -1, curpos = -1, debug=False) :

    cp = curpos
    dsum = 0
    for i, v in enumerate(vpos) :
        dvt = [v[j] - cp[i][j] for j in range(3)]
        d = dvt[0]**2 + dvt[1]**2 + dvt[2]**2
        dsum += d
        if debug :
            tools.maketext(t = d,name="_"+str(i)+":temptext", p = v, s = 0.1)
    return dsum

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



def diff_pos2d(myface, pinIndexList = -1, vpos = -1, params = -1, curpos = -1, debug=False, cam_info=None) :

    cp2d = [projection_2D([cp[0],cp[1],cp[2]], cam_info[1], cam_info[2], cam_info[3], cam_info[4]) for cp in curpos]
    vp2d = [projection_2D([cp[0],cp[1],cp[2]], cam_info[1], cam_info[2], cam_info[3], cam_info[4]) for cp in vpos]
    

    if len(curpos) != len(vpos) : print "ERROR"
    dsum = 0
    for i in range(len(curpos)) :
        dx = cp2d[i][0]-vp2d[i][0]
        dy = cp2d[i][1]-vp2d[i][1]

        dist = dx**2 + dy**2

        #dist = dist *(100/abs(angle_cur[i]))   # �d�݂Â�

        dsum += dist

    return dsum




# ���̊e�_���琂�ʂ�L�΂��C��ԋ߂��_��Ή��Ƃ���
# ��荇�����C�J�[�u�𕪊����Ă��ꂼ��̃Z�O�����e�[�V�����Ɛ��ʂƂ̌���������Ƃ�D
# kwards:: pinIndex
def diff_3D(myface, pinIndexList = -1, pos = -1, **kwargs) :

    cur      = myface.curve
    sampling = kwargs.get("sampling", 30)
    
    if type(pinIndexList) is int : 
        pinIndexList = kwargs.get( "pinIndex", myface.parts_vertex[myface.context_parts] )
    n = len(pinIndexList)

    if type(pos) is int :
        pmpoints = [pm.pointPosition(myface.obj.vtx[i]) for i in pinIndexList]
    else : 
        pmpoints = pos
    
    points = []
    for i in pmpoints :
        points.append(om2.MPoint(i[0], i[1], i[2]))

    #tools.makeSphere(pos_list=pos, name = "temp_rhis!")
    
    dist_sum = 0
    for i, p in enumerate(points) :
        
        pbef = points[-1] if i == 0   else points[i-1]
        pnex = points[0]  if i == n-1 else points[i+1]

        v1 = (pbef - p).normal()
        v2 = (pnex - p).normal()
        
        va = (v1 + v2).normal()
        vb = v1 ^ v2
        vn = va ^ vb

        #tools.makeVector(vn, p, "VN")

        dist_cache = -1
        # �J�[�u�̊e�Z�O�ƌ�������C�߂����̂��̗p�D
        for j in range(sampling) :

            end = curvetool.getCurvePoint(cur, [j/float(sampling), (j+1)/float(sampling)], "normal")

            en0 = (end[0]-p)*vn
            en1 = (end[1]-p)*vn 
            if en0 * en1 <= 0 :
                ip = end[0] - (end[1]-end[0])*( en0 / (en1-en0) )
                dist = (ip - p).length()
                
                if dist_cache == -1 or dist <= dist_cache :
                    dist_cache = dist
                    #crspt = ip

        if dist_cache == -1 : 
            print (u"ERROR ��_��������܂���")
            #return -1
        else:
            dist_sum += dist_cache
        #tools.makeVector(crspt - p, p, "XtoP")

    
    #print "difference : ", dist_sum / n 
    return dist_sum / n


# ---------------------------------------------------------------------


def diff_3D_max(myface, **kwargs) :

    cur      = myface.curve
    sampling = kwargs.get("sampling", 30)
    
    pinIndexList = kwargs.get( "pinIndex", myface.parts_vertex[myface.context_parts] )
    n = len(pinIndexList)

    pmpoints = [pm.pointPosition(myface.obj.vtx[i]) for i in pinIndexList]
    points = []
    for i in pmpoints :
        points.append(om2.MPoint(i[0], i[1], i[2]))

    dist_max = 0
    for i, p in enumerate(points) :
        
        pbef = points[-1] if i == 0   else points[i-1]
        pnex = points[0]  if i == n-1 else points[i+1]

        v1 = (pbef - p).normal()
        v2 = (pnex - p).normal()
        
        va = (v1 + v2).normal()
        vb = v1 ^ v2
        vn = va ^ vb

        #tools.makeVector(vn, p, "VN")

        dist_cache = -1
        # �J�[�u�̊e�Z�O�ƌ�������C�߂����̂��̗p�D
        for j in range(sampling) :

            end = curvetool.getCurvePoint(cur, [j/float(sampling), (j+1)/float(sampling)], "normal")

            en0 = (end[0]-p)*vn
            en1 = (end[1]-p)*vn 
            if en0 * en1 <= 0 :
                ip = end[0] - (end[1]-end[0])*( en0 / (en1-en0) )
                dist = (ip - p).length()
                
                if dist_cache == -1 or dist <= dist_cache :
                    dist_cache = dist
                    #crspt = ip

        if dist_cache == -1 : 
            print (u"ERROR ��_��������܂���")
            #return -1
        else:
            if dist_max < dist_cache :
                dist_max = dist_cache
        #tools.makeVector(crspt - p, p, "XtoP")

    #print "max_difference : ", dist_max 
    return dist_max


# ---------------------------------------------------------------------


def dist(
    myface,
    curpos_list = -1,
    param_list = -1,
    pinindex_list = -1
) :
    if param_list == -1 :
        param_list = myface.param_list
    if curpos_list == -1 :
        curpos_list = curvetool.getCurvePoint(myface.curve, param_list, "normal")
    if pinindex_list == -1 :
        pinindex_list =  myface.parts_vertex[myface.context_parts]

    if not len(param_list) == len(curpos_list) == len(pinindex_list) :
        print "ERROR"
        return -1
    
    d = 0
    for i in range(len(param_list)) :
        p1 = curpos_list[i]
        p2 = myface.defaultShape[pinindex_list[i]]

        d += ((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2 + (p1[2]-p2[2])**2)**0.5
        
    return d




# =====================================================================



def projectoin_3D(
        p,      # �X�N���[����̍��W
        scr,    # �X�N���[�����S
        scr_x,
        scr_y):
    
    return scr + p[0]*scr_x + p[1]*scr_y

# �I���̂QD�ʒu���v�Z
def point_2D_test():

    distance = 100

    p = pm.pointPosition()
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

    print "axis " , scr_x, scr_y
    
    ret = projection_2D(p,c,scr,scr_x,scr_y)
    print "2D Position : ", ret

# ��������񎟌��ɓ��e���āC�ʐς��v�Z�D
# ��̕��[�v�ɂ��āC�h�ǂ��炩����݂̂̓����h�ɂ���_�̐��𐔂���D
# ��������F�_����x�����ɕ�����L�΂��C�����񐔂���Ȃ�����D(�ڂ���ꍇ�̓~�X��)
def diff_2D(line1, line2, **kwargs) :
    width = kwargs.get('width', 2048)
    height = kwargs.get("height", 2048)

    # line�̈ʒu�̍ő�(+-)
    x_max = kwargs.get('x_max', 100)
    y_max = kwargs.get('y_max', 100)

    # ���C�����X�P�[�����O
    line1 = np.array(line1)
    line2 = np.array(line2)
    m     = np.array([x_max, y_max])
    wh    = np.array([width, height])
    for i, p in enumerate( line1 ) :
        line1[i] =  (m + p) * wh / (2 * m)
    for i, p in enumerate( line2 ) :
        line2[i] =  (m + p) * wh / (2 * m)
        
    #print line1
    #print line2

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

        if j%50 == 0 :print j, " ",

    # �摜�o�͗p�ɏ����o��
    path = 'C:\\Users\\piedp\\OneDrive\\Labo\\Sketch\\Script\\BlendLap\\Graph\\image\\differ.json'
    json_file = open(path, 'w')
    dic = {}
    dic["pix"]     = pix
    dic["width"]   = width
    dic["height"]  = height
    json.dump(dic, json_file)
    json_file.close() 
                

    print " "
    return S


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





# ====================================================================================


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
    print "axis " , scr_x, scr_y


    line1_3D = [pm.pointPosition(i) for i in myface.curve.cv]
    line1_2D = [projection_2D(i,c,scr,scr_x,scr_y) for i in line1_3D]

    pins = myface.parts_vertex["mouth"]
    pinss, params = tools.complete_pinIndenList(myface,pins)
    line2_3D = [pm.pointPosition(myface.obj.vtx[i]) for i in pinss]
    line2_2D = [projection_2D(i,c,scr,scr_x,scr_y) for i in line2_3D]

    print "line1(",len(line1_2D),") ", line1_2D
    print "line2(",len(line2_2D),") ", line2_2D

    dif =  diff_2D(line1_2D,line2_2D)

    return dif
