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
���p�̈ʒu�����[�U�[���w�肵�āC�㉺���S����������D
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
# ���X�g��^����ꂽ�͈͂Ő��K��
def list_normalize(target, myrange=[0,1]) :
    d         = myrange[1] - myrange[0]
    target_d  = float(max(target) - min(target))
    nom = [ d * (i-min(target))/target_d + myrange[0] for i in target ]
    return(nom)
# -----------------------------------------------------------------------------------


def dmp_with_corner( 
            myface, 
            corner = [-1,-1],       # ���p�̈ʒu
            um = 0.5,               # �㕔�̒��S
            lm = 0.5,               # �����̒��S
            ap = True,               # �ό`��K�p���邩�ǂ���
            log = True
            ) :

    c0 = corner[0]
    c1 = corner[1]

    if log : preview_point(myface,[c0,c1], True)
    if log : print "corner ::" , [c0,c1]

    # �s���̐�
    nu = 5  # ���[���܂ށC��O�̃s���̐�
    nl = 5  # ���[���܂ށC���O�̃s���̐�
    
    
    index = myface.parts_vertex[myface.context_parts]
    
    upper_index = index[:nu]
    lower_index = index[-(nl-1):]
    lower_index.append(index[0])

    # �����Ŕz�u�����Cmyface����param���g�p
    params = myface.param_list
    upper_params = list_normalize(params[:5])
    lower_params = params[-4:]
    lower_params.append(params[0]+1)
    lower_params = list_normalize(lower_params)
    
    # ���p��param�C���S��param(0-1)����J�[�u��̈ʒu���w��D
    # �񎟊֐��ŕ⊮(�C���O�̒��S�ʒu�̃p�����[�^��0.5�Ƃ���D) 
    # ���v���̑O��
    
    # �㉺���ꂼ���0-1�ɔz�u
    # ��O
    if nu%2 == 0 :
        print "ERROR : ���_���������ł��D"
    else :
        temp = []
        for i in upper_params :
            if i >= 0.5 :
                temp.append(i*um/0.5)
            else :
                temp.append( ((1-um)/0.5)*i + (um-0.5)/0.5 ) 
        upper_params = temp
    # ���O
    if nl%2 == 0 :
        print "ERROR : ���_���������ł��D"
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
    
    # �w�肵�����p�͈̔͂ŏ㉺������
    if c1 < c0 : c1 += 1
    params = list_normalize(upper_params, [c0,c1])[:-1]
    c0 += 1
    params.extend( list_normalize(lower_params, [c1,c0])[:-1] )

    # �P�𒴂������̂�ҏW
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
            # �덷�]��
            #diff[ii][jj] = difference.diff_3D(myface)
            #diff[ii][jj] = difference.diff_3D_max(myface)
            #diff[ii][jj] = difference.do_diff_2D(myface)
            diff[ii][jj] = difference.dist(myface, param_list=params)
            print "distance : ", diff[ii][jj]
            
    

    # �œK��
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


