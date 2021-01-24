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
�s���𓙊Ԋu�Ŕz�u���C���̎n�_�̈ʒu���J�[�u����X���C�h���đS�ʂ莎�����ƂŁC
�����Ƃ����]�ɋ߂��Ȃ�悤�Ȍ`��������D

�����F
w^2�Ō�������ꍇ
    �E�G�C�g�ɐ����������čs�����ꍇ�C���܂��œK�Ȉʒu��I�΂Ȃ�
    �ꍇ������D
    �E�G�C�g�ɐ����������Ȃ��Ō��������ꍇ�C�����ނ˗ǍD
Bw-m�Ō�������ꍇ�D
    �d�����T�˗ǍD
"""

"""
�����F�J�[�u�����͎��v����

"""


# �𑜓x�̕������n�_��ς��Čv�Z���s���C�K�v�Ȑ��l�������o���D
def repeat_dmp(myface, sample = 8) :
    
    # �s���̐�
    n = len(myface.parts_vertex[myface.context_parts])
    
    # �����̉𑜓x
    starting_point = [ i * (1. / sample) for i in range(sample)]

    cost = []
    w2   = []
    count = 0
    bwm = []
    for st in starting_point :
        
        # ��������p�����[�^
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
        

#�@�ŏI�I�ɓK�؂�ID��dmp�����s����D
def do_dmp_with_id(myface, sample, id):
    # �s���̐�
    n = len(myface.parts_vertex[myface.context_parts])
    starting_point = float(id) / float(sample)
    
    # ��������p�����[�^
    params = []
    for i in range(n) :
        param = starting_point + (float(i)/n)
        param = param - int(param)
        params.append(param)
    print "params", params
    
    curPosList =  curvetool.getCurvePoint(myface.curve, params, "normal")
    calc = doDMP_constraint.do_dmp(myface, curPosList, ap = True)
    
    # ����ꂽ�E�G�C�g��blendshape��ݒ�
    for i, weight in enumerate(myface.blender.w):
        pm.setAttr(weight,calc["w"][i])

    tools.deltemp("tempvec")



"""
# Bw-m�������Ƃ��������u�����h�V�F�C�v��K�p����D
cal = repeat_dmp(myface, 30)
id = cal["Bw-m"].index(min(cal["Bw-m"]))
print id
do_dmp_with_id(myface, 30, id)
"""