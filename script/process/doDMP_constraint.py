# coding:shift-JIS
# pylint: disable=F0401

import pymel.core as pm
import sys
import json
import numpy as np
import cvxopt

from ..tool import my_face
reload (my_face)


# ���C�u����cvxopt��p���ē񎟌v��@�������D
# 0����P�̊Ԃɐ������ău�����h�V�F�C�v�E�G�C�g�������D
"""
���������邱�Ƃɂ����ʁF
�ω��̏��Ȃ��`��̏ꍇ�́C�������Ȃ��ꍇ���������ߑł��ł����Ȃ��D
�������C�ω����傫���ꍇ�́C�������ߑł����ƕ����\���������D
���������邱�Ƃɂ���āC������x�͈̔͂ɂƂǂ߂���D
�܂��C���̒l������Ȃ����b���傫���D
(������������-0.2���炢�܂ł͕s�����e�����ق������������H
"""

# kward::pinIndex applyBlendShape(ap) 
def do_dmp( myface, 
            curPosList,     # �J�[�u���,�s���̖ړI�ʒu 
            alpha = 0.10, 
            t0 = 0.00,         # ���� 
            t1 = 1.00,         # ���
            ret_info = False,   # �œK���p�F�E�G�C�g�ȊO�̏��������o����?
            **kwargs
            ) :

    # �s���ɂ��钸�_�̃C���f�b�N�X(�^�����Ȃ����myface����D)
    pinIndexList    = kwargs.get( "pinIndex", myface.parts_vertex[myface.context_parts] )
    # �u�����h�V�F�C�v�ɂ��ό`�����s���邩
    applyBlendShape = kwargs.get( "applyBlednShape", True ) and \
                      kwargs.get( "ap", True)

    
    with open(myface.mesh_data_path,"r") as json_file:

        data         = json.load(json_file)
        num_of_pin   = len(pinIndexList)         # �s���̐�        
        n            =  len(data["target"])      # �u�����h�V�F�C�v�̐�
        w0           =  np.zeros((n,1))          # �E�G�C�g�̏����l
        mu           =  0.0001                   # �W��

        
        # ------------- �ړ���̈ʒu(�ړ���) -----------------
        # -- B�̌`�̊֌W�ろ��1*3n�̂悤�ɏc�ɕ��ׂ� --
        m = np.zeros((3*num_of_pin, 1))
        for i in range(num_of_pin):
            default_position = myface.defaultShape[pinIndexList[i]]
            for j in range(3) :
                m[3*i + j, 0] = curPosList[i][j] - default_position[j]
        # -------------------------------------------
        
        # ----------- �s���̃u�����h�V�F�C�v�x�N�g�� -------------
        B  = np.zeros((3*num_of_pin, n))
        for BS_index, BS in enumerate(data["target"]) :
            for i, pin_index in enumerate(pinIndexList):
                for j in range(3):
                    B[3*i + j, BS_index] = BS[pin_index][j]
        # -------------------------------------------------------            
        

        BT  = B.T

        I   = np.identity(n)

        S   = 2 * ( np.dot(BT, B) + (alpha + mu)*I )

        q   = (-2 * np.dot(BT, m) ) + (alpha * w0) 
        
        G = np.concatenate( [np.identity(n), -1*np.identity(n)], axis = 0 )

        h = np.concatenate( [np.full((n,1), float(t1)), np.full((n,1), -1.*t0)], axis = 0)

        """
        print "S" , S
        print "q" , q
        print "G" , G
        print "h" , h
        """

        # cvxopt�̃}�g���b�N�X�ɕϊ�
        S = cvxopt.matrix(S)
        q = cvxopt.matrix(q)
        G = cvxopt.matrix(G)
        h = cvxopt.matrix(h)


        # �񎟌v��@������
        cvxopt.solvers.options["show_progress"] = False    # �R�����g�̔�\��
        sol=cvxopt.solvers.qp(S,q, G,h)
        #print(sol)
        #print("weight :", sol["x"])                # ��
        #print("cost :", sol["primal objective"])   # �ŏI�I�ȃR�X�g�֐�

        if applyBlendShape :
            # ����ꂽ�E�G�C�g��blendshape��ݒ�
            for i, weight in enumerate(myface.blender.w):
                pm.setAttr(weight,sol["x"][i])
        
        
        if ret_info :
            weight   = sol["x"]
            cost     = sol["primal objective"]
            
            pos = np.dot(B,sol["x"])               # numpy.ndarray
            #print pos.reshape([len(pos)/3, 3])
            Bmw = np.linalg.norm(pos-m, ord=2)

            pos = pos.reshape([len(pos)/3, 3])
            for i in range(num_of_pin) :
                for j in range(3) :
                    pos[i][j] += myface.defaultShape[pinIndexList[i]][j]

            return weight, cost, pos, Bmw
            
        else :
            return sol["x"]

