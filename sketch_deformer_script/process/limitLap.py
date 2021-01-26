# coding:shift-JIS
# pylint: disable=F0401

import pymel.core as pm
import maya.api.OpenMaya as om2

import sys
import json
import numpy as np
import time

from ..tool import tools
reload (tools)
from ..tool import curvetool
reload (curvetool)
from ..tool import my_face
reload (my_face)



# ----------------------------------------------------
#    ラプラシアンエディットを実行
#       - - 周辺頂点に範囲を限定
#       - - ピンを補完してスケッチ上の全頂点を合わせる
# ----------------------------------------------------
def laplacian_cmd_completion( myface, 
                              search_area = 8,
                              do_completation = 1,
                              pinIndexList = None
                               ) :

    print u"\n------- 範囲を指定してLaplacianEditを行います ----------"
    print  " - serch_area : ", search_area
    print  " - lambda     : ", myface.lamda
    start = time.time()

    # ------- ブレンドシェイプをフリーズ ----------
    tools.freeze_blend_shape(
                    myface.obj, 
                    myface.blender, 
                    myface.defaultShape)  # 重い
    # --------------------------------------------

    print "Lap time: ", time.time()-start

    

    # -------- ピンを補完 -------------------------
    if do_completation == 1 :
        pinIndexList_comp  = [-1]
        paramList_comp     = [-1]
        curPosList_comp    = complete_pinIndenList(
                                    myface, 
                                    pinIndexList_comp, 
                                    paramList_comp)
    else :
        pinIndexList_comp = myface.parts_vertex[myface.context_parts]
        paramList_comp  =  myface.param_list
        curPosList_comp = curvetool.getCurvePoint(myface.curve,paramList_comp,"normal") # normalじゃないかも
    # --------------------------------------------

    print "Lap time: ", time.time()-start

    # --------- ラプラシアンエディットを実行 -------
    do_lap_limit(
            myface,
            pinIndexList_comp,
            search_area, 
            curPosList_comp, 
            )
    # ---------------------------------------------

    print "Lap time: ", time.time()-start




# ---- 近傍頂点を検索し、リストとして返す。リストは最初の頂点からの距離で階層化 ----
def serch_close_vertex( obj_name, pinIndexList, connectionLength) :
    print "\n - - - serch_close_vertex - - -"
    area = []
    area.append(pinIndexList)
    
    dagPath = tools.getDagPath(obj_name)
    mitMeshVertIns  = om2.MItMeshVertex(dagPath)
    print " - serch range        :",connectionLength
    
    for d in range(connectionLength) :
        area.append([])
        for i in area[d] :
            mitMeshVertIns.setIndex(i)
            connectList = mitMeshVertIns.getConnectedVertices()
            
            for p in connectList :
                tr = 0
                for q in range(0,d+2) :
                    if p in area[q] :
                        tr = 1
                if tr == 0 :
                    area[d+1].append(p)
    
    # 例外処理：最外殻頂点について、一つの頂点としか接続しない頂点が生まれる。のでとりあえずこれのみを除外(再外殻がピンでなくなる)
    for p in area[connectionLength][:] :
        mitMeshVertIns.setIndex(p)
        connectList = mitMeshVertIns.getConnectedVertices()
        
        count = 0
        for i in connectList :
            if i in area[connectionLength-1] or i in area[connectionLength] :
                count += 1
        if count == 1 :
            area[connectionLength].remove(p)
                
    print "\n"            
    return area    # 接続距離ごとに行が分かれている．



# -------------- ピンを補完 -----------------------------------    
def complete_pinIndenList(myface,
                          pinIndexList_comp, # return
                          paramList_comp    # return
                          ) :

    pinIndexList   = myface.parts_vertex[myface.context_parts]
    paramList      = myface.param_list
    pinIndexList_comp[0]  = pinIndexList[0]      # 補完された頂点番号
    paramList_comp[0]     = paramList[0]         # 補完されたカーブ上の位置パラメータ

    for i in range( len(pinIndexList)-1 ) :
        vertex_path = tools.path_search(myface.obj, pinIndexList[i], pinIndexList[i+1])
        #print "start-end",pinIndexList[i], pinIndexList[i+1]
        vertex_path[0].pop(0)
        vertex_path[1].pop(0)
        for ind, v_index in enumerate( vertex_path[0]) :
            pinIndexList_comp.append(v_index)
            paramA  = paramList[i]
            paramB  = paramList[i+1]
            p       = vertex_path[1][ind]
            paramList_comp.append( paramA + ((paramB-paramA)* p))
    # paramList を用いて、curvetool.curPosList　を更新
    curPosList_comp = curvetool.getCurvePoint(myface.curve,paramList_comp,"normal")
    
    print "pinIndexList_comp : ", pinIndexList_comp
    print "paramList_comp : ", paramList_comp

    return curPosList_comp
# --------------------------------------------------
    
    

# 周辺頂点のみの頂点位置と接続関係を出力する．
def exp_vertex_pos_limit(name, area) :
    print "\n - - - exp_vertex_pos_limit - - -"
    dagPath = tools.getDagPath(name)
    #------ 全ての頂点のデータを書き出す -------------
    """
     仕様 ※キーで入れてるので辞書の順番はこの通りではない、インデックスで呼ばないように
     {
         vertex : 
         [
             頂点の座標(n x 1) : []
         ]
         connect[]　：               
     }
    """
    #---------------------------------------------------
    area_flat = []
    for area_v in area :
        for area_p in area_v :
            area_flat.append(area_p)
    
    dict         = {}
    #---- 頂点のイテレータをまわし、保存 -----
    v_ls    = []
    conn_ls = []
    mitMeshVertIns         = om2.MItMeshVertex(dagPath)    
    mitMeshVertIns.reset()                                   # .resetで現在のindexを初期化できます。
    for n in area_flat :
        mitMeshVertIns.setIndex(n)
        pos = mitMeshVertIns.position(om2.MSpace.kWorld)     # <type 'OpenMaya.MPoint'>
        v_ls.append( [pos.x, pos.y, pos.z] )
        
        connectList = mitMeshVertIns.getConnectedVertices()
        # もとのインデックスを新しいインデックス(0から始まる)に変換
        new_connectList = []
        for c in connectList :
            if c in area_flat :
                new_index = area_flat.index(c)
                new_connectList.append(new_index)
        
        conn_ls.append(new_connectList)
             
    # 辞書に入れる
    dict = {}
    dict["vertex"] = v_ls
    dict["connect"] = conn_ls
    
    #print "---------------------------------------------", dict
    
    """
    json_file = open(path, 'w')
    json.dump(dict, json_file)    
    json_file.close()
    """
    return dict


def do_lap_limit(
        myface,
        pinIndexList,       # 補完されてるかもしれないししてないかもしれない
        serch_area,         # 計算する頂点の範囲
        curPosList,         # 補完されてるかもしれないししてないかもしれない
        pin_area_num = 1,    # ピンとして設定する範囲
        debug = False
        ) :

    start  =  time.time()
    obj    =  myface.obj
    print "\n - - - do_lap_limit - - -"
    

    # ---------- 計算する範囲を取得 ----------------------------------------
    area      = serch_close_vertex( myface.name, pinIndexList, serch_area )
    area_flat = []
    for area_v in area :
        for area_p in area_v :
            area_flat.append(area_p)
    print  "serch_area         : 0 to", len(area)-1
    print u"area vertex        :", len(area_flat)
    # ---------------------------------------------------------------------

    # ----------- 現在の頂点情報を取得 -------------------------------------
    data = exp_vertex_pos_limit( myface.name, area)
    vtxPos = data["vertex"]
    connection = data["connect"]
    # ----------------------------------------------------------------------
    
    # 頂点位置をひとまず移動
    for i in range( len( area[0] ) ) :
        #count = 0
        pm.move(obj.vtx[area[0][i]], curPosList[i][0], curPosList[i][1], curPosList[i][2], a = 1)
        #pm.move(obj.vtx[area[0][i]], 0,0,0, a = 1, ws = 1)
        if debug : tools.makeSphere(curPosList[i])
    
    if debug : [tools.makeVector([curPosList[i][j]-vtxPos[i][j] for j in range(3)], vtxPos[i]) for i in range(len(curPosList))]

    pm.refresh()    #これがないとエラーになる？

    
    # pinを設定
    pin_area = [0]
    for i in range(pin_area_num) :
        pin_area.append(len(area) - 1 - i )
    
    u_index = []        # もともとのインデックス
    u_index_new = []    # 制限下でのpinのインデックス
    
    for i in pin_area :
        for p in area[i] :
            u_index.append( p )
            u_index_new.append( area_flat.index(p) )

    print "pin                 :", [i for i in u_index ]
    

    print "num of pins         :", len(u_index) / len(u_index_new)
    
    
    print u"[途中: time]  ", time.time() - start
    
    # 現在位置からmovesを計算
    if len(u_index) == 0 :
        print "ERROR"
        return -1
    # ワールドで渡す
    moves = []
    for i in u_index :
        pos = pm.pointPosition( obj.vtx[i] )
        moves.append( list(pos) )   

    
    """
    for i in range(8):
        print area[0][i], moves[i]
        tools.makeSphere(moves[i])
    """
    print u"[途中: time]  ", time.time() - start
    # ------------------------------------------------------------
    #LapSurを計算
    
    LAP_limit = LaplacianSurfaceEdit(vtxPos, connection)    # ここが重い:最初に定義するべきでは？→ブレンドシェイプ適用後の形状を持ってきているから不可能？
    print u"[途中: time]  ", time.time() - start
    q = LAP_limit.calc_lapEdit( u_index_new, moves, myface.lamda )
    w    =  q.flatten()
    w = w.tolist()
    
    # --------------------------------------------------------------
    
    print u"moved vertexes      :", len(w)/3
    
    
    # ---------------------------------------------------------------------------
    print u"[頂点を移動します．: time]  ", time.time() - start
    dagPath = tools.getDagPath(myface.name)
    mitMeshVertIns         = om2.MItMeshVertex(dagPath)
    mitMeshVertIns.reset()
    for i, index in enumerate(area_flat):
        mitMeshVertIns.setIndex(index)
        #print (w[i*3],w[i*3+1],w[i*3+2])
        mitMeshVertIns.setPosition(om2.MPoint(w[i*3],w[i*3+1],w[i*3+2]), om2.MSpace.kWorld)
    # ------------------------------------------------------------------------------
    
    print u"[終了 : time]  ", time.time() - start

    """
    for i in range(8):
        print area[0][i], [w[i*3],w[i*3+1],w[i*3+2]]
    """


# --------------------------------------------------------------------------------
class LaplacianSurfaceEdit() :

    def __init__(self, vtxPos, connection ) :
        
        self.make_data(vtxPos, connection)

    # u ?ｿｽ?ｿｽ?ｿｽ^?ｿｽ?ｿｽ?ｿｽ?ｿｽ?ｿｽﾈゑｿｽ?ｿｽﾄゑｿｽ?ｿｽv?ｿｽZ?ｿｽﾅゑｿｽ?ｿｽ?ｿｽﾍ囲につゑｿｽ?ｿｽﾄはゑｿｽ?ｿｽ轤ｩ?ｿｽ?ｿｽ?ｿｽﾟ計?ｿｽZ?ｿｽ?ｿｽ?ｿｽ?ｿｽB
    def make_data(
                    self,
                    vtxPos,         # ?ｿｽﾚ難ｿｽ?ｿｽO?ｿｽﾌ抵ｿｽ?ｿｽ_?ｿｽ?ｿｽ?ｿｽW
                    connection      # ?ｿｽﾚ托ｿｽ?ｿｽs?ｿｽ?ｿｽ
                    ) :
        #print u"vtxPos", vtxPos
        #print u"connection", connection

        start  =  time.time()

        np.set_printoptions(threshold=2000)


        n = len(vtxPos)
        self.vtxPos = vtxPos

        # ------- L : L*V_dash = delta -----------------------
        global L
        L = np.zeros((3*n,3*n))
        # ?ｿｽX?ｿｽ?ｿｽ?ｿｽC?ｿｽh?ｿｽﾅは対角?ｿｽ?ｿｽ?ｿｽ?ｿｽ?ｿｽ?ｿｽ?ｿｽ?ｿｽ?ｿｽﾄなゑｿｽ?ｿｽ?ｿｽ?ｿｽ?ｿｽ?ｿｽ?ｿｽ?ｿｽﾇなゑｿｽﾅ？
        
        for i in range(3*n) :
            L[i][i] = 1
        """
        for i in range(n) :
            d  = len(data["connection"][i])
            d_dash = - (1/d)
            for j in range(3) :
                L[3*i+j][3*i+j] = d_dash 
        """
        # ?ｿｽﾚ托ｿｽ?ｿｽs?ｿｽ?ｿｽ?ｿｽ?ｿｽ`?ｿｽ?ｿｽ
        j = 0
        for ls in connection :
            d = len(ls)
            #print "d   :", d
            if d ==0 :
                print ("ERROR : vertex", j, "is INDEPENDENT VERTEX")
                sys.exit()
            
            ######  ☆☆ なぜかPython2だとキャストをしてくれない。　☆☆ #######
            d_dash = - (1 / float(d))
            ###############################################################
            for i in ls :
                #print "connect", d_dash
                for k in range(3) :
                    L[ 3*j + k ][ 3*i + k ] = d_dash
            j+=1
        #print u"L =",L
        #print u"L[1] =", L[1]
        #print L[0][0:10]
        # -----------------------------------------------------
        print u"    --time: calc L--  ", time.time() - start
        # ------------- V -------------------------------------
        global V
        V_temp = np.array(vtxPos)
        V = V_temp.reshape([3*n, 1])
        #print u"V = ",V
        # -----------------------------------------------------

        # --------- delta (?ｿｽ?ｿｽ?ｿｽ?ｿｽ?ｿｽﾊ置?ｿｽﾌ??ｿｽ?ｿｽv?ｿｽ?ｿｽ?ｿｽV?ｿｽA?ｿｽ?ｿｽ?ｿｽ?ｿｽ?ｿｽW) -----------
        global delta
        delta = np.dot(L,V)         # n * 3
        #print u"delta =",delta
        # -----------------------------------------------------
        print u"    --time: calc V delta--  ", time.time() - start
        
        """
        # --------- A+ ----------------------------------------
        A = 0
        for i in range(n) :
            NiAndi = data["connection"][i][:]
            NiAndi.append(i)                    # ?ｿｽ?ｿｽ?ｿｽX?ｿｽg?ｿｽ?ｿｽ?ｿｽﾅの擾ｿｽ?ｿｽﾔに抵ｿｽ?ｿｽ?ｿｽ
            print ("eeeeeee", data["connection"][i])
            
            
            Ai = 0
            for j in NiAndi :
                vk = data["vertex"][j]
                Ai_element = np.array( 
                        [[ vk[0],       0,    vk[2], -1*vk[1],  1,  0,  0 ],
                        [  vk[1], -1*vk[2],       0,    vk[0],  0,  1,  0 ],
                        [  vk[2],    vk[1], -1*vk[0],       0,  0,  0,  1 ] ])
                if type(Ai) is int :
                    Ai  = Ai_element
                else :
                    Ai  = np.concatenate([Ai,Ai_element])

            if type(A) is int :
                A = Ai
            else :
                A = np.concatenate([A,Ai])
        
        print ( "Size of A is",A.shape )

        AT = A.T
        A_plus = np.dot ( np.linalg.inv( np.dot(AT,A) ), AT )
        print ( "Size of A+ is",A_plus.shape )
        print ("test:A+ =\n", A_plus)
        """

        # --------- D_dash ------------------------------------
        #print (n)
        global D_dash
        D_dash = 0 
        D_dash_lst = []
        #D_dash = np.zeros((3*n, 3*n))
        
        
        # ここが重い
        for i in range(n) : 
            
            
            NiAndi = connection[i][:]    # ?ｿｽQ?ｿｽﾆ渡?ｿｽ?ｿｽ?ｿｽﾉ抵ｿｽ?ｿｽ?ｿｽ
            #NiAndi.append(i)                    # ?ｿｽ?ｿｽ?ｿｽX?ｿｽg?ｿｽ?ｿｽ?ｿｽﾅの擾ｿｽ?ｿｽﾔに抵ｿｽ?ｿｽ?ｿｽ
            NiAndi.insert( 0, i )
            #print ("NiAndi =",NiAndi)
            

            
            Ai_lst = []
            for j in NiAndi :
                vk = vtxPos[j]
                Ai_element = np.array( 
                        [[ vk[0],       0,    vk[2], -1*vk[1],  1,  0,  0 ],
                        [  vk[1], -1*vk[2],       0,    vk[0],  0,  1,  0 ],
                        [  vk[2],    vk[1], -1*vk[0],       0,  0,  0,  1 ] ])
                """
                if type(Ai) is int :
                    Ai  = Ai_element
                else :
                    Ai  = np.concatenate([Ai,Ai_element])
                """
                Ai_lst.append(Ai_element)
            Ai = np.concatenate(Ai_lst)

            #print ("i =",i,"\nAi =\n",Ai)
            
            AiT = Ai.T
            Ai_plus = np.dot ( np.linalg.inv( np.dot(AiT,Ai) ), AiT )
            
            
            # --- Di ---
            del_i= [delta[ 3*i ][0], delta[3*i + 1][0], delta[3*i + 2][0] ]
            Di = np.array( 
                    [[ del_i[0],           0,    del_i[2], -1*del_i[1],  0,  0,  0 ],
                    [  del_i[1], -1*del_i[2],           0,    del_i[0],  0,  0,  0 ],
                    [  del_i[2],    del_i[1], -1*del_i[0],           0,  0,  0,  0 ] ])
                    # -----------------------------------------------------------------
                    # Di?ｿｽﾌ右?ｿｽ?ｿｽ?ｿｽ?ｿｽI?ｿｽﾅなゑｿｽ?ｿｽO?ｿｽﾉゑｿｽ?ｿｽ?ｿｽ?ｿｽ?ｿｽ?ｿｽ?ｿｽ?ｿｽ?ｿｽr?ｿｽI?ｿｽ謔｢?ｿｽ?ｿｽ?ｿｽﾊゑｿｽ?ｿｽ?ｿｽ?ｿｽ?ｿｽ?ｿｽ?ｿｽﾌゑｿｽ?ｿｽ?ｿｽ?ｿｽA?ｿｽﾈゑｿｽ?ｿｽ?ｿｽ?ｿｽ?う?ｿｽH?ｿｽH
                    # -----------------------------------------------------------------

            # --- Si ---
            Si = np.zeros((3*(len(NiAndi)), 3*n ))
            k = 0
            for j in NiAndi :
                Si[ 3*k  , 3*j   ] = 1
                Si[ 3*k+1, 3*j+1 ] = 1
                Si[ 3*k+2, 3*j+2 ] = 1
                k += 1

            #print ("Di =",Di)
            #print ("Ai+ =",Ai_plus)
            #print ("SI =\n",Si)

            D_dash_i = np.dot( np.dot(Di, Ai_plus), Si )
            #print ("Size of D'i =", D_dash_i.shape)

            # concentenateはいったんリストにまとめて最後に結合すると早い．
            D_dash_lst.append(D_dash_i)
                
            
        #print ("Size of D'=", D_dash.shape  )
        #print ( "D' =\n",D_dash)
        #print ("n =",n)

        
        # --------- L_minus_D ------------------------------------
        D_dash = np.concatenate(D_dash_lst)
        global LminusD
        LminusD =  L - D_dash

        #print u"L-d     :",L, D_dash
        print u"    --time: end--  ", time.time() - start
        
                    

    # u, ?ｿｽ?ｿｽ?ｿｽ?ｿｽ?ｿｽ?ｿｽ?ｿｽﾍ??ｿｽ?ｿｽ?ｿｽ?ｿｽ_?ｿｽ?ｿｽ?ｿｽﾈゑｿｽ?ｿｽﾆ計?ｿｽZ?ｿｽﾅゑｿｽ?ｿｽﾈゑｿｽ?ｿｽ?ｿｽ?ｿｽ?ｿｽ
    def calc_lapEdit(
                    self,
                    u_index, # ?ｿｽs?ｿｽ?ｿｽ?ｿｽﾌイ?ｿｽ?ｿｽ?ｿｽf?ｿｽb?ｿｽN?ｿｽX
                    moves,   # ?ｿｽs?ｿｽ?ｿｽ?ｿｽﾌ移難ｿｽ?ｿｽﾊ置
                    lamda    # ?ｿｽW?ｿｽ?ｿｽ
                    ):
        
        # ?ｿｽ?ｿｽ?ｿｽﾍデ?ｿｽ[?ｿｽ^?ｿｽﾌ撰ｿｽ?ｿｽ?ｿｽ
        
        num_of_pin = len(u_index)
        
        lamda_2 = np.sqrt(lamda)
        
        vtxPos = self.vtxPos
        
        n = len(vtxPos)

        # ---------- U ---------------------------------------
        U = np.zeros((3*num_of_pin, 1))
        for i in range(num_of_pin) :
            #print (U[3*i])
            #print (len(moves), num_of_pin)
            #print (moves[i][0])
            U[3*i  ] = moves[i][0]
            U[3*i+1] = moves[i][1]
            U[3*i+2] = moves[i][2]
            #U[i] = np.array( data["vertex"][u_index[i]] ) + moves[i]

        #print ("U =\n",U)

        # ---------- C ---------------------------------------
        C = np.zeros((3*num_of_pin, 3*n))
        for i in range(num_of_pin) :
            C[3*i  ][3*u_index[i]  ] = 1
            C[3*i+1][3*u_index[i]+1] = 1
            C[3*i+2][3*u_index[i]+2] = 1
        #print ("CV =\n",np.dot(C,V))
        #print (" = ", [data["vertex"][pp] for pp in u_index])
        # -----------------------------------------------------

        # -------- L_dash -------------------------------------
        Cs = lamda_2 * C
        L_dash = np.concatenate([LminusD,Cs]) # n+m * n

        # -------- U_dash -------------------------------------
        Us = lamda_2 * U
        zeros3n_1 = np.zeros((3*n,1)) 
        U_dash = np.concatenate([zeros3n_1,Us]) # n+m * 3

        # -------- V_dash = ANS -------------------------------
        V_dash = np.zeros((n,3))

        L_dash_t = L_dash.T
        LL       = np.dot(L_dash_t, L_dash)
        LL_inv   = np.linalg.inv( LL )
        V_dash   = np.dot( np.dot(LL_inv, L_dash_t), U_dash ) 

        #print ("Vdash =", V_dash)

        # ?ｿｽﾈ会ｿｽ?ｿｽm?ｿｽ?ｿｽ?ｿｽﾟ用
        """
        V_dash_temp = np.dot( np.linalg.inv(L_dash), U_dash )
        print ("V'temp =", V_dash_temp)

        for i in range(n) :
            NiAndi = data["connection"][i][:]    # ?ｿｽQ?ｿｽﾆ渡?ｿｽ?ｿｽ?ｿｽﾉ抵ｿｽ?ｿｽ?ｿｽ
            #NiAndi.append(i)                    # ?ｿｽ?ｿｽ?ｿｽX?ｿｽg?ｿｽ?ｿｽ?ｿｽﾅの擾ｿｽ?ｿｽﾔに抵ｿｽ?ｿｽ?ｿｽ
            NiAndi.insert( 0, i)
            
            Ai = 0
            for j in NiAndi :
                vk = data["vertex"][j]
                Ai_element = np.array( 
                        [[ vk[0],       0,    vk[2], -1*vk[1],  1,  0,  0 ],
                        [  vk[1], -1*vk[2],       0,    vk[0],  0,  1,  0 ],
                        [  vk[2],    vk[1], -1*vk[0],       0,  0,  0,  1 ] ])
                if type(Ai) is int :
                    Ai  = Ai_element
                else :
                    Ai  = np.concatenate([Ai,Ai_element])

            #print ("Ai =\n",Ai)
            AiT = Ai.T
            Ai_plus = np.dot ( np.linalg.inv( np.dot(AiT,Ai) ), AiT )    

            
            Si = np.zeros((3*(len(NiAndi)), 3*n ))
            k = 0
            for j in NiAndi :
                Si[ 3*k  , 3*j   ] = 1
                Si[ 3*k+1, 3*j+1 ] = 1
                Si[ 3*k+2, 3*j+2 ] = 1
                k += 1

            bi = np.dot(Si, V_dash)
            xi = np.dot(Ai_plus, bi)
            print ("x",i,"=",xi.flatten())

        print ("L-D", LminusD)
        print ("(L-D)V'=", np.dot(LminusD,V_dash) )
        print ( "LV'=", np.dot(L,V_dash))

        #print (" pin?ｿｽ?ｿｽ?ｿｽ?ｿｽ?ｿｽ?ｿｽ?ｿｽﾈゑｿｽ(V'=V)?ｿｽﾈゑｿｽADV'?ｿｽ?ｿｽdelta?ｿｽ@?ｿｽ?ｿｽ?ｿｽﾈわち?ｿｽAD?ｿｽ?ｿｽ", np.dot( delta, np.linalg.inv(V) ) )
        """
        return V_dash