# coding:shift-JIS
# pylint: disable=F0401

# �����Ȃ��u�����h�V�F�C�v

import pymel.core as pm  
import sys
import numpy as np
import json
import time


from ..tool import tools
reload (tools)

from ..tool import my_face
reload (my_face)


def do_dmp_with_my_face( myface, curPosList ):

    # ---------�K�v�ȃf�[�^ -----------------------------------------
    # �X�P�b�`�̃^�C�v����s�����v�Z
    pinIndexList = myface.parts_vertex[myface.context_parts]
    # �s���̌��̈ʒu
    print pinIndexList
    prePos  = [ myface.defaultShape[i] for i in pinIndexList ]
    
    alpha = myface.alpha
 
    path_for_dmp = myface.mesh_data_path
    # --------------------------------------------------------------

    # -------- DMP���v�Z -------------------------------------------
    start = time.time()
    print u"\n - - - do_DMP  - - - \nalpha = ", alpha 
    w           =  DmpBlendShape(path_for_dmp, pinIndexList, curPosList, prePos, alpha).calc_weight() 
    # --------------------------------------------------------------
    
    print u"�u�����h�V�F�C�v�E�G�C�g:", w

    # ����ꂽ�E�G�C�g��blendshape��ݒ�
    for i, weight in enumerate(myface.blender.w):
        pm.setAttr(weight,w[i])

    print u"[time]  ", time.time() - start

class DmpBlendShape() :
    w_max   = 10.0                           # �d�݂̍ő�
    w_min   = -10.0                          # �d�݂̍ŏ�
    
    def __init__(
                    self, 
                    jsonPath, 
                    pinIndex, 
                    pin_pos_target,  # �s���̖ړI�ʒu�̃��X�g(pinIndex*3)
                    pin_pos_source,  # �s���̂��Ƃ��Ƃ̈ʒu(pinIndex*3)
                    alpha
                    ):
        self.num_of_pin = len(pinIndex)
        self.alpha = alpha
        self.m = []

        for i in range(len(pinIndex)) :
            self.m.append([ pin_pos_target[i][j] - pin_pos_source[i][j] for j in range(3) ])
            # �����쐬
            #tools.makeVector(self.m[i] , pin_pos_source[i])


        with open(jsonPath,"r") as json_file:
            
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            data         = json.load(json_file)
            self.n       = len(data["target"])               # �u�����h�V�F�C�v�̐�
            n            = self.n
            print u"BS�̐�     |", n
            num_of_pin   = self.num_of_pin
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            print u"���_��     |", len(data["target"][0])
            
            # ��������A���ׂĂ̒��_�ɂ���BT��B �����߂�
            # L�����߂�
            self.L = np.zeros((n,n))
            self.BT      = []
            for p in range(num_of_pin):
                self.BT.append ( np.zeros((n,3)) )
                #print (BT[p], p)
                
                for i,vec in enumerate( data["target"] ) :
                    #print (n_name[i])
                    #print (vec[ int(pinIndex[p]) ])
                    self.BT[p][i] = vec[ int(pinIndex[p]) ]
                #print ("\n")

                # - - - - - - - - - - - - - - - - - - - -
                # w = Xm[0] + Xm[1] + Xm[2] + .... + K
                # - - - - - - - - - - - - - - - - - - - -

                # �܂��Aalpha�𑫂��Ȃ��Ƃ����Ȃ�
                self.L  +=  self.BT[p].dot(self.BT[p].T)                                 

    
    def calc_weight(self, m_in = -1, alpha_in = -1) :

        n           =  self.n
        if m_in != -1 :
            self.m  =  m_in       
        m           =  self.m
        if alpha_in != -1 :
            self.alpha  =  alpha_in
        alpha       =  self.alpha
        
        # - - - L�����߂� - - -
        self.L     +=  (alpha * np.eye(n)) 
        L_inv       =  np.linalg.inv( self.L )
        
        # - - - X,K�����߂� - - -
        Xm_sum      = np.zeros(n)
        for p in range(self.num_of_pin) :
            Xm_sum += np.dot( np.dot(L_inv, self.BT[p]), m[p])

        w0          =  np.zeros(n)                    # �E�G�C�g�̏����l
        K           =  L_inv.dot(w0)

        #print("X=",X)
        #print("K=",K)

        # - - - w�����߂� - - -
        w           =  Xm_sum + K
        print u"num_of_pin  = ", self.num_of_pin
        

        # - - - �N���b�s���O - - -
        w           =  np.clip(w, self.w_min, self.w_max)

        print u"w           = \n",w
        return w


