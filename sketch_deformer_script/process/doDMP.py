# coding:shift-JIS
# pylint: disable=F0401

# 制限なしブレンドシェイプ

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

    # ---------必要なデータ -----------------------------------------
    # スケッチのタイプからピンを計算
    pinIndexList = myface.parts_vertex[myface.context_parts]
    # ピンの元の位置
    print pinIndexList
    prePos  = [ myface.defaultShape[i] for i in pinIndexList ]
    
    alpha = myface.alpha
 
    path_for_dmp = myface.mesh_data_path
    # --------------------------------------------------------------

    # -------- DMPを計算 -------------------------------------------
    start = time.time()
    print u"\n - - - do_DMP  - - - \nalpha = ", alpha 
    w           =  DmpBlendShape(path_for_dmp, pinIndexList, curPosList, prePos, alpha).calc_weight() 
    # --------------------------------------------------------------
    
    print u"ブレンドシェイプウエイト:", w

    # 得られたウエイトでblendshapeを設定
    for i, weight in enumerate(myface.blender.w):
        pm.setAttr(weight,w[i])

    print u"[time]  ", time.time() - start

class DmpBlendShape() :
    w_max   = 10.0                           # 重みの最大
    w_min   = -10.0                          # 重みの最小
    
    def __init__(
                    self, 
                    jsonPath, 
                    pinIndex, 
                    pin_pos_target,  # ピンの目的位置のリスト(pinIndex*3)
                    pin_pos_source,  # ピンのもともとの位置(pinIndex*3)
                    alpha
                    ):
        self.num_of_pin = len(pinIndex)
        self.alpha = alpha
        self.m = []

        for i in range(len(pinIndex)) :
            self.m.append([ pin_pos_target[i][j] - pin_pos_source[i][j] for j in range(3) ])
            # 矢印を作成
            #tools.makeVector(self.m[i] , pin_pos_source[i])


        with open(jsonPath,"r") as json_file:
            
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            data         = json.load(json_file)
            self.n       = len(data["target"])               # ブレンドシェイプの数
            n            = self.n
            print u"BSの数     |", n
            num_of_pin   = self.num_of_pin
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            print u"頂点数     |", len(data["target"][0])
            
            # いったん、すべての頂点についてBT＊B を求める
            # Lを求める
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

                # まだ、alphaを足さないといけない
                self.L  +=  self.BT[p].dot(self.BT[p].T)                                 

    
    def calc_weight(self, m_in = -1, alpha_in = -1) :

        n           =  self.n
        if m_in != -1 :
            self.m  =  m_in       
        m           =  self.m
        if alpha_in != -1 :
            self.alpha  =  alpha_in
        alpha       =  self.alpha
        
        # - - - Lを求める - - -
        self.L     +=  (alpha * np.eye(n)) 
        L_inv       =  np.linalg.inv( self.L )
        
        # - - - X,Kを求める - - -
        Xm_sum      = np.zeros(n)
        for p in range(self.num_of_pin) :
            Xm_sum += np.dot( np.dot(L_inv, self.BT[p]), m[p])

        w0          =  np.zeros(n)                    # ウエイトの初期値
        K           =  L_inv.dot(w0)

        #print("X=",X)
        #print("K=",K)

        # - - - wを求める - - -
        w           =  Xm_sum + K
        print u"num_of_pin  = ", self.num_of_pin
        

        # - - - クリッピング - - -
        w           =  np.clip(w, self.w_min, self.w_max)

        print u"w           = \n",w
        return w


