# coding:shift-JIS
# pylint: disable=F0401


import sys
#myfanc_path = "C:/Program Files/Autodesk/Maya2019/Python/Lib/site-packages"
#if not myfanc_path in sys.path :
#    sys.path.append(myfanc_path )

import maya.api.OpenMaya as om2
import pymel.core as pm
import socket
import json
import os
import time
import numpy as np

world = om2.MSpace.kWorld



# テスト用
def makeSphere(pos = -1, r = 0.1, name = "temp", pos_list=-1 ) :
    if type(pos_list) is int :
        sp = pm.sphere(n = name, r=r)[0]
        pm.move(sp,[pos[0],pos[1],pos[2]])
        
    else :
        sp = []
        for p in pos_list :
            s = pm.sphere(n = name, r=r)[0]
            pm.move(s,[p[0],p[1],p[2]])
            sp.append(s)
    
    return sp
    
   
def makeVector(
        vecs,   # 先の絶対位置ではなく、始点に対する相対位置。
        sources = [0.0, 0.0, 0.0],
        name = "tempvec") :
    #print test
    vec     = pm.dt.Vector([vecs[0], vecs[1], vecs[2]])
    source  = pm.dt.Point([sources[0], sources[1], sources[2]])
    target  = source + vec
    atom    = vec / 6
    opt     = pm.dt.Vector([0.0, 0.0, 1.0])
    unit    = vec.cross(opt)
    unit    = unit * atom.length() / unit.length()
    p1      = target - atom + unit
    p2      = target - atom - unit 
    cvList  = [source, target, p1, target, p2]
    cv      = [ [i[0],i[1],i[2]] for i in cvList]
    #print test
    cur     = pm.curve( p = cv, n=name, d = 1 )   
    
    return cur
 

def makePlane(point, name= "temp") :
    if len(point) != 4 :
        print "4つの座標を入力してください(makePlane)"
    pl = pm.polyPlane(n = name, sx=1, sy=1)
    
    pm.move(pl[0].vtx[0],[point[0][0],point[0][1],point[0][2]])
    pm.move(pl[0].vtx[1],[point[1][0],point[1][1],point[1][2]])
    pm.move(pl[0].vtx[3],[point[2][0],point[2][1],point[2][2]])
    pm.move(pl[0].vtx[2],[point[3][0],point[3][1],point[3][2]])

    return pl[0]
    
# strの含まれるOBJを削除
def deltemp(str = "temp") :
    list = pm.ls(type = u'transform')
    for i in list :
        if str in i.name() :
            pm.delete(i)    #なんだかここがクソ重い
    
    
# ----- ターミナルに送信し、BSウェイトを取得する。 -------------------------------
def getWeight(
            data    # Jsonを用いてテキスト型にしたデータ
            ):
    if type(data) != str :
        print u"ERROR"            
              
    print u"   - - -通信を開始します- - -" 
    host = "127.0.0.1"
    port = 8080

    # Create socket object
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Establish TCP connection
    client.connect((host, port))
    
    # Data send
    client.send(data)

    # Data receive
    data = client.recv(32768)

    w = str2list(data)
    print u"Recieve  |",w
    
    print u"   - - -通信を終了します- - -" 
    return w
    
    
def send_data(
            lst    # Jsonを用いてテキスト型にしたデータ OR DICT
            ):
                
    if type(lst) != 'str' :
        lst = json.dumps(lst)
                
    print u"\n   - - -通信を開始します- - -" 
    host = "127.0.0.1"
    port = 8080
    print u"send     |", lst

    # Create socket object
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Establish TCP connection
    client.connect((host, port))
    
    # Data send
    client.send(str(lst))

    # Data receive
    data = client.recv(65536*2)

    w = str2list(data)
    print u"Recieve  |",w
    
    print u"   - - -通信を終了します- - -\n" 
    return w
    
    
def exp_vertex_pos(name,path) :
    dagPath = getDagPath(name)
    #------ 全ての頂点のデータを書き出す -------------
    """
     仕様 ※キーで入れてるので辞書の順番はこの通りではない、インデックスで呼ばないように
     {
         vertex : 
         [
             頂点の座標(n x 1) : []
         ]               
     }
    """
    #---------------------------------------------------
    dict         = {}
    #---- 頂点のイテレータをまわし、保存 -----
    v_ls    = []
    mitMeshVertIns         = om2.MItMeshVertex(dagPath)    
    mitMeshVertIns.reset()                                   # .resetで現在のindexを初期化できます。
    for i in range(mitMeshVertIns.count()):
        pos = mitMeshVertIns.position(world)     # <type 'OpenMaya.MPoint'>
        v_ls.append( [pos.x, pos.y, pos.z] )
             
        # ----- ローカルの方がいい？ -----
        mitMeshVertIns.next()
    # 辞書に入れる
    dict = {}
    dict["vertex"] = v_ls
    
    #print v_ls[119]
    
    
    print dict
    
    json_file = open(path, 'w')
    json.dump(dict, json_file)    
    json_file.close()


def str2list(st):
    print st
    lst = st[:].split(" ")
    #print lst
    lst = [float(s) for s in lst]
    return lst


# ---- オブジェクト名から　dagPath　を取得 ----------------------
def getDagPath ( name ):
    sel             =  om2.MSelectionList()
    sel.add( name )
    dagPath         =  sel.getDagPath(0) 
    # dagPath.extendToShape()        #メッシュへのパスに変換される
    #print(dagPath.fullPathName())

    return dagPath
    


def mypopup(text = "worning") :
    pm.window(w = 300, h = 100)
    pm.columnLayout()
    pm.text(l = text, w = 300, h = 100, al = "center")
    pm.showWindow()


# ---- アクティブなパネルからカメラの名前を返す ----------------------
def getCamFromModelPanel(panel=None):
    cam = None
    if not panel:
        panel = pm.getPanel(withFocus=True)
    if pm.modelPanel(panel, exists=True):
        # whether panel is modelPanel(viewport) or not
        cam = pm.modelPanel(panel, q=True, camera=True)
    else:
        om2.MGlobal.displayWarning('Active panel is not modelPanel(viewport)!')
        mypopup("ビューポートが非アクティブです．")
        return 0
    return cam
    


#-----レイトレーシングで点をオブジェクトの表面に転写------------------
# 
# 三角ポリゴンのみ
# オブジェクトに回転がかかっているとエラーが起きる
# 
#------------------------------------------------------
def laytomesh(
        dagPath,          # 衝突検知対象のオブジェクトのパス
        cvPos,            # om2.MPoint クラスのオブジェクト / 移動対象
        cam               # カメラのトランスフォームノード
        ):
             
    # カメラデータの成型
    camPostemp = pm.getAttr(cam.translate)
    camShapes  = pm.listRelatives(cam)[0]
    orth       = pm.getAttr(camShapes.orthographic)        # 平行投影ならTrue
    camPos     = om2.MPoint(camPostemp[0],camPostemp[1],camPostemp[2])
    
    
    
    # 視線 とりあえずは平行でもこのままで大丈夫そう?
    if orth :
        print u"[not persp]"
        ray = cvPos - camPos    # MVector
        ray = ray.normal()      
    else :
        ray = cvPos - camPos    # MVector
        ray = ray.normal()      
    
    meshFn = om2.MFnMesh(dagPath)
   
    # ワールドスペース空間指定
    space = om2.MSpace.kWorld
   
    #mfnMeshIns         = om2.MFnMesh(dagPath)      
    mitMeshPolygonIns  = om2.MItMeshPolygon(dagPath)    # MItはイテレータクラス

    length             = 0.0
    returnPoint        = om2.MVector( 0.0, 0.0, 0.0 )
    mitMeshPolygonIns.reset()                          # .resetで現在のindexを初期化できます。
    for n in range(mitMeshPolygonIns.count()):         # .countで全体の長さを調べられます。
        
        #print u"\nface index is",n                      # .indexで現在のindexを調べられます。
        
        #----- フェースごとの処理 -------
        
        faceNormal = mitMeshPolygonIns.getNormal()    # MVector
        #print faceNormal, mitMeshPolygonIns.polygonVertexCount()
        
        
        
        
        #--- MPointの配列として頂点位置を取得 --------
        pointer = []
        i = 0
        for pt in mitMeshPolygonIns.getVertices():    #現在のフェースを構成する頂点のインデックスを取得
            pointer.append( meshFn.getPoint(pt,space) )
            i += 1
            #makeSphere(meshFn.getPoint(pt,space))
            
        #print u"pointer = ", pointer
        #---------------------------------------
        
        if i > 3 :
            print u"ERROR!!! 四角以上のポリゴンが含まれています"
        
        # とりあえず三角ポリゴンのみ
        if faceNormal * ray < 0 :
            
        
            ap = pointer[0]    # MPoint
            bp = pointer[1]
            cp = pointer[2]

            AB = bp - ap
            BC = cp - bp
            CA = ap - cp

            PA = ap - camPos       # MVector
            PB = bp - camPos
            PC = cp - camPos

            # 法線を求める
            nABP = PA ^ AB    #MVector
            nBCP = PB ^ BC
            nCAP = PC ^ CA

            # 内積を求める
            dot = []
            dot.append( nABP * ray )
            dot.append( nBCP * ray )
            dot.append( nCAP * ray )
            
            
            # 交差判定
            if ( dot[0] >= 0 and dot[1] >= 0 and dot[2] >= 0 ) or ( dot[0] <= 0 and dot[1] <= 0 and dot[2] <= 0 ):
                
                """
                makeSphere(ap, 0.01)
                makeSphere(bp, 0.01)
                makeSphere(cp, 0.01)
                makeSphere(camPos, 0.02)
                print n, faceNormal,camPos,cam
                # 法線を出力
                mp0 = om2.MPoint()
                apv = ap- mp0
                bpv = bp- mp0
                cpv = cp- mp0
                gr = (apv+bpv+cpv)/3
                npp = gr + faceNormal
                makeSphere(gr,0.01)
                makeSphere(npp,0.03)
                """
                
                print n,"Crossing!!"
                #---- 交差点の計算 ------
                fa = faceNormal.x
                fb = faceNormal.y
                fc = faceNormal.z
                fx = ap.x
                fy = ap.y
                fz = ap.z
                
                fd = -(fa*fx + fb*fy + fc*fz)

                a1 = ray.x
                b1 = ray.y
                c1 = ray.z

                x1 = camPos.x
                y1 = camPos.y
                z1 = camPos.z

                ft = -(fa*x1 + fb*y1 + fc*z1 + fd) / (fa*a1 + fb*b1 + fc*c1)

                rt = om2.MPoint( x1 + a1*ft, y1 + b1*ft, z1 + c1*ft )
                
                tempLength = (rt - camPos).length()
                
                if(length == 0):
                    length = tempLength
                    returnPoint = rt
                    
                    
                elif length > tempLength :
                    length = tempLength
                    returnPoint = rt
                    
                makeSphere(rt, 0.01)
                
                #makeVector(faceNormal)                
        #--------------------------
        mitMeshPolygonIns.next(1)              # なぜかポリゴンだけnextに引数が必要…？ドキュメントに書いてないんで多分バグ

    if (length != 0) :
        print u"cv is       = ", returnPoint


        return returnPoint

    


    #------- 衝突しなかった場合の処理 -------------
    #
    # 輪郭を構成する中で最も近い頂点の
    # 法線方向に拡張した平面上に打つ？とか？
    #
    # ほんとは法線方向がいいけど、とりあえず最近傍頂点とカメラZが等しい点に打つよ
    # 最近傍頂点の検索　直線と点の距離を回す？
    #
    #---------------------------------------- 
    
    print u"- - - 衝突を検知しませんでした - - -"
  
    #-----　rayとの距離が最も近い頂点を検索 ------------
    nearVtxPos    = om2.MPoint()
    
    # 頂点でイテレータを回す
    mitMeshVertIns         = om2.MItMeshVertex(dagPath)    
    mitMeshVertIns.reset()                                       # .resetで現在のindexを初期化できます。
    for n in range(mitMeshVertIns.count()):
        
        vtxPos       = mitMeshVertIns.position(space)            # <type 'OpenMaya.MPoint'>
        camtoVtx     = om2.MVector( vtxPos.x - camPos.x, vtxPos.y - camPos.y, vtxPos.z - camPos.z )
        
        LL  =  camtoVtx * ray                                    # H = camPos + (LL * ray)
        
        s2  =  (camtoVtx * camtoVtx) - (LL * LL)                 # 距離の二乗
        
        if n == 0:
            print u"update!!! index is ",n, "---",
            cvtoRay     = s2
            nearVtxPos  = camPos + (ray * LL) #om2.MPoint( vtxPos ) 
        elif(cvtoRay > s2):
            print u"update!!! index is ",n, "---",
            cvtoRay     = s2
            nearVtxPos  = camPos + (ray * LL) #om2.MPoint( vtxPos ) 
            
        mitMeshVertIns.next()

    #----- 得た頂点について、ray上の最も近い点を返す
    
    print u"/n"
    return nearVtxPos


# CVの座標のみから最も曲率の高い点を簡易的に求める
def getMostBend(cur) :
    le = len(cur.cv)
    n = 9999
    #point = cur.cv[0]
    
    for i in range(le - 2) :
        p1 = pm.pointPosition (cur.cv[i])
        p2 = pm.pointPosition (cur.cv[i+1])
        p3 = pm.pointPosition (cur.cv[i+2])
        v1 = p2 - p1
        v2 = p3 - p2

        ntemp = v2.dot(v1)
        if ntemp < n :
            n = ntemp
            #point = p2
            index = i+1

    #makeSphere(point)
    return index
    # もっとも曲がっている点の曲率を返す
    # curveFn.getPointAtParam の Param　として使える?
    
    
    
def freeze_blend_shape(obj, blender, defaultShape ) :

    print (" - - - ブレンドシェイプをフリーズします")

    start = time.time()

    if type(obj) == str :
        dagPath = getDagPath(obj)
        obj = pm.PyNode(obj)
    else :
        dagPath = getDagPath(obj.name())
        
    # ------------ 現在の位置を保存 ----------------------------------------------------------------
    tempPointList = []
    mask = []   # 0:置き換えない 1:置き換える
    mitMeshVertIns         = om2.MItMeshVertex(dagPath)    
    mitMeshVertIns.reset()                                   # .resetで現在のindexを初期化できます。
    for i in range(mitMeshVertIns.count()):
        pos = mitMeshVertIns.position(world)     # <type 'OpenMaya.MPoint'>
        if pos[0] == defaultShape[i][0] and pos[1] == defaultShape[i][1] and pos[2] == defaultShape[i][2] :
            mask.append(0)
        else :
            mask.append(1)
        tempPointList.append( pos )
        # ----- ローカルの方がいい？ -----
        mitMeshVertIns.next()
    # ---------------------------------------------------------------------------------------------

    
    # ------------- ブレンドシェイプを初期化 ------------------------------------------------------
    [ pm.setAttr(w,0.0) for w in blender.w ]
    pm.move()
    # -------------------------------------------------------------------------------------------

    print "---------time :", time.time() - start

    # ほぼここで時間がかかってるからjsonから頂点情報を探してもだめかな？
    # ------------ 頂点を移動 ---------------------------------------------------------------------
    mitMeshVertIns.reset()                                   # .resetで現在のindexを初期化できます。
    for i, pos in enumerate(tempPointList):
        if mask[i] == 1 :
            mitMeshVertIns.setPosition(pos, world)     # <type 'OpenMaya.MPoint'>
        mitMeshVertIns.next()
        
    
    print "---------time :", time.time() - start
    


        
# ２頂点間の最短経路を求める[[最短経路の頂点列],[各頂点がどの位置にあるか]]
def path_search(base, index1, index2, search_range = 15) :
    
    s1_connect = [[index1]]
    s2_connect = [[index2]]

    path    = []
    
    dagPath = getDagPath(base.name())
    mitMeshVertIns  = om2.MItMeshVertex(dagPath)
    finish_flag = False
    for i in range(search_range) :
        temp = []
        for v in s1_connect :
            mitMeshVertIns.setIndex(v[0])
            connect = mitMeshVertIns.getConnectedVertices()
            for q in connect :
                flat = []
                for l in s1_connect :
                    flat += l
                if not q in v + flat:
                    for lst in s2_connect :
                        if q in lst :
                            v.reverse()
                            for i in v + lst :
                                path.append(i)
                                #pm.select(base.vtx[i], add = 1)
                            #print u"終了します(1)"
                            finish_flag = True
                            break
                    if finish_flag : break
                    temp.append( [q] + v )
            if finish_flag : break    
        if finish_flag : break
        s1_connect = temp

        temp = []
        for v in s2_connect :
            mitMeshVertIns.setIndex(v[0])
            connect = mitMeshVertIns.getConnectedVertices()
            for q in connect :
                flat = []
                for l in s2_connect :
                    flat += l
                if not q in v + flat:
                    for lst in s1_connect :
                        
                        if q in lst :
                            v.reverse()
                            for i in v + lst :
                                path.append(i)
                                #pm.select(base.vtx[i], add = 1)
                            path.reverse()
                            #print u"終了します(2)"
                            finish_flag = True
                            break
                        
                    if finish_flag : break
                    temp.append( [q] + v )
            if finish_flag : break    
        if finish_flag : break
        s2_connect = temp

    if finish_flag == False :
        print "ERROR 検索範囲を広げてください"

    #print u"path :",path  # 最短経路
    
    
    """
    # 経路を辺で取得
    path_edge = []
    ed = []
    for i in path :
        mitMeshVertIns.setIndex(i)
        ed.append( mitMeshVertIns.getConnectedEdges() )
    for i in range(len(path)-1) :
        for e in ed[i] :
            if e in ed[i+1]:
                path_edge.append(e)
                break
    print "edge =",path_edge
    """

    length = []
    length_sum = 0.0
    for i in range( len(path)-1 ):
        mitMeshVertIns.setIndex(path[i])
        pos1 = mitMeshVertIns.position()
        mitMeshVertIns.setIndex(path[i+1])
        pos2 = mitMeshVertIns.position()

        l = (pos2 - pos1).length()
        length.append( l )
        length_sum += l

    param = [0]
    length_prog = 0.0
    for i in length :
        length_prog += i
        param.append( length_prog/length_sum )

    #print u"param :",param
    
    return [path,param]

    
def calc_bwm(myface, indexes, curposlist) :
    
    m     =  []
    num_of_pin = len(curposlist)
    print num_of_pin
    m = np.zeros((3*num_of_pin, 1))
    for i, p in enumerate( curposlist ) :
        for j, a in enumerate( p ) :
            m[3*i + j][0] = a

    posnow = np.array([[pm.pointPosition(myface.obj.vtx[i]) for i in indexes]])

    tt = posnow.T - m

    return np.linalg.norm(tt, ord=2)
    

def json_export(target, path) :

    json_file = open(path, 'w')
    json.dump(target, json_file)    
    json_file.close()


def json_import(path) :
    
    json_file    = open(path, 'r')
    data         = json.load(json_file)
    json_file.close()
    
    return data
    

def complete_pinIndenList(myface,
                          pinIndexList = None,
                          paramList = None ) :

    if not pinIndexList : pinIndexList  =  myface.parts_vertex[myface.context_parts]
    if not paramList    : paramList     =  myface.param_list
    pinIndexList_comp     = [pinIndexList[0]]      # 補完された頂点番号
    paramList_comp        = [paramList[0]]         # 補完されたカーブ上の位置パラメータ

    for i in range( len(pinIndexList)-1 ) :
        vertex_path = path_search(myface.obj, pinIndexList[i], pinIndexList[i+1])
        #print "start-end",pinIndexList[i], pinIndexList[i+1]
        vertex_path[0].pop(0)
        vertex_path[1].pop(0)
        for ind, v_index in enumerate( vertex_path[0]) :
            pinIndexList_comp.append(v_index)
            paramA  = paramList[i]
            paramB  = paramList[i+1]
            p       = vertex_path[1][ind]
            paramList_comp.append( paramA + ((paramB-paramA)* p))
    
    
    return pinIndexList_comp, paramList_comp
# --------------------------------------------------
    
def cam_info(cam = pm.PyNode("persp"), distance = 100) :
    # 返値:[CameraNode, cam.translata, screen_center, scr_x_axis, scr_y_axis]
    c      =  pm.getAttr(cam.translate)
    pm.move(cam, -1,0,0,r = 1, os = 1, wd = 1)
    moved = pm.getAttr(cam.translate)
    pm.move(cam, 1,0,0,r = 1, os = 1, wd = 1)
    scr_x = moved - c
    pm.move(cam, 0,-1,0,r = 1, os = 1, wd = 1)
    moved = pm.getAttr(cam.translate)
    pm.move(cam, 0,1,0,r = 1, os = 1, wd = 1)
    scr_y = moved - c
    scr_z = scr_x.cross(scr_y)
    scr = c - (distance*scr_z)
    
    return cam, c, scr, scr_x, scr_y


def projection_2D(
        p,      # ワールド座標
        c,      # カメラ位置(ワールド)
        scr,    # スクリーン中心
        scr_x,
        scr_y):
   
    
    k = ( (scr-c)*(scr-c) ) / ( (p-c)*(scr-c) )

    proj = k*(p-c) + c

    v = proj - scr

    #makeSphere(proj,name="tempproj")
    #print "proj", proj
    #print "v", v

    alpha = v*scr_x
    beta  = v*scr_y

    
    return [alpha, beta]


def projection_2D_2(cam_info, poss) :
    pos2d = []
    for p in poss :
        c = cam_info[1]
        scr_minus_c = cam_info[2]-c
        p_minus_c = [p[i]-c[i] for i in [0,1,2]]
        
        k = ( (scr_minus_c)**2 ) / ( (p_minus_c)*(scr_minus_c) )

        proj = k*(p_minus_c) + c
        v = proj - cam_info[2]

        alpha = v*cam_info[3]
        beta  = v*cam_info[4]

        pos2d.append([alpha, beta])

    return pos2d


def maketext(t=u"temptext",name = u"temptext", p=[0,0,0], r=[0,0,0], s=0.1) :
    t = str(t)
    obj = pm.textCurves(n = name, t=t, f ='Courier')
    pm.move(obj[0], p[0],p[1],p[2])
    pm.rotate(obj[0],r[0],r[1],r[2])
    pm.scale(obj[0],s,s,s)
    return obj[0]


