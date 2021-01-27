# coding:shift-JIS
# pylint: disable=F0401

### m�������������Ăł��邩�H###

import pymel.core as pm  
import sys
import numpy as np
import json
import time
myfanc_path = ["C:/Users/piedp/OneDrive/Labo/Sketch/Script/BlendLap/myfanc",
               "C:/Users/piedp/OneDrive/Labo/Sketch/Script/BlendLap"]
for path in myfanc_path :
    if not path in sys.path :
        sys.path.append( path )
import tools
reload (tools)
import my_face
reload (my_face)
import curvetool
reload (curvetool)



def do_dmp_with_my_face( myface, curPosList ):

    # -------- DMP���v�Z -------------------------------------------
    start = time.time()
    print u"\n - - - do_DMP  - - - \nalpha = ", alpha 
    w = DmpBlendShape(myface).calc_weight(curPosList)
    # --------------------------------------------------------------
    
    print u"�u�����h�V�F�C�v�E�G�C�g:", w
    # ����ꂽ�E�G�C�g��blendshape��ݒ�
    for i, weight in enumerate(myface.blender.w):
        pm.setAttr(weight,w[i])

    print u"[time]  ", time.time() - start


class DmpBlendShape() :
    w_max   = 1.0                           # �d�݂̍ő�
    w_min   = -1.0                          # �d�݂̍ŏ�
    
    def __init__(   self, 
                    myface, 
                    pinIndex = None, 
                    alpha = 0.5,
                    debug = False 
                    ):
        
        self.alpha = alpha
        
        if pinIndex : self.pinIndex = pinIndex
        else : self.pinIndex = myface.parts_vertex[myface.context_parts]
        self.num_of_pin = len(self.pinIndex)
        
        
        # �s���̂��Ƃ��Ƃ̈ʒu(pinIndex*3)   : prepos
        self.pin_pos_source= [ myface.defaultShape[i] for i in self.pinIndex ]


        with open(myface.mesh_data_path,"r") as json_file:
            
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
            L = np.zeros((n,n))
            self.BT      = []               #BT[p] : p�Ԗڂ̃s���ɂ�����e�u�����h�V�F�C�v�̈ړ���(�u�����h�V�F�C�v��*3)
            for p in range(num_of_pin):
                self.BT.append ( np.zeros((n,3)) )
                for i,vec in enumerate( data["target"] ) :
                    #print (n_name[i])
                    #print (vec[ int(pinIndex[p]) ])
                    self.BT[p][i] = vec[ int(self.pinIndex[p]) ]
                
                # �܂��Aalpha�𑫂��Ȃ��Ƃ����Ȃ�
                L  +=  self.BT[p].dot(self.BT[p].T)
                
            # - - - L�����߂� - - -
            L       +=   (alpha * np.eye(n)) 
            L_inv    =   np.linalg.inv( L )

            # - - - X,K�����߂� - - -
            self.X = []
            for p in range(self.num_of_pin) :
                self.X.append(np.dot(L_inv, self.BT[p]))
            
            w0          =  np.zeros(n)                    # �E�G�C�g�̏����l
            self.K      =  L_inv.dot(w0)                  # �Ȃ�Ń��Ȃ���H
                        

    
    def calc_weight(self, curposlist, ret_info = False, debug = False) :

        n           =  self.n
        self.pin_pos_target = curposlist     # �s���̖ړI�ʒu�̃��X�g(pinIndex*3)
        
        m = []
        for i in range(len(self.pinIndex)) :
            m.append([ self.pin_pos_target[i][j] - self.pin_pos_source[i][j] for j in range(3) ])
            # �����쐬
            if debug : tools.makeVector(m[i] , self.pin_pos_source[i])


        # - - - - - - - - - - - - - - - - - - - -
        # w = Xm[0] + Xm[1] + Xm[2] + .... + K
        # - - - - - - - - - - - - - - - - - - - -
        Xm_sum      = np.zeros(n)
        for p in range(self.num_of_pin) :
            Xm_sum += np.dot( self.X[p], m[p])

        # - - - w�����߂� - - -
        w           =  Xm_sum + self.K
        print u"num_of_pin  = ", self.num_of_pin

        # - - - �N���b�s���O - - -
        w           =  np.clip(w, self.w_min, self.w_max)

        if debug : print u"w           = \n",w
        
        
        if ret_info :
            weight   = w
            cost     = 100
            
            Bmw = 0#np.linalg.norm(pos-m, ord=2)

            pos = [np.dot(w, self.BT[i]) + self.pin_pos_source[i] for i in range(n)]

            return weight, cost, pos, Bmw

        else : return w


#curPosList =  curvetool.getCurvePoint(myface.curve, myface.param_list, "curvature")
#do_dmp_with_my_face(myface, curPosList)