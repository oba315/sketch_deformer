# coding:shift-JIS
# pylint: disable=F0401

import pymel.core as pm
import maya.api.OpenMaya as om2
import sys
import numpy as np
import json

from ..tool import my_face
reload (my_face)
from . import difference
reload (difference)
from ..tool import tools
reload (tools)
from ..tool import curvetool
reload (curvetool)

# 法線を用いて口の上下を判断する


def normal_check(myface, sampling = 30, cp= -1) :
    cur = myface.curve

    sampling_list = [float(i)/sampling for i in range(sampling)]
    

    if type(cp) is int : cp =  curvetool.getCurvePoint(cur, sampling_list, "normal")
    
    # 中心の点
    csum = [0,0,0]
    for i in range(3):
        for p in cp :
            csum[i] += p[i]
    cent = om2.MPoint(csum[0]/sampling, csum[1]/sampling, csum[2]/sampling)

    # とりあえず，前後のサンプリング点から．それよりこまかく前後の点をとったほうがいいかも
    for i, p in enumerate( cp ) :
        pbef = cp[i-1]
        pnex = cp[0]  if i == len(cp)-1 else cp[i+1]

        v1 = (pbef - p).normal()
        v2 = (pnex - p).normal()
        
        va = v1 + v2
        vb = v1 ^ v2

        vs = va ^ vb    # 進行方向

        pc = p - cent
        vtemp = vs ^ pc

        vn = (vtemp ^ vs).normal()
                 
        tools.makeVector(vn, p)

    print "cp", cp


def normal_from_2dpoints(cp, cam_info, cp3d,  debug = False) :
    vecs = []
    # とりあえず，前後のサンプリング点から．それよりこまかく前後の点をとったほうがいいかも
    for i, p in enumerate( cp ) :
        p    = np.array( p )
        pbef = np.array( cp[i-1] )
        pnex = np.array( cp[0] if i == len(cp)-1 else cp[i+1])

        v1 = pbef - p
        v1 = v1 / np.linalg.norm(v1)
        v2 = pnex - p
        v2 = v2 / np.linalg.norm(v2)
        
        va = v1+v2
        va = va / np.linalg.norm(va)

        # 向きを指定
        if v2[0] > 0 :
            if va[1] <= (v2[1]/v2[0])*va[0] :
                va = -1*va
        else :
            if va[1] >= (v2[1]/v2[0])*va[0] :
                va = -1*va

        if debug : tools.makeVector(  (va[0]*cam_info[3] + va[1]*cam_info[4]), cp3d[i])

        vecs.append(va)
    return vecs

def normal_check_2D(myface, sampling = 30 , params = -1, cam_info = -1, cp3d=-1, debug=False) :

    # - - - カメラ情報を取得 - - - - - - - - - 
    if cam_info == -1 :
        cam_info = tools.cam_info()
    # - - - - - - - - - - - - - - - - - - 
    cur = myface.curve
    if params == -1 :
        sampling_list = [float(i)/sampling for i in range(sampling)]
    else :
        sampling_list = params
    if type(cp3d) is int : cp3d =  curvetool.getCurvePoint(cur, sampling_list, "normal")
    cp = [difference.projection_2D([i[0],i[1],i[2]],cam_info[1],cam_info[2],cam_info[3],cam_info[4]) for i in cp3d]
    # 中心の点
    """
    csum = [0,0,0]
    for i in range(3):
        for p in cp :
            csum[i] += p[i]
    cent = om2.MPoint(csum[0]/sampling, csum[1]/sampling, csum[2]/sampling)
    """
    vecs = normal_from_2dpoints(cp,cam_info,cp3d, debug)

    if debug : print "cp : ", cp
    return vecs


def mouth_normal_check_2D(  myface, sampling = 30, params = -1, 
                            comp = False, pins = -1, 
                            cp3d=-1,     # 変形後の頂点位置
                            cam_info = -1, debug =False) :

    # - - - カメラ情報を取得 - - - - - - - - - 
    if cam_info == -1 :
        cam_info = tools.cam_info()
    # - - - - - - - - - - - - - - - - - - 

    if comp : pins, param_comp = tools.complete_pinIndenList(myface)
    else :
        if pins == -1 :
            pins = myface.parts_vertex[myface.context_parts]

    obj = myface.obj

    if type(cp3d) is int : cp3d = [pm.pointPosition(obj.vtx[i]) for i in pins]

    cp = [difference.projection_2D([i[0],i[1],i[2]],cam_info[1],cam_info[2],cam_info[3],cam_info[4]) for i in cp3d]
    vecs = normal_from_2dpoints(cp,cam_info,cp3d, debug)
    
    return vecs


def diff_nom(   myface, pins = -1,
                curpos = -1,
                mouthpos=-1,        # 変形後の頂点位置 
                params = -1, cam_info = -1, 
                debug = False) :
    
    if params == -1 :
        params = myface.param_list
    
    vecs1 = normal_check_2D(myface, params = params, cam_info=cam_info, cp3d = curpos, debug=debug) # スケッチ
    vecs2 = mouth_normal_check_2D(myface, pins = pins, cp3d = mouthpos, cam_info=cam_info, debug=debug)            # モデル
    
    if debug : print len(vecs1), " ", vecs1
    if debug : print len(vecs2), " ", vecs2

    # ベクトルの誤差：とりあえず内積
    dist = 0
    
    for i in range(len(vecs1)) :
        dist -= np.dot(vecs1[i], vecs2[i]) / (np.linalg.norm(vecs1[i]) * np.linalg.norm(vecs2[i]))

    if debug : print "dist :: ",dist
    
    
    return dist


def angle( pos ) :
    
    pos = [np.array(i) for i in pos]

    n = len(pos)

    angle = [0]*n

    for i,p in enumerate(pos) : 
        p1 = pos[i-2]
        p2 = pos[i+2 if i+2 < n-1 else i+2-(n-1)]
        v1 = p1 - p
        v2 = p2 - p
        v1 = v1/np.linalg.norm(v1)
        v2 = v2/np.linalg.norm(v2)

        angle[i] = v1.dot(v2)
    

    if not np.isnan(angle).any() :
        return angle
    else :
        print "pos   ", pos
        print "angle ", angle
        raise Exception('ERROR : angleにnp.nanが含まれています.パラメータに[0:1]以外の値が入っている可能性があります．')


def diff_angle(myface, pinIndexList=-1, mouthpos=-1, curpos=-1, params=-1) :

    angle_mouth = angle(mouthpos)
    angle_cor   = angle(curpos)

    diff = 0
    for i in range(len(angle_mouth)) :
        diff += abs(angle_mouth[i]-angle_cor[i])

    return diff

def show_angle(mouthpos=-1, curpos=-1) :
    angle_mouth = angle(mouthpos)
    angle_cur   = angle(curpos)
    
    # 誤差を表示
    for i, p in  enumerate (mouthpos) :
        d = angle_mouth[i]- angle_cur[i]
        t = '{:.4f}'.format(d)
        n = "_" + str(i)+"temptext"
        tools.maketext(t,n,p,s=0.1)

"""
    for i,t in enumerate(angle_mouth):
        t = '{:.4f}'.format(t)
        t = "m"+str(i)+":"+t
        n = "_m"+str(i)+"temptext"
        tools.maketext(t = t, name=n, p = mouthpos[i],s = 0.1 )

    for i,t in enumerate(angle_cur):
        t = '{:.4f}'.format(t)
        t = "c"+str(i)+":"+t
        n = "_c"+str(i)+"temptext"
        tools.maketext(t = t, name=n, p = curpos[i],s = 0.1 )
"""

# まがっているところに重みづけ
def angle_normal(myface, pinIndexList=-1, pins = -1,mouthpos=-1, curpos=-1, params=-1, cam_info = -1,debug = False) :
    angle_mouth = angle(mouthpos)
    angle_cur   = angle(curpos)

    vecs1 = normal_check_2D(myface, params = params, cam_info=cam_info, cp3d = curpos, debug=debug) # スケッチ
    vecs2 = mouth_normal_check_2D(myface, pins = pins, cp3d = mouthpos, cam_info=cam_info, debug=debug)            # モデル

    if debug : print len(vecs1), " ", vecs1
    if debug : print len(vecs2), " ", vecs2

    print angle_cur

    # ベクトルの誤差：とりあえず内積
    dist = 0
    for i in range(len(vecs1)) :
        dot = np.dot(vecs1[i], vecs2[i]) / (np.linalg.norm(vecs1[i]) * np.linalg.norm(vecs2[i]))
        
        print " ", angle_cur[i]
        print 1/abs(angle_cur[i])

        dist -= dot*(1/abs(angle_cur[i]))   # 重みづけ

        #print dot,  "/", angle_cor[i], "/", dist
    
    if debug : print "dist :: ",dist
    
    return dist

#normal_check_2D(myface, debug=True)
#mouth_normal_check_2D(myface, comp = True, debug =True)
#diff_nom(myface, debug=True)

def angle_pos(myface, vpos, curpos, debug = False):
    angle_cur   = angle(curpos)

    if debug : print angle_cur
    if debug : print vpos

    cp = curpos
    dsum = 0
    for i, v in enumerate(vpos) :
        dvt = [v[j] - cp[i][j] for j in range(3)]
        d = dvt[0]**2 + dvt[1]**2 + dvt[2]**2
        
        d += d*(1/abs(angle_cur[i]))   # 重みづけ
        print " ", d
        dsum += d
    return dsum




def angle_2dpos(myface, vpos, curpos, cam_info, debug=False):
    angle_cur = angle(curpos)

    cp2d = [tools.projection_2D([cp[0],cp[1],cp[2]], cam_info[1], cam_info[2], cam_info[3], cam_info[4]) for cp in curpos]
    vp2d = [tools.projection_2D([cp[0],cp[1],cp[2]], cam_info[1], cam_info[2], cam_info[3], cam_info[4]) for cp in vpos]

    if len(curpos) != len(vpos) : print "ERROR"
    dsum = 0
    for i in range(len(curpos)) :
        dx = cp2d[i][0]-vp2d[i][0]
        dy = cp2d[i][1]-vp2d[i][1]

        dist = dx**2 + dy**2

        dist = dist *(100/abs(1-angle_cur[i]))   # 重みづけ

        dsum += dist
    # 内積でなくarctanのほうがよくない？内積だとまずくない？？
    return dsum

def angle_2dposplus(myface, vpos, curpos, cam_info, debug=False):
    
    cp2d = [tools.projection_2D([cp[0],cp[1],cp[2]], cam_info[1], cam_info[2], cam_info[3], cam_info[4]) for cp in curpos]
    vp2d = [tools.projection_2D([cp[0],cp[1],cp[2]], cam_info[1], cam_info[2], cam_info[3], cam_info[4]) for cp in vpos]

    if len(curpos) != len(vpos) : print "ERROR"
    dsum = 0
    for i in range(len(curpos)) :
        dx = cp2d[i][0]-vp2d[i][0]
        dy = cp2d[i][1]-vp2d[i][1]

        dist = dx**2 + dy**2

        #dist = dist *(100/abs(angle_cur[i]))   # 重みづけ

        dsum += dist

    print "pos ",dsum

    angle_mouth = angle(vpos)
    angle_cor   = angle(curpos)

    diff = 0
    for i in range(len(angle_mouth)) :
        
        diff += abs(angle_mouth[i]-angle_cor[i])
        #if np.isnan(diff) :
            #print "EROOR ", angle_mouth[i], " " , angle_cor[i]
        

    print "ang ",diff

    return dsum + diff*400


def angle_posplus(myface, vpos, curpos, cam_info, debug=False):
    
    if len(curpos) != len(vpos) : print "ERROR"
    dsum = 0
    for i in range(len(curpos)) :
        dx = curpos[i][0]-vpos[i][0]
        dy = curpos[i][1]-vpos[i][1]
        dz = curpos[i][2]-vpos[i][2]

        dist = dx**2 + dy**2 + dz**2

        #dist = dist *(100/abs(angle_cur[i]))   # 重みづけ

        dsum += dist

    if debug : print "pos ",dsum

    angle_mouth = angle(vpos)
    angle_cor   = angle(curpos)

    diff = 0
    for i in range(len(angle_mouth)) :
        
        diff += abs(angle_mouth[i]-angle_cor[i])
        #if np.isnan(diff) :
            #print "EROOR ", angle_mouth[i], " " , angle_cor[i]
        

    if debug : print "ang ",diff

    return dsum + diff*400

def angle_2dposplus_half(myface, vpos, curpos, cam_info, debug=False):
    
    cc = []
    vv = []
    for i in range(len(vpos)) :
        if i%2 == 0 :    
            cc.append(curpos[i])
            vv.append(vpos[i])

    cp2d = [tools.projection_2D([cp[0],cp[1],cp[2]], cam_info[1], cam_info[2], cam_info[3], cam_info[4]) for cp in cc]
    vp2d = [tools.projection_2D([cp[0],cp[1],cp[2]], cam_info[1], cam_info[2], cam_info[3], cam_info[4]) for cp in vv]

    if len(curpos) != len(vpos) : print "ERROR"
    dsum = 0
    for i in range(len(cc)) :
        dx = cp2d[i][0]-vp2d[i][0]
        dy = cp2d[i][1]-vp2d[i][1]

        dist = dx**2 + dy**2
        dsum += dist

    print "pos ",dsum

    angle_mouth = angle(vpos)
    angle_cor   = angle(curpos)

    diff = 0
    for i in range(len(angle_mouth)) :
        diff += abs(angle_mouth[i]-angle_cor[i])

    print "ang ",diff

    return dsum + diff*800