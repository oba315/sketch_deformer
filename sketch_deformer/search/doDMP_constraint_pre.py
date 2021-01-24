# coding:shift-JIS
# pylint: disable=F0401

import pymel.core as pm
import sys
import json
import numpy as np
import cvxopt

from ..tool import my_face
reload (my_face)


# ライブラリcvxoptを用いて二次計画法を解く．
# 0から１の間に制限してブレンドシェイプウエイトを解く．
"""
制限があることによる効果：
変化の少ない形状の場合は，制限がない場合もαを決め打ちでも問題ない．
しかし，変化が大きい場合は，αを決め打ちだと崩れる可能性が高い．
制限があることによって，ある程度の範囲にとどめられる．
また，負の値が入らない恩恵も大きい．
(もしかしたら-0.2くらいまでは不を許容したほうがいいかも？
"""

class Dmp_const :

    # 前処理
    def __init__(self, myface, alpha= 0.1, t0=0.0,t1=1.0, **kwargs) :

        self.myface = myface
        self.alpha = alpha
        self.t0 = t0
        self.t1 = t1

        # ピンにする頂点のインデックス(与えられなければmyfaceから．)
        self.pinIndexList    = kwargs.get( "pinIndex", myface.parts_vertex[myface.context_parts] )
        
        
        with open(myface.mesh_data_path,"r") as json_file:

            data         = json.load(json_file)
            self.num_of_pin   = len(self.pinIndexList)         # ピンの数        
            n            =  len(data["target"])      # ブレンドシェイプの数
            self.w0           =  np.zeros((n,1))          # ウエイトの初期値
            mu           =  0.0001                   # 係数

            # -- Bの形の関係上ｍは1*3nのように縦に並べる --
            self.pin_def_pos = []
            for i in range(self.num_of_pin):
                self.pin_def_pos.append( myface.defaultShape[self.pinIndexList[i]] ) 
            # -------------------------------------------
            
            # ----------- ピンのブレンドシェイプベクトル -------------
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

            # cvxoptのマトリックスに変換
            self.S = cvxopt.matrix(S)
            self.G = cvxopt.matrix(G)
            self.h = cvxopt.matrix(h)

            #return myface, pin_def_pos, pinIndexList, num_of_pin, B,  BT, alpha, w0, S,G,h, applyBlendShape, ret_info
            
        

    def do_dmp_post(self, curPosList, applyBlendShape, ret_info) :
        # ------------- 移動後の位置(移動量) -----------------
        m = np.zeros((3*self.num_of_pin, 1))
        for i in range(self.num_of_pin):
            for j in range(3) :
                m[3*i + j, 0] = curPosList[i][j] - self.pin_def_pos[i][j]
            

        q   = (-2 * np.dot(self.BT, m) ) + (self.alpha * self.w0) 
        q = cvxopt.matrix(q)
                
        # 二次計画法を解く
        cvxopt.solvers.options["show_progress"] = False    # コメントの非表示
        sol=cvxopt.solvers.qp(self.S,q, self.G,self.h)
        #print(sol)
        #print("weight :", sol["x"])                # 解
        #print("cost :", sol["primal objective"])   # 最終的なコスト関数

        if applyBlendShape :
            # 得られたウエイトでblendshapeを設定
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