# coding:shift-JIS
# pylint: disable=F0401

# �����X�P�b�`����͂����ۂ̕ό`

import pymel.core as pm  
import sys
import numpy as np
import json
import time


from ..tool import tools
reload (tools)

from ..tool import my_face
reload (my_face)
from ..tool import curvetool
reload (curvetool)
from . import doDMP_constraint
reload(doDMP_constraint)
from . import limitLap
reload(limitLap)


def do_only_one_parts(myface, alpha,t0 = 0, t1 = 1) :

    curPosall = curvetool.getCurvePoint(myface.curve, myface.param_list)
    pinIDall  = myface.parts_vertex[myface.context_parts]

    doDMP_constraint.do_dmp( myface,
                        curPosall,
                        pinIndex = pinIDall, 
                        ap = True,
                        alpha= alpha,
                        t0=t0,
                        t1=t1
                        )


def do(myface, alpha, t0 = 0, t1 = 1) :

    curPosall = []
    pinIDall  = []


    for partname in myface.parts_vertex :
        curvename = myface.projection_curve_name + "_" + partname
        if pm.objExists(curvename) :
            cur = pm.PyNode(curvename)
            # �p�����[�^�͎g���܂킵
            curPosall  += curvetool.getCurvePoint(cur, myface.param_list)
            pinIDall   += myface.parts_vertex[partname]

    doDMP_constraint.do_dmp( myface,
                        curPosall,
                        pinIndex = pinIDall, 
                        ap = True,
                        alpha= alpha,
                        t0=t0,
                        t1=t1
                        )

def lap(myface, area=8) :
    # ------- �u�����h�V�F�C�v���t���[�Y ----------
    tools.freeze_blend_shape(
                    myface.obj, 
                    myface.blender, 
                    myface.defaultShape)  # �d��
    # --------------------------------------------
    
    # �p�����[�^�͎g����
    params = myface.param_list
    area_in = area

    for partname in myface.parts_vertex :
        
        curvename = myface.projection_curve_name + "_" + partname
        if pm.objExists(curvename) :
            cur = pm.PyNode(curvename)

            pinID = myface.parts_vertex[partname]

            # --------- �s����⊮ -----------------------
            pinID_comp, params_comp = tools.complete_pinIndenList(myface,pinID,params)
            curpos_comp = curvetool.getCurvePoint(cur,  params_comp, "curvature")

            # --------- area���㏑�� ---------------------
            if partname in myface.lap_area :
                area = myface.lap_area[partname]
            else :
                area = area_in
            # --------- ���v���V�A���G�f�B�b�g�����s -------
            limitLap.do_lap_limit(
                    myface,
                    pinID_comp,
                    area, 
                    curpos_comp, 
                    debug=False
                    )

    

