# coding:shift-JIS
# pylint: disable=F0401

import json
import os
import maya.api.OpenMaya as om2
import maya.cmds as cmds
import sys
import pymel.core as pm

space = om2.MSpace.kWorld


from . import tools
reload (tools)

def expoert_mesh_data(path) :

    #------ blendshapeの変化量をJsonに書き出す! -------------
    """
    仕様 ※キーで入れてるので辞書の順番はこの通りではない、インデックスで呼ばないように
    {
        data          :
        {
            name_of_BS
        }
        base　：　
        {
            vtx        : [頂点座標],
            connection : [接続頂点]
        }
        
        target : 
        [
            [頂点ごとのblendshapeベクトル]
        ]
    }
    注意
    ブレンドシェイプと同じ名前のオブジェクトを検索し、そこからblendshapeのベクトルを取得しています。
    ブレンドシェイプの元オブジェクトが消えていると書き出せない
    
    """
    #---------------------------------------------------

    # 名前のリスト：ブレンドシェイプの順番に注意

    ObjNameList  = [ "base" ]
    blender      = pm.PyNode('blendShape1')
    #BSlist       = cmds.listAttr(blender + '.w', m=True)
    numOfBS = 0
    for i in blender.w :    # なぜかlenが使えない場合がある．
        numOfBS += 1
        pm.setAttr(i, 0)    # ブレンドシェイプの初期化
    #numOfBS = len(blender.w)

    pm.progressWindow( isInterruptable = 1)

    dict         = {}
    dict["data"] = {}

    dict["data"]["name_of_BS"]  = numOfBS


    # ベースOBJの処理
    name = ObjNameList[0]
    dagPath = tools.getDagPath(name)


    #---- 頂点のイテレータをまわし、保存 -----
    mitMeshVertIns         = om2.MItMeshVertex(dagPath)    

    v_ls = [] 
    con_ls  = []                                    # .resetで現在のindexを初期化できます。
    mitMeshVertIns.reset()
    for n in range(mitMeshVertIns.count()):
        pos = mitMeshVertIns.position(space)     # <type 'OpenMaya.MPoint'>
        v_ls.append( [pos.x, pos.y, pos.z] )     
        # ----- ローカルの方がいい？ -----
        
        #makeSphere(pos, 0.02)
        
        connectList = mitMeshVertIns.getConnectedVertices()
        con_ls.append( [i for i in connectList ])
        mitMeshVertIns.next()


    # 辞書に入れる
    base_dic = {}
    base_dic["vtx"] = v_ls
    base_dic["connection"] = con_ls

    dict[name] = base_dic
        

    # ブレンドシェイプのデータを格納
    # ウエイトを実際に変更し，ベースモデルから位置を取得．
    target = []
    for i in blender.w:
        
        for w in blender.w:
            if w == i :
                pm.setAttr(w,1.0)
            else :
                pm.setAttr(w,0.0)
            
        
            
        #dagPath   =  getDagPath(name)    
        #obj_dic   =  {}                 # 法線など別な情報を保存するときはこのオブジェクトごとの辞書に
        
        #---- 頂点のイテレータ -----
        mitMeshVertIns         = om2.MItMeshVertex(dagPath)    
                            
        # BSベクトルを取得
        v_ls = []
        mitMeshVertIns.reset()
        for n in range(mitMeshVertIns.count()):
            
            pos = mitMeshVertIns.position(space)     # <type 'OpenMaya.MPoint'>
            
            
            basePos = dict["base"]["vtx"][n]
            v_ls.append( [
                    pos.x - basePos[0],
                    pos.y - basePos[1],
                    pos.z - basePos[2]   ] )
            # ----- ローカルの方がいい？ -----
            
            mitMeshVertIns.next()
            
            
            #if i.index() == 1 :
            #    makeVector(v_ls[n], basePos)
            
        
        for vi in v_ls :
            for p in vi :
                if -0.0001 < p < 0.0001 :
                    p = 0
        
        
        print "len(v_ls) : ", len(v_ls)    
        target.append( v_ls )
        
        
        
        if pm.progressWindow(q = 1, isCancelled=1) :
            break

    [pm.setAttr(w,0.0) for w in blender.w]
        
    dict["target"] = target    
    print dict

    print u"jsonファイル" + path + u"を開きます．"
    json_file = open(path, 'w')

    json.dump(dict, json_file)

    json_file.close()

    pm.progressWindow( endProgress = 1)

    """
    json_file = open(path, 'r')
    print type(json.load(json_file)[0])
    json_file.close()
    """
    """
    with open(path, 'r') as json_file:
        data = json.load(json_file)
    """