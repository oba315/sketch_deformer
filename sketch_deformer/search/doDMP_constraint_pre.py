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

class Dmp_const :

    # �O����
    def __init__(self, myface, alpha= 0.1, t0=0.0,t1=1.0, **kwargs) :

        self.myface = myface
        self.alpha = alpha
        self.t0 = t0
        self.t1 = t1

        # �s���ɂ��钸�_�̃C���f�b�N�X(�^�����Ȃ����myface����D)
        self.pinIndexList    = kwargs.get( "pinIndex", myface.parts_vertex[myface.context_parts] )
        
        
        with open(myface.mesh_data_path,"r") as json_file:

            data         = json.load(json_file)
            self.num_of_pin   = len(self.pinIndexList)         # �s���̐�        
            n            =  len(data["target"])      # �u�����h�V�F�C�v�̐�
            self.w0           =  np.zeros((n,1))          # �E�G�C�g�̏����l
            mu           =  0.0001                   # �W��

            # -- B�̌`�̊֌W�ろ��1*3n�̂悤�ɏc�ɕ��ׂ� --
            self.pin_def_pos = []
            for i in range(self.num_of_pin):
                self.pin_def_pos.append( myface.defaultShape[self.pinIndexList[i]] ) 
            # -------------------------------------------
            
            # ----------- �s���̃u�����h�V�F�C�v�x�N�g�� -------------
            self.B  = np.zeros((3*self.num_of_pin, n))
            for BS_index, BS in enumerate(data["target"]) :
                for i, pin_index in enumerate(self.pinIndexList):
                    for j in range(3):
                        self.B[3*i + j, BS_index] = BS[pin_index][j]
            # -------------------------------------------------------            
            

            self.BT  = self.B.T

            I   = np.identity(n)

            S   = 2 * ( np.dot(self.BT, self.B) + (self.alpha + mu)*I )

            
            G = np.concatenate( [np.identity(n), -1*np.identity(n)], axis = 0 )

            h = np.concatenate( [np.full((n,1), float(t1)), np.full((n,1), -1.*t0)], axis = 0)

            """
            print "S" , S
            print "q" , q
            print "G" , G
            print "h" , h
            """

            # cvxopt�̃}�g���b�N�X�ɕϊ�
            self.S = cvxopt.matrix(S)
            self.G = cvxopt.matrix(G)
            self.h = cvxopt.matrix(h)

            #return myface, pin_def_pos, pinIndexList, num_of_pin, B,  BT, alpha, w0, S,G,h, applyBlendShape, ret_info
            
        

    def do_dmp_post(self, curPosList, applyBlendShape, ret_info) :
        # ------------- �ړ���̈ʒu(�ړ���) -----------------
        m = np.zeros((3*self.num_of_pin, 1))
        for i in range(self.num_of_pin):
            for j in range(3) :
                m[3*i + j, 0] = curPosList[i][j] - self.pin_def_pos[i][j]
            

        q   = (-2 * np.dot(self.BT, m) ) + (self.alpha * self.w0) 
        q = cvxopt.matrix(q)
                
        # �񎟌v��@������
        cvxopt.solvers.options["show_progress"] = False    # �R�����g�̔�\��
        sol=cvxopt.solvers.qp(self.S,q, self.G,self.h)
        #print(sol)
        #print("weight :", sol["x"])                # ��
        #print("cost :", sol["primal objective"])   # �ŏI�I�ȃR�X�g�֐�

        if applyBlendShape :
            # ����ꂽ�E�G�C�g��blendshape��ݒ�
            for i, weight in enumerate(self.myface.blender.w):
                pm.setAttr(weight,sol["x"][i])
        


        if ret_info :
            weight   = sol["x"]
            cost     = sol["primal objective"]
            
            pos = np.dot(self.B,sol["x"])               # numpy.ndarray
            #print pos.reshape([len(pos)/3, 3])
            Bmw = np.linalg.norm(pos-m, ord=2)

            pos = pos.reshape([len(pos)/3, 3])
            for i in range(self.num_of_pin) :
                for j in range(3) :
                    pos[i][j] += self.myface.defaultShape[self.pinIndexList[i]][j]

            return weight, cost, pos, Bmw
            
        else :
            return sol["x"]