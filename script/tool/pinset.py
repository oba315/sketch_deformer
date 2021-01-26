# coding:shift-JIS
# pylint: disable=F0401

import pymel.core as pm
import sys
import time
import maya.api.OpenMaya as om2
import itertools as it


from . import my_face
reload (my_face)
from . import tools
reload (tools)




    

# もっとも近い組み合わせから順番につなげていく．
# 頂点がある程度等間隔で配置されている前提．
def calc_chain(myface, indexes) :

    combinations =  list(it.combinations(indexes, 2))
    print "combinations : ", combinations 
    lenlist = []
    for combi in combinations :
        pos1  =  pm.pointPosition(myface.obj.vtx[combi[0]])
        pos2  =  pm.pointPosition(myface.obj.vtx[combi[1]])
        # (距離，index1, index2)
        lenlist.append( ( (pos1-pos2).length(), combi[0], combi[1] ) )
        
    # 距離がもっとも近いものからソート
    ls = sorted(lenlist)
    print ls
    
    # 採用する接続関係を抜き出す
    necessary = []
    once      = []
    twice     = []
    for count, tup in enumerate( ls ) :
        # 既に二回使われた頂点を含むものは使わない．
        if (tup[1] in twice) or (tup[2] in twice) :
            continue

        for i in [tup[1], tup[2]] :
            if i in once :
                once.remove(i)
                twice.append(i)
            else :
                once.append(i)
        necessary.append((tup[1], tup[2]))
        
        if count >= len(indexes)-1 : break

    print "once : ", once
    print "twice : ", twice
    print "PPPPP necessary : ", necessary
    # 最後に，くっつけてリストを作成
    # 短点のindexはonceに格納され，かつ二つであるはずである．
    # より左の点を採用
    x1 = pm.pointPosition(myface.obj.vtx[once[0]])[0]
    x2 = pm.pointPosition(myface.obj.vtx[once[1]])[0]
    chain = [once[0]] if x1 < x2 else [once[1]]
    
    for i in range(len(indexes)-1):
        for tup in necessary :
            if chain[-1] in tup :
                next = tup[1] if tup[0]==chain[-1] else tup[0]

                print chain[-1], " ", next
                chain.append(next)
                necessary.remove(tup)

                
                break
    
    if necessary != [] :
        print "ERROR necessary : ", necessary

    #print "chain : ", chain
    return chain
    
# myfaceと，設定保存用オブジェクトに頂点を設定
def change_parts_vertex(myface, key) :

    # 選択からピンを設定する．
    slls = pm.ls(sl = 1, fl = 1)
    if not type(slls[0]) == pm.general.MeshVertex :
        print (u"ERROR : 頂点を選択してください．")
    
    indexes = [i.index() for i in slls]

    indexes = calc_chain(myface, indexes)

    print "indexes : ", indexes

    myface.parts_vertex[key] = indexes
    
    # 設定保存用オブジェクトに設定．
    if pm.objExists(myface.param_obj_name) :
        attname = myface.param_obj_name + "." + key
        if pm.objExists(attname) :
            pm.setAttr(attname, indexes)
        else :
            print "Error no attribute ", attname
    else :
        print "Error no obj named ", myface.param_obj_name
            
        
# 上唇と下唇の情報からmouthの頂点情報を再設定
def refresh_mouth(myface) :
    indexes = myface.parts_vertex["upper_mouth"]
    indexes.remove(indexes[-1])

    cp = myface.parts_vertex["lower_mouth"][:]
    cp.reverse()
    indexes.extend(cp)
    indexes.remove(indexes[-1])

    myface.parts_vertex["mouth"] = indexes