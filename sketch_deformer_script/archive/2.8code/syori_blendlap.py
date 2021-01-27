# ----注意----
"""
小数点の端っこが切り落とされてるっぽさがある。
"""

import json
import numpy as np
import socket 
import threading 
import sys
import gc
from tqdm import tqdm

np.set_printoptions(linewidth=200)

path_for_dmp      = "C:\\Users\\piedp\\OneDrive\\Labo\\Sketch\\models\\face7.json"
path_for_lapEdit  = "C:/Users/piedp/OneDrive/Labo/Sketch/Script/BlendLap/lap.json"
path_for_lap_limit = "C:/Users/piedp/OneDrive/Labo/Sketch/Script/BlendLap/limitLap/lap.json"

# ----------------サーバーを立てる--------------------------------
SERVER_IP = "127.0.0.1" 
SERVER_PORT = 8080 

# Create socket object (AF_INET -> IPv4 , SOCK_STREAM -> TCP) 
s_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
# Binding ip and port 
s_sock.bind((SERVER_IP, SERVER_PORT)) 
# Number of connection queue 
s_sock.listen(5) 
print ("[*] Server listening | %s:%d" % (SERVER_IP,SERVER_PORT)) 
#----------------------------------------------------------------

# クライアントからデータを受け取ったときの処理
def client_handler(c_sock): 
    
    req  =  c_sock.recv(32768*4) 
    print ("[*] Request    | %s .... %s" % (req[1:200], req[-200:]) )

    dataIn  =  json.loads(req)

    print ("mode        = ", dataIn["mode"])
    if   dataIn["mode"] == "dmpOnly" :
        """
        欲しい情報：ピン（座標→ベクトル、インデックス、数）、alpha
        """

        # -------------- 成型 --------------------------------
        num_of_pin = dataIn["num_of_pin"]
        alpha      = dataIn["alpha"]
        moves      = []
        index      = []
        for i in range(num_of_pin):
            moves.append( dataIn["pin"][i]["position"] )
            index.append( dataIn["pin"][i]["index"] )
        # ----------------------------------------------------

        # -------------- 処理 --------------------------------
        w           =  DmpBlendShape(path_for_dmp, index, moves, alpha).calc_weight() 
        
        w_map = map(str, w)
        res = " ".join(w_map).encode()
        #res = res.encode() + req    # Python３の時はencode()が必要→str型をbytes型に変換
        
        
    elif dataIn["mode"] == "lapSurOnly" :
        """
        欲しい情報：ピン（座標→ワールド、インデックス、数）、lamda
        """
        
        connection = []
        with open(path_for_dmp,"r") as json_file:
            data2         = json.load(json_file)
            connection = data2["base"]["connection"]
        
        with open(path_for_lapEdit, 'r') as json_file:
            data   =  json.load(json_file)     # JSONデータ
            vtxPos =  data["vertex"] 

        

        LAP = LaplacianSurfaceEdit( vtxPos, connection )
        
        u_index = np.array( dataIn["u_index"] )
        moves2   = np.array( dataIn["moves"] )    #WORLD
        lamda   = dataIn["lamda"]
        q    =  LAP.calc_lapEdit( u_index, moves2, lamda)
        w    =  q.flatten()

        w_map = map(str, w)
        res = " ".join(w_map).encode()
        #res = res.encode() + req    # Python３の時はencode()が必要→str型をbytes型に変換

    elif dataIn["mode"] == "lamdaOnly" :
        
        lamda   = dataIn["lamda"]
        q    =  LAP.calc_lapEdit( u_index, moves, lamda)
        w    =  q.flatten()

        w_map = map(str, w)
        res = " ".join(w_map).encode()


    elif dataIn["mode"] == "lap_limit" :
        with open(path_for_lap_limit, 'r') as json_file:
            data   =  json.load(json_file)     # JSONデータ
            vtxPos =  data["vertex"]
            connection = data["connect"] 

        lamda  = dataIn["lamda"]
        u_index = dataIn["u_index"]
        moves = dataIn["moves"]

        LAP_limit = LaplacianSurfaceEdit(vtxPos, connection)

        q = LAP_limit.calc_lapEdit( u_index, moves, lamda )
        w    =  q.flatten()

        w_map = map(str, w)
        res = " ".join(w_map).encode()



    # 送るときにはbytes型になることに注意
    c_sock.send(res) 
    print ("\n[*] Response   | %s ........" % res[1:200] )

    c_sock.close()
    print ("[*] Server listening | %s:%d" % (SERVER_IP,SERVER_PORT)) 


# bytes型をfloatのListに変換
def bytes2list(st):
    
    #print ("st=",st)
    # bytes型で受け取ったものをfloatの配列に変換
    st = st.decode()
    #print ("st=",st)
    lst = str(st)[1:-1].split(", ")
    lst = [float(s) for s in lst]
    return lst



# --------------------------------------------------------------------------------
# 最小二乗法を用いて　重み行列 w を求める
class DmpBlendShape() :
    w_max   = 10.0                           # 重みの最大
    w_min   = -10.0                          # 重みの最小
    
    def __init__(self, jsonPath, pinIndex, moves, alpha):
        self.num_of_pin = len(pinIndex)
        self.alpha = alpha
        self.m     = moves

        with open(jsonPath,"r") as json_file:
            
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            data         = json.load(json_file)
            self.n       = len(data["target"])               # ブレンドシェイプの数
            n            = self.n
            print ("BSの数     |", n)
            num_of_pin   = self.num_of_pin
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            print ("頂点数     |", len(data["target"][0]))

            # いったん、すべての頂点についてBT＊B を求める
            # Lを求める
            self.L = np.zeros((n,n))
            self.BT      = []
            for p in range(num_of_pin):
                self.BT.append ( np.zeros((n,3)) )
                #print (BT[p], p)
                
                for i,vec in enumerate( data["target"] ) :
                    #print (n_name[i])
                    print (vec[ int(pinIndex[p]) ])
                    self.BT[p][i] = vec[ int(pinIndex[p]) ]
                print ("\n")

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
        print ("num_of_pin  = ", self.num_of_pin)
        

        # - - - クリッピング - - -
        w           =  np.clip(w, self.w_min, self.w_max)

        print ("w           = \n",w)
        return w


# --------------------------------------------------------------------------------
class LaplacianSurfaceEdit() :

    def __init__(self, vtxPos, connection ) :
        
        self.make_data(vtxPos, connection)

    # u が与えられなくても計算できる範囲についてはあらかじめ計算する。
    def make_data(
                    self,
                    vtxPos,         # 移動前の頂点座標
                    connection      # 接続行列
                    ) :
        

        n = len(vtxPos)
        self.vtxPos = vtxPos

        # ------- L : L*V_dash = delta -----------------------
        global L
        L = np.zeros((3*n,3*n))
        # スライドでは対角成分を入れてなかったけどなんで？
        
        for i in range(3*n) :
            L[i][i] = 1
        """
        for i in range(n) :
            d  = len(data["connection"][i])
            d_dash = - (1/d)
            for j in range(3) :
                L[3*i+j][3*i+j] = d_dash 
        """
        # 接続行列を形成
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

        # --------- delta (初期位置のラプラシアン座標) -----------
        global delta
        delta = np.dot(L,V)         # n * 3
        #print ("delta =",delta)
        # -----------------------------------------------------

        """
        # --------- A+ ----------------------------------------
        A = 0
        for i in range(n) :
            NiAndi = data["connection"][i][:]
            NiAndi.append(i)                    # リスト内での順番に注意
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
        

        for i in tqdm(range(n)) : 
            
            
            NiAndi = connection[i][:]    # 参照渡しに注意
            #NiAndi.append(i)                    # リスト内での順番に注意
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
                    # Diの右側をIでなく０にした方が比較的よい結果が得られるのだか、なぜだろう？？
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
                    

    # u, もしくはラムダがないと計算できない部分
    def calc_lapEdit(
                    self,
                    u_index, # ピンのインデックス
                    moves,   # ピンの移動位置
                    lamda    # 係数
                    ):
        
        # 入力データの整理
        
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

        # 以下確かめ用
        """
        V_dash_temp = np.dot( np.linalg.inv(L_dash), U_dash )
        print ("V'temp =", V_dash_temp)

        for i in range(n) :
            NiAndi = data["connection"][i][:]    # 参照渡しに注意
            #NiAndi.append(i)                    # リスト内での順番に注意
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

        #print (" pinが動かない(V'=V)なら、DV'＝delta　すなわち、D＝", np.dot( delta, np.linalg.inv(V) ) )
        """
        
        return V_dash


# ---------------------------------------------------------------------------------



# -----MAIN--------------------
while True: 
    client,addr = s_sock.accept() 
    print ("\n[*] Connection | %s:%d" % (addr[0],addr[1]) )

    client_handler_thread = threading.Thread(target=client_handler, args=(client,)) 
    client_handler_thread.start()


