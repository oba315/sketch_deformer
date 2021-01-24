# coding:shift-JIS
# pylint: disable=F0401

import pymel.core as pm
import sys
import json
import numpy as np
import time
import scipy
#from ..scipy import optimize


from ..tool import my_face
reload (my_face)
from ..tool import tools
reload (tools)
from ..tool import curvetool
reload (curvetool)
from ..process import limitLap
reload (limitLap)
from ..process import doDMP_completed
reload (doDMP_completed)
from ..process import doDMP_constraint
reload (doDMP_constraint)
from . import difference
reload (difference)
from . import housen
reload (housen)
from . import doDMP_constraint_pre
reload (doDMP_constraint_pre)
from ..process import limitLap
reload (limitLap)
from . import doDMP_kensaku2
reload (doDMP_kensaku2)

"""
���p��2�_����ɂ��C�K�؂Ȕz�u����������D
�܂��́C�ŋ}�~���@�I�ȍl�����Ō������\���𒲂ׂ�
���߁C�S�p�^�[�����߂��ăO���t���o���D
"""



# Nelder-Mead�@��p���čœK��
def myoptimize( myface, 
                x0 = [0,0.4],    # �����̏����ʒu
                debug = False, 
                do_ones = False, # �����ʒu�ł̂ݎ��s
                distance = [-1], # �ŏI�I�Ȍ덷���o��
                ) :
    
    cam_info = tools.cam_info()

    # �s���̐�
    n = len(myface.parts_vertex[myface.context_parts])
    nu = 5  # ���[���܂ށC��O�̃s���̐�
    nl = 5  # ���[���܂ށC���O�̃s���̐�
    
    pinID_comp_pre, params_comp_pre = doDMP_completed.complete_pin(myface)
    dmp = doDMP_constraint_pre.Dmp_const(myface, pinIndex = pinID_comp_pre)
    
    def targetfunc(x, *args) :
        # *args[0] : applyblendshape
        # *args[1] : params_comp_adr
        

        # �߂����镔���Ƃ��̉�������͍s���ׂ��H

        while(x[0] < 0) :
            x[0] += 1
        x[1] = x[1] - int(x[1])
        while(x[0] > x[1] or x[1] > x[0]+1) :
            x[1] += 1

        params = []
        # ��O
        for i in range(nu - 1) :
            param = x[0] + ( ((x[1]-x[0])/(nu-1.)) * float(i) )
            params.append(param - int(param))

        # ���O
        x[0] += 1
        
        for i in range(nl - 1) :
            param = x[1] + ( ((x[0]-x[1])/(nl-1.)) * float(i) )
            params.append(param - int(param))

        #print "id     : ", p1, ", ", p2
        #print "params : ", params
        x[0] -= 1

        curPosList =  curvetool.getCurvePoint(myface.curve, params, "normal")
        
        if debug :
            tools.makeSphere(pos_list = [curPosList[0]], name = "tempA")
            tools.makeSphere(pos_list = [curPosList[4]], name = "tempB")

        # - - - �s����⊮����DMP�����s - - - - - - - - - - - - - -  - - - - - -
        pinID_comp, params_comp = doDMP_completed.complete_pin(myface, params=params)
        curPosList_comp = curvetool.getCurvePoint(myface.curve, params_comp, "normal")
        
        weight, cost, pos, Bmw = dmp.do_dmp_post(curPosList_comp, applyBlendShape = args[0], ret_info = True)

        # --------------------------------------------------------------------
        
        #dist = 0
        #diff3D_row.append(difference.diff_3D_max(myface))
        #diff3D_row.append(difference.do_diff_2D(myface))
        #dist = difference.diff_pos2d(myface, pinIndexList=pinID_comp, vpos=pos, params=params_comp, curpos=curPosList_comp, cam_info=cam_info)
        #dist = difference.diff_3D(myface, pinIndexList=pinID_comp, pos = pos)
        #dist = difference.diff_3D_max(myface, pinIndexList=pinID_comp, pos = pos)
        #dist = ]]  difference.do_diff_2D(myface)
        #dist = housen.diff_nom(myface, pins=pinID_comp, curpos=curPosList_comp, mouthpos=pos, params=params_comp, cam_info=cam_info)
        #dist = housen.angle_normal(myface, pinIndexList= pinID_comp, mouthpos= pos, curpos= curPosList_comp, params= params_comp, cam_info=cam_info, pins=pinID_comp)
        #dist = housen.angle_2dpos(myface, vpos = pos, curpos=curPosList_comp, cam_info=cam_info)
        
        #dist = housen.angle_2dposplus(myface, vpos = pos, curpos=curPosList_comp, cam_info=cam_info)
        
        #dist = difference.diff_pos(myface, pinIndexList=pinID_comp, vpos=pos, params=params_comp, curpos=curPosList_comp)
        #dist = housen.diff_angle(myface, pinID_comp, pos, curPosList_comp, params_comp)
        dist = housen.angle_posplus(myface, vpos = pos, curpos=curPosList_comp, cam_info=cam_info, debug=debug)
        
        #dist = housen.angle_2dposplus_half(myface, vpos = pos, curpos=curPosList_comp, cam_info=cam_info)
        #print dist

        if args[1] != 0 :
            args[1][0] = curPosList_comp
        return dist
    
    curPosList_comp_adr = [0]
    if do_ones :
        pp = targetfunc(x0, True, curPosList_comp_adr)
        return
    else :
        # Nelder-Mead�@��p���čœK��
        args = (False, 0)  # targetfunc�ɑ������
        pp = scipy.optimize.minimize(targetfunc, x0, args, method = "Nelder-Mead", options = {"maxiter" : 80})
        distance[0] = targetfunc(pp["x"], True , curPosList_comp_adr)
    
        if debug : print pp
        return pinID_comp_pre, curPosList_comp_adr[0]


def DMP_search(sample, myface, opt_ids, opt_curpos) :
    
    # �X�P�b�`�w�肵���T���v�����őS�T��
    calc  = doDMP_kensaku2.repeat_dmp(myface,sample)
    # �v�Z���ʂ���ό`�����s
    dif = [0]
    pp    = doDMP_kensaku2.do_dmp_from_bwm(myface, sample,calc["diff3D"], distance=dif)

    print u"���p�̈ʒu�@�@       : ", pp
    print u"�ʒu�{�p�x�덷       : ",dif[0]
    print u"\n"

    print u"\n�l���_�[�~�[�h���ɂ��T��"

    # �S�T���̌��ʂ��󂯂ăl���_�[�~�[�h���ɂ��T��
    ids,curpos = myoptimize(myface,pp,debug = False, distance=dif)
    print u"�ʒu�{�p�x�덷       : ",dif[0]

    return ids, curpos


def lap(myface, pinID_comp, curPosList_comp) :
    
    if pinID_comp == -1 : 
        pm.warning(u"�œK����p�����u�����h�V�F�C�v�����s���Ă��������D")
        return

    # ------- �u�����h�V�F�C�v���t���[�Y ----------
    tools.freeze_blend_shape(
                    myface.obj, 
                    myface.blender, 
                    myface.defaultShape)  # �d��
    # --------------------------------------------

    
    #temp
    print "len", len(curPosList_comp)
    vtxPos = [pm.pointPosition(myface.obj.vtx[i]) for i in pinID_comp]
    print "len", len(vtxPos),  " ", len(vtxPos[0])
    mv = [tools.makeVector([curPosList_comp[i][j]-vtxPos[i][j] for j in range(3)], vtxPos[i]) for i in range(len(curPosList_comp))]
    print len(mv)
    

    print "id : ", pinID_comp
    limitLap.do_lap_limit(myface, pinID_comp, 12, curPosList_comp, debug = True)

    return 1







