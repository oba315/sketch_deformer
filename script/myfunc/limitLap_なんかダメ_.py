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

# ---- ?��ߖT?��?��?��_?��?��?��?��?��?��?��?��?��A?��?��?��X?��g?��Ƃ�?��ĕԂ�?��B?��?��?��X?��g?��͍ŏ�?��̒�?��_?��?��?��?��̋�?��?��?��ŊK?��w?��?�� ----
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
    
    # ?��?��O?��?��?��?��?��F?��ŊO?��k?��?��?��_?��ɂ�?��āA?��?��̒�?��_?��Ƃ�?��?��?��ڑ�?��?��?��Ȃ�?��?��?��_?��?��?��?��?��܂�?��B?��̂łƂ肠?��?��?��?��?��?��?��?��݂̂�?��?��?��O(?��ĊO?��k?��?��?��s?��?��?��łȂ�?��Ȃ�)
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
    
    
# ?��?��?��?��̃G?��?��?��A?��?��?��?��?��?��?��I?��u?��W?��F?��N?��g?��Ƃ�?��ĔF?��?��?��?��?��ď�?��?��?��o?��?��
def exp_vertex_pos_limit(name, path, area) :
    print "\n - - - exp_vertex_pos_limit - - -"
    dagPath = tools.getDagPath(name)
    #------ ?��S?��Ă̒�?��_?��̃f?��[?��^?��?��?��?��?��?��?��o?��?�� -------------
    """
     ?��d?��l ?��?��?��L?��[?��œ�?��?��Ă�̂Ŏ�?��?��?��̏�?��Ԃ͂�?��̒ʂ�ł͂Ȃ�?��A?��C?��?��?��f?��b?��N?��X?��ŌĂ΂Ȃ�?��悤?��?��
     {
         vertex : 
         [
             ?��?��?��_?��̍�?��W(n x 1) : []
         ]
         connect[]?��@?��F               
     }
    """
    #---------------------------------------------------
    area_flat = []
    for area_v in area :
        for area_p in area_v :
            area_flat.append(area_p)
    
    dict         = {}
    #---- ?��?��?��_?��̃C?��e?��?��?��[?��^?��?��?��܂킵?��A?��ۑ� -----
    v_ls    = []
    conn_ls = []
    mitMeshVertIns         = om2.MItMeshVertex(dagPath)    
    mitMeshVertIns.reset()                                   # .reset?��Ō�?��݂�index?��?��?��?��?��?��?��?��?��ł�?��܂�?��B
    for n in area_flat :
        mitMeshVertIns.setIndex(n)
        pos = mitMeshVertIns.position(world)     # <type 'OpenMaya.MPoint'>
        v_ls.append( [pos.x, pos.y, pos.z] )
        
        connectList = mitMeshVertIns.getConnectedVertices()
        # ?��?��?��Ƃ̃C?��?��?��f?��b?��N?��X?��?��V?��?��?��?��?��C?��?��?��f?��b?��N?��X(0?��?��?��?��n?��܂�)?��ɕϊ�
        new_connectList = []
        for c in connectList :
            if c in area_flat :
                new_index = area_flat.index(c)
                new_connectList.append(new_index)
        
        conn_ls.append(new_connectList)
             
    # ?��?��?��?��?��ɓ�?��?��?��
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
        pin_area_num = 1    # ?��ŊO?��k?��?��?��牽?��Ԗڂ܂ł�?��s?��?��?��ɂ�?��邩
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
            

    # ?��?��?��_?��?��?��܂�?��J?��[?��u?��̈ʒu?��܂Ŗ�?��?��?��?��莝�?��?��Ă�?��?��(?��ړ�?��?��?��?��?��ɍ�?��W?��?���VSC?��ɂ�?��?��?��ꂽ?��?��Ȃ�?��悵)
    for i in range( len( area[0] ) ) :
        #count = 0
        print u"?��?��?��_", area[0][i], "?��?��?��ړ�?��?��?��܂�?��B : ?��ړ�?��ʒu", curPosList[i]
        pm.move(obj.vtx[area[0][i]], curPosList[i][0], curPosList[i][1], curPosList[i][2], a = 1)
        #makeSphere(curPosList[i])
    
    pm.refresh()
    
    
    # pin?��̐ݒ�
    pin_area = [0]
    for i in range(pin_area_num) :
        pin_area.append(len(area) - 1 - i )
    print "pin_area            :", pin_area
    
    u_index = []        #?��@?��?��?��Ƃ�?��Ƃ̃C?��?��?��f?��b?��N?��X
    u_index_new = []    # ?��?��?��?��?��?��?��ł�pin?��̃C?��?��?��f?��b?��N?��X
    
    for i in pin_area :
        for p in area[i] :
            u_index.append( p )
            u_index_new.append( area_flat.index(p) )
    
    print "len of u_index      :", len(u_index)
    print "len of u_index_new  :", len(u_index_new)
    
    
    
    # ?��?��?��݈ʒu?��?��?��?��moves?��?��?��v?��Z
    if len(u_index) == 0 :
        print "ERROR"
        return -1
    # ?��?��?��[?��?��?��h?��œn?��?��
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
    print "len(Recieve) :", len(w), "?��?�� vertex :", len(w)/3
    
    # ?��ړ�?��ʒu?��?��K?��p
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

    # u ?��?��?��^?��?��?��?��?��Ȃ�?��Ă�?��v?��Z?��ł�?��?��͈͂ɂ�?��Ă͂�?��炩?��?��?��ߌv?��Z?��?��?��?��B
    def make_data(
                    self,
                    vtxPos,         # ?��ړ�?��O?��̒�?��_?��?��?��W
                    connection      # ?��ڑ�?��s?��?��
                    ) :
        

        n = len(vtxPos)
        self.vtxPos = vtxPos

        # ------- L : L*V_dash = delta -----------------------
        global L
        L = np.zeros((3*n,3*n))
        # ?��X?��?��?��C?��h?��ł͑Ίp?��?��?��?��?��?��?��?��?��ĂȂ�?��?��?��?��?��?��?��ǂȂ�ŁH
        
        for i in range(3*n) :
            L[i][i] = 1
        """
        for i in range(n) :
            d  = len(data["connection"][i])
            d_dash = - (1/d)
            for j in range(3) :
                L[3*i+j][3*i+j] = d_dash 
        """
        # ?��ڑ�?��s?��?��?��?��`?��?��
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

        # --------- delta (?��?��?��?��?��ʒu?���??��?��v?��?��?��V?��A?��?��?��?��?��W) -----------
        global delta
        delta = np.dot(L,V)         # n * 3
        #print ("delta =",delta)
        # -----------------------------------------------------

        """
        # --------- A+ ----------------------------------------
        A = 0
        for i in range(n) :
            NiAndi = data["connection"][i][:]
            NiAndi.append(i)                    # ?��?��?��X?��g?��?��?��ł̏�?��Ԃɒ�?��?��
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
            
            
            NiAndi = connection[i][:]    # ?��Q?��Ɠn?��?��?��ɒ�?��?��
            #NiAndi.append(i)                    # ?��?��?��X?��g?��?��?��ł̏�?��Ԃɒ�?��?��
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
                    # Di?��̉E?��?��?��?��I?��łȂ�?��O?��ɂ�?��?��?��?��?��?��?��?��r?��I?��悢?��?��?��ʂ�?��?��?��?��?��?��̂�?��?��?��A?��Ȃ�?��?��?��?��?��H?��H
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
                    

    # u, ?��?��?��?��?��?��?���??��?��?��?��_?��?��?��Ȃ�?��ƌv?��Z?��ł�?��Ȃ�?��?��?��?��
    def calc_lapEdit(
                    self,
                    u_index, # ?��s?��?��?��̃C?��?��?��f?��b?��N?��X
                    moves,   # ?��s?��?��?��̈ړ�?��ʒu
                    lamda    # ?��W?��?��
                    ):
        
        # ?��?��?��̓f?��[?��^?��̐�?��?��
        
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

        # ?��ȉ�?��m?��?��?��ߗp
        """
        V_dash_temp = np.dot( np.linalg.inv(L_dash), U_dash )
        print ("V'temp =", V_dash_temp)

        for i in range(n) :
            NiAndi = data["connection"][i][:]    # ?��Q?��Ɠn?��?��?��ɒ�?��?��
            #NiAndi.append(i)                    # ?��?��?��X?��g?��?��?��ł̏�?��Ԃɒ�?��?��
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

        #print (" pin?��?��?��?��?��?��?��Ȃ�(V'=V)?��Ȃ�ADV'?��?��delta?��@?��?��?��Ȃ킿?��AD?��?��", np.dot( delta, np.linalg.inv(V) ) )
        """
        
        return V_dash

