# coding:shift-JIS
# pylint: disable=F0401

import pymel.core as pm
import maya.api.OpenMaya as om2
import sys
import json
import gc
import numpy as np
from tqdm import tqdm

myfanc_path = "C:/Program Files/Autodesk/Maya2019/Python/Lib/site-packages"
if not myfanc_path in sys.path :
    sys.path.append( myfanc_path )

import tools
reload (tools)

world = om2.MSpace.kWorld

# ---- ?ｿｽﾟ傍?ｿｽ?ｿｽ?ｿｽ_?ｿｽ?ｿｽ?ｿｽ?ｿｽ?ｿｽ?ｿｽ?ｿｽ?ｿｽ?ｿｽA?ｿｽ?ｿｽ?ｿｽX?ｿｽg?ｿｽﾆゑｿｽ?ｿｽﾄ返ゑｿｽ?ｿｽB?ｿｽ?ｿｽ?ｿｽX?ｿｽg?ｿｽﾍ最擾ｿｽ?ｿｽﾌ抵ｿｽ?ｿｽ_?ｿｽ?ｿｽ?ｿｽ?ｿｽﾌ具ｿｽ?ｿｽ?ｿｽ?ｿｽﾅ階?ｿｽw?ｿｽ?ｿｽ ----
def serch_close_vertex( obj_name, pinIndexList, connectionLength) :
    print "\n - - - serch_close_vertex - - -"
    area = []
    area.append(pinIndexList)
    
    dagPath = tools.getDagPath(obj_name)
    mitMeshVertIns  = om2.MItMeshVertex(dagPath)
    print "serch range        :",connectionLength
    
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
    
    # ?ｿｽ?ｿｽO?ｿｽ?ｿｽ?ｿｽ?ｿｽ?ｿｽF?ｿｽﾅ外?ｿｽk?ｿｽ?ｿｽ?ｿｽ_?ｿｽﾉつゑｿｽ?ｿｽﾄ、?ｿｽ?ｿｽﾂの抵ｿｽ?ｿｽ_?ｿｽﾆゑｿｽ?ｿｽ?ｿｽ?ｿｽﾚ托ｿｽ?ｿｽ?ｿｽ?ｿｽﾈゑｿｽ?ｿｽ?ｿｽ?ｿｽ_?ｿｽ?ｿｽ?ｿｽ?ｿｽ?ｿｽﾜゑｿｽ?ｿｽB?ｿｽﾌでとりあ?ｿｽ?ｿｽ?ｿｽ?ｿｽ?ｿｽ?ｿｽ?ｿｽ?ｿｽﾌみゑｿｽ?ｿｽ?ｿｽ?ｿｽO(?ｿｽﾄ外?ｿｽk?ｿｽ?ｿｽ?ｿｽs?ｿｽ?ｿｽ?ｿｽﾅなゑｿｽ?ｿｽﾈゑｿｽ)
    for p in area[connectionLength][:] :
        mitMeshVertIns.setIndex(p)
        connectList = mitMeshVertIns.getConnectedVertices()
        
        count = 0
        for i in connectList :
            if i in area[connectionLength-1] or i in area[connectionLength] :
                count += 1
        if count == 1 :
            area[connectionLength].remove(p)
                
                
    return area
    
    
# ?ｿｽ?ｿｽ?ｿｽ?ｿｽﾌエ?ｿｽ?ｿｽ?ｿｽA?ｿｽ?ｿｽ?ｿｽ?ｿｽ?ｿｽ?ｿｽ?ｿｽI?ｿｽu?ｿｽW?ｿｽF?ｿｽN?ｿｽg?ｿｽﾆゑｿｽ?ｿｽﾄ認?ｿｽ?ｿｽ?ｿｽ?ｿｽ?ｿｽﾄ擾ｿｽ?ｿｽ?ｿｽ?ｿｽo?ｿｽ?ｿｽ
def exp_vertex_pos_limit(name, path, area) :
    print "\n - - - exp_vertex_pos_limit - - -"
    dagPath = tools.getDagPath(name)
    #------ ?ｿｽS?ｿｽﾄの抵ｿｽ?ｿｽ_?ｿｽﾌデ?ｿｽ[?ｿｽ^?ｿｽ?ｿｽ?ｿｽ?ｿｽ?ｿｽ?ｿｽ?ｿｽo?ｿｽ?ｿｽ -------------
    """
     ?ｿｽd?ｿｽl ?ｿｽ?ｿｽ?ｿｽL?ｿｽ[?ｿｽﾅ難ｿｽ?ｿｽ?ｿｽﾄゑｿｽﾌで趣ｿｽ?ｿｽ?ｿｽ?ｿｽﾌ擾ｿｽ?ｿｽﾔはゑｿｽ?ｿｽﾌ通ゑｿｽﾅはなゑｿｽ?ｿｽA?ｿｽC?ｿｽ?ｿｽ?ｿｽf?ｿｽb?ｿｽN?ｿｽX?ｿｽﾅ呼ばなゑｿｽ?ｿｽ謔､?ｿｽ?ｿｽ
     {
         vertex : 
         [
             ?ｿｽ?ｿｽ?ｿｽ_?ｿｽﾌ搾ｿｽ?ｿｽW(n x 1) : []
         ]
         connect[]?ｿｽ@?ｿｽF               
     }
    """
    #---------------------------------------------------
    area_flat = []
    for area_v in area :
        for area_p in area_v :
            area_flat.append(area_p)
    
    dict         = {}
    #---- ?ｿｽ?ｿｽ?ｿｽ_?ｿｽﾌイ?ｿｽe?ｿｽ?ｿｽ?ｿｽ[?ｿｽ^?ｿｽ?ｿｽ?ｿｽﾜわし?ｿｽA?ｿｽﾛ托ｿｽ -----
    v_ls    = []
    conn_ls = []
    mitMeshVertIns         = om2.MItMeshVertex(dagPath)    
    mitMeshVertIns.reset()                                   # .reset?ｿｽﾅ鯉ｿｽ?ｿｽﾝゑｿｽindex?ｿｽ?ｿｽ?ｿｽ?ｿｽ?ｿｽ?ｿｽ?ｿｽ?ｿｽ?ｿｽﾅゑｿｽ?ｿｽﾜゑｿｽ?ｿｽB
    for n in area_flat :
        mitMeshVertIns.setIndex(n)
        pos = mitMeshVertIns.position(world)     # <type 'OpenMaya.MPoint'>
        v_ls.append( [pos.x, pos.y, pos.z] )
        
        connectList = mitMeshVertIns.getConnectedVertices()
        # ?ｿｽ?ｿｽ?ｿｽﾆのイ?ｿｽ?ｿｽ?ｿｽf?ｿｽb?ｿｽN?ｿｽX?ｿｽ?ｿｽV?ｿｽ?ｿｽ?ｿｽ?ｿｽ?ｿｽC?ｿｽ?ｿｽ?ｿｽf?ｿｽb?ｿｽN?ｿｽX(0?ｿｽ?ｿｽ?ｿｽ?ｿｽn?ｿｽﾜゑｿｽ)?ｿｽﾉ変奇ｿｽ
        new_connectList = []
        for c in connectList :
            if c in area_flat :
                new_index = area_flat.index(c)
                new_connectList.append(new_index)
        
        conn_ls.append(new_connectList)
             
    # ?ｿｽ?ｿｽ?ｿｽ?ｿｽ?ｿｽﾉ難ｿｽ?ｿｽ?ｿｽ?ｿｽ
    dict = {}
    dict["vertex"] = v_ls
    dict["connect"] = conn_ls
    
    print "---------------------------------------------", dict
    
    json_file = open(path, 'w')
    json.dump(dict, json_file)    
    json_file.close()

    return dict


def do_lap_limit(
        lamda,
        curPosList,
        base_name,
        pinIndexList,
        serch_area,
        path,
        pin_area_num = 1    # ?ｿｽﾅ外?ｿｽk?ｿｽ?ｿｽ?ｿｽ迚ｽ?ｿｽﾔ目までゑｿｽ?ｿｽs?ｿｽ?ｿｽ?ｿｽﾉゑｿｽ?ｿｽ驍ｩ
        ) :
    print "\n - - - do_lap_limit - - -"
    #print "serch_area          : 0 +", len(area)-1

    area   =  serch_close_vertex( base_name, pinIndexList, serch_area )
    ret    =  exp_vertex_pos_limit( base_name, path, area)


            
    obj    =  pm.PyNode(base_name)

    area_flat = []
    for area_v in area :
        for area_p in area_v :
            area_flat.append(area_p)

    print "len_area :",len(area) 
            

    # ?ｿｽ?ｿｽ?ｿｽ_?ｿｽ?ｿｽ?ｿｽﾜゑｿｽ?ｿｽJ?ｿｽ[?ｿｽu?ｿｽﾌ位置?ｿｽﾜで厄ｿｽ?ｿｽ?ｿｽ?ｿｽ?ｿｽ闔晢ｿｽ?ｿｽ?ｿｽﾄゑｿｽ?ｿｽ?ｿｽ(?ｿｽﾚ難ｿｽ?ｿｽ?ｿｽ?ｿｽ?ｿｽ?ｿｽﾉ搾ｿｽ?ｿｽW?ｿｽ?ｼ撰ｿｽVSC?ｿｽﾉゑｿｽ?ｿｽ?ｿｽ?ｿｽ黷ｽ?ｿｽ?ｿｽﾈゑｿｽ?ｿｽ謔ｵ)
    for i in range( len( area[0] ) ) :
        #count = 0
        print u"?ｿｽ?ｿｽ?ｿｽ_", area[0][i], "?ｿｽ?ｿｽ?ｿｽﾚ難ｿｽ?ｿｽ?ｿｽ?ｿｽﾜゑｿｽ?ｿｽB : ?ｿｽﾚ難ｿｽ?ｿｽﾊ置", curPosList[i]
        pm.move(obj.vtx[area[0][i]], curPosList[i][0], curPosList[i][1], curPosList[i][2], a = 1)
        #makeSphere(curPosList[i])
    
    pm.refresh()
    
    
    # pin?ｿｽﾌ設抵ｿｽ
    pin_area = [0]
    for i in range(pin_area_num) :
        pin_area.append(len(area) - 1 - i )
    print "pin_area            :", pin_area
    
    u_index = []        #?ｿｽ@?ｿｽ?ｿｽ?ｿｽﾆゑｿｽ?ｿｽﾆのイ?ｿｽ?ｿｽ?ｿｽf?ｿｽb?ｿｽN?ｿｽX
    u_index_new = []    # ?ｿｽ?ｿｽ?ｿｽ?ｿｽ?ｿｽ?ｿｽ?ｿｽﾅゑｿｽpin?ｿｽﾌイ?ｿｽ?ｿｽ?ｿｽf?ｿｽb?ｿｽN?ｿｽX
    
    for i in pin_area :
        for p in area[i] :
            u_index.append( p )
            u_index_new.append( area_flat.index(p) )
    
    print "len of u_index      :", len(u_index)
    print "len of u_index_new  :", len(u_index_new)
    
    
    
    # ?ｿｽ?ｿｽ?ｿｽﾝ位置?ｿｽ?ｿｽ?ｿｽ?ｿｽmoves?ｿｽ?ｿｽ?ｿｽv?ｿｽZ
    if len(u_index) == 0 :
        print "ERROR"
        return -1
    # ?ｿｽ?ｿｽ?ｿｽ[?ｿｽ?ｿｽ?ｿｽh?ｿｽﾅ渡?ｿｽ?ｿｽ
    moves = []
    for i in u_index :
        pos = pm.pointPosition( obj.vtx[i] )
        moves.append( list(pos) )    
    dict = {}
    dict["u_index"] = u_index_new
    dict["moves"]   = moves
    dict["lamda"]   = lamda
    dict["num_of_pin"] = len(u_index) 
    dict["mode"]    = "lap_limit"

    #[makeSphere(i) for i in moves]

    

    LAP_limit = LaplacianSurfaceEdit(ret["vertex"], ret["connect"])

    q = LAP_limit.calc_lapEdit( u_index_new, moves, lamda )
    print u"q is", q
    w    =  q.flatten()

    """
    for i in range(len(w)/3) :
        tools.makeSphere([w[i+0],w[i+1],w[i+2]])
    """

    #send = json.dumps(dict)
    #w = tools.send_data(dict)
    print "len(Recieve) :", len(w), "?ｿｽ?ｿｽ vertex :", len(w)/3
    
    # ?ｿｽﾚ難ｿｽ?ｿｽﾊ置?ｿｽ?ｿｽK?ｿｽp
    for i in range(len(area_flat)) :
        pm.move( obj.vtx[area_flat[i]], w[i*3],w[i*3+1],w[i*3+2] ) 
    
        
def get_index(pre, area) :
    #global area
    area_flat = []
    for area_v in area :
        for area_p in area_v :
            area_flat.append(area_p)
    return( area_flat[pre] )
    
def highlight_pin(u_index_new, area, baseObj) :
    #global area
    area_flat = []
    for area_v in area :
        for area_p in area_v :
            area_flat.append(area_p)
            
    [pm.select(baseObj.vtx[area_flat[i]], add=1) for i in u_index_new]
            


# --------------------------------------------------------------------------------
class LaplacianSurfaceEdit() :

    def __init__( self, vtxPos, connection ) :
        
        self.make_data( vtxPos, connection )

    # u ?ｿｽ?ｿｽ?ｿｽ^?ｿｽ?ｿｽ?ｿｽ?ｿｽ?ｿｽﾈゑｿｽ?ｿｽﾄゑｿｽ?ｿｽv?ｿｽZ?ｿｽﾅゑｿｽ?ｿｽ?ｿｽﾍ囲につゑｿｽ?ｿｽﾄはゑｿｽ?ｿｽ轤ｩ?ｿｽ?ｿｽ?ｿｽﾟ計?ｿｽZ?ｿｽ?ｿｽ?ｿｽ?ｿｽB
    def make_data(
                    self,
                    vtxPos,         # ?ｿｽﾚ難ｿｽ?ｿｽO?ｿｽﾌ抵ｿｽ?ｿｽ_?ｿｽ?ｿｽ?ｿｽW
                    connection      # ?ｿｽﾚ托ｿｽ?ｿｽs?ｿｽ?ｿｽ
                    ) :
        

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
            if d ==0 :
                print ("ERROR : vertex", j, "is INDEPENDENT VERTEX")
                sys.exit()
            d_dash = - (1 / d)
            for i in ls :
                for k in range(3) :
                    L[ 3*j + k ][ 3*i + k ] = d_dash
            j+=1
        #print ("L =",L)
        # -----------------------------------------------------

        # ------------- V -------------------------------------
        global V
        V_temp = np.array(vtxPos)
        V = V_temp.reshape([3*n, 1])
        #print ("V = ",V)
        # -----------------------------------------------------

        # --------- delta (?ｿｽ?ｿｽ?ｿｽ?ｿｽ?ｿｽﾊ置?ｿｽﾌ??ｿｽ?ｿｽv?ｿｽ?ｿｽ?ｿｽV?ｿｽA?ｿｽ?ｿｽ?ｿｽ?ｿｽ?ｿｽW) -----------
        global delta
        delta = np.dot(L,V)         # n * 3
        #print ("delta =",delta)
        # -----------------------------------------------------

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
        print (n)
        global D_dash
        D_dash = 0 
        #D_dash = np.zeros((3*n, 3*n))
        
        #tqdm
        for i in range(n) : 
            
            
            NiAndi = connection[i][:]    # ?ｿｽQ?ｿｽﾆ渡?ｿｽ?ｿｽ?ｿｽﾉ抵ｿｽ?ｿｽ?ｿｽ
            #NiAndi.append(i)                    # ?ｿｽ?ｿｽ?ｿｽX?ｿｽg?ｿｽ?ｿｽ?ｿｽﾅの擾ｿｽ?ｿｽﾔに抵ｿｽ?ｿｽ?ｿｽ
            NiAndi.insert( 0, i )
            #print ("NiAndi =",NiAndi)
            

            
            Ai = 0
            for j in NiAndi :
                vk = vtxPos[j]
                Ai_element = np.array( 
                        [[ vk[0],       0,    vk[2], -1*vk[1],  1,  0,  0 ],
                        [  vk[1], -1*vk[2],       0,    vk[0],  0,  1,  0 ],
                        [  vk[2],    vk[1], -1*vk[0],       0,  0,  0,  1 ] ])
                if type(Ai) is int :
                    Ai  = Ai_element
                else :
                    Ai  = np.concatenate([Ai,Ai_element])

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
            if type(D_dash) is int :
                D_dash  = D_dash_i
                #print (D_dash.shape)
            else :
                gc.collect()
                temp = D_dash
                #if i == 10:
                #    sys.exit()
                D_dash  = np.concatenate([temp,D_dash_i])
                #print(D_dash.shape, D_dash[0,0])
            #print (i)
        #print ("Size of D'=", D_dash.shape  )
        #print ( "D' =\n",D_dash)
        #print ("n =",n)

        # --------- L_minus_D ------------------------------------
        global LminusD
        LminusD = L - D_dash
                    

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

