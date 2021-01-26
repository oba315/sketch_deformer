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

# kward::pinIndex applyBlendShape(ap) 
def do_dmp( myface, 
            curPosList,     # カーブ上の,ピンの目的位置 
            alpha = 0.10, 
            t0 = 0.00,         # 下限 
            t1 = 1.00,         # 上限
            ret_info = False,   # 最適化用：ウエイト以外の情報を書き出すか?
            **kwargs
            ) :

    # ピンにする頂点のインデックス(与えられなければmyfaceから．)
    pinIndexList    = kwargs.get( "pinIndex", myface.parts_vertex[myface.context_parts] )
    # ブレンドシェイプによる変形を実行するか
    applyBlendShape = kwargs.get( "applyBlednShape", True ) and \
                      kwargs.get( "ap", True)

    
    with open(myface.mesh_data_path,"r") as json_file:

        data         = json.load(json_file)
        num_of_pin   = len(pinIndexList)         # ピンの数        
        n            =  len(data["target"])      # ブレンドシェイプの数
        w0           =  np.zeros((n,1))          # ウエイトの初期値
        mu           =  0.0001                   # 係数

        
        # ------------- 移動後の位置(移動量) -----------------
        # -- Bの形の関係上ｍは1*3nのように縦に並べる --
        m = np.zeros((3*num_of_pin, 1))
        for i in range(num_of_pin):
            default_position = myface.defaultShape[pinIndexList[i]]
            for j in range(3) :
                m[3*i + j, 0] = curPosList[i][j] - default_position[j]
        # -------------------------------------------
        
        # ----------- ピンのブレンドシェイプベクトル -------------
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

        # cvxoptのマトリックスに変換
        S = cvxopt.matrix(S)
        q = cvxopt.matrix(q)
        G = cvxopt.matrix(G)
        h = cvxopt.matrix(h)


        # 二次計画法を解く
        cvxopt.solvers.options["show_progress"] = False    # コメントの非表示
        sol=cvxopt.solvers.qp(S,q, G,h)
        #print(sol)
        #print("weight :", sol["x"])                # 解
        #print("cost :", sol["primal objective"])   # 最終的なコスト関数

        if applyBlendShape :
            # 得られたウエイトでblendshapeを設定
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

