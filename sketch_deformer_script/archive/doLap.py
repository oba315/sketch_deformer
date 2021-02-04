# coding:shift-JIS
# pylint: disable = F0401

import pymel.core as pm
import json
import numpy




# - - - - - 辞書を作る(json) - - - - - - - - - - - - -
"""
dict{
    "num_of_pin"               : int
    "u_index" :
        [
            index
        ]
    "moves" :
        [
            移動座標 # WORLD
        ]
    "lamda" :
        
}
"""


slls     = pm.ls(sl = 1)
u_index  = []

#lamda = 1

def show_u() :
    global base
    baseObj = pm.PyNode(base)
    pm.select(baseObj)
    
    pm.mel.doMenuComponentSelectionExt("base", "vertex", 1);
    pm.setToolTo("selectSuperContext")
    
    global u_index
    [pm.select(baseObj.vtx[i], add=1) for i in u_index] 


# u_indexに追加するだけ
def setPin(lst = []) :
    if len(lst) != 0 :
        for i in lst :
            if i not in u_index :
                u_index.append( i )
        
    slls     = pm.ls(sl = 1, fl = 1)
    if len(slls) != 0 and str(type(slls[0])) == "<class 'pymel.core.general.MeshVertex'>":
        for v in slls :
            print v.index()
            if v.index() not in u_index :
                u_index.append( v.index() )
        
    deltemp()
    try :
        tempobj      = pm.listRelatives( pm.listRelatives(slls[0],p=1), p=1 )[0]
        for i in u_index :
            makeSphere( pm.pointPosition(tempobj.vtx[i]) )
    except :
        pass
    
    

# - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def doLap(lamda = 1) :
    
    obj = pm.PyNode("base")
    
    slls     = pm.ls(sl = 1)
    if len(slls) != 0 and str(type(slls[0])) == "<class 'pymel.core.general.MeshVertex'>":
        for v in slls :
            if not v.index() in u_index :
                u_index.append( v.index() )
    
    # 現在位置からmovesを計算
    if len(u_index) == 0 :
        print "ERROR"
        return -1

    # ワールドで渡す
    moves = []
    for i in u_index :
        pos = pm.pointPosition( obj.vtx[i] )
        moves.append( list(pos) )    

    dict = {}
    dict["u_index"] = u_index
    dict["moves"]   = moves
    dict["lamda"]   = lamda
    dict["num_of_pin"] = len(u_index) 
    dict["mode"]    = "lapSurOnly"

    print dict
    send = json.dumps(dict)
    print "send     |", send
    
    w = send_data(send)
    print "len(Recieve) :",len(w)
    
    
    
    i = 0
    j = 0
    while i < len(obj.vtx)*3 :
        pm.move( obj.vtx[j],w[i], w[i+1], w[i+2] )
        i += 3
        j += 1
        