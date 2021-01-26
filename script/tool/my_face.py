# coding:shift-JIS
# pylint: disable=F0401

import pymel.core as pm
import maya.api.OpenMaya as om2
import sys

from . import tools
reload (tools)
from . import export
reload (export)
from . import curvetool
reload (curvetool)

from ..data import mypath
reload (mypath)

#顔の各パーツをクラスとして格納してはどうか？


class MyFace() :
    # デフォでpublic

    # 定義
    name = "base"                   # 顔オブジェクトの名称
    blender_name = "blendShape1"     # ブレンドシェイプの名称

    mesh_data_path = mypath.mesh_data_path
            # 各ブレンドシェイプでの形状とベースの接続状態を保存するファイル

    # 顔のパーツ
    parts_vertex = {}
    
    parts_vertex["mouth"]             = [3654,  4037, 3658, 3212, 2862, 2846, 4042, 3638]
    #parts_vertex["mouth"]             = [3654, 4040,4038,4037,4044,4039,3659,3658,2863,3214,3218,3212,3213,3215,2862,2857,2858,2845,2846,3217,3216,4042,4041,4043,3638,3637,3650,3649]
    #parts_vertex["nose"]              = [2890,2884,2923,2922,2901,2905,2898,2875]
    parts_vertex["eye_r"]             = [3689,3683,3722,3721,3700,3704,3697,3674]
    parts_vertex["eye_l"]             = [2890,2884,2923,2922,2901,2905,2898,2875]
    parts_vertex["eyebrows_r"]        = [66,  40,  41,  43,  69,  47,  36,  45]
    parts_vertex["eyebrows_l"]        = [57,  31,  29,  28,  54,  33,  24,  35]
    

    context_parts = "mouth"     # 現在操作している顔のパーツ

    param_list = [ 0, 0.12, 0.25, 0.38, 0.50, 0.65, 0.75, 0.85 ]

    # エリアを上書き
    lap_area = {}
    lap_area["eye_r"] = 2
    lap_area["eye_l"] = 2
    lap_area["eyebrows_r"] = 2
    lap_area["eyebrows_l"] = 2

    
    # カーブ情報
    projection_curve_name = "projectionCurve"
    curve = -1      # 投影されたカーブオブジェクト
    curve1 = -1
    curve2 = -1

    blender       = -1
    defaultShape  = []
    obj           = -1

    # いずれ消したい定数
    alpha = 0.5
    lamda = 1.0

    # 単位系
    space = om2.MSpace.kWorld

    # パラメータ保存用オブジェクトの名称
    param_obj_name = "my_face_parameters"

    def __init__(self) :
        
        # 初期状態を保存
        self.blender       = pm.PyNode(self.blender_name)
        [ pm.setAttr(w,0.0) for w in self.blender.w ]
        self.obj           = pm.PyNode(self.name) 
        self.defaultShape  = [ pm.pointPosition(v) for v in self.obj.vtx ]


        # パラメータ保存用オブジェクトから顔パーツのパラメータを設定
        # パラメータがアトリビュートとして存在しない場合，アトリビュートを作成
        if pm.objExists(self.param_obj_name) :
            obj = pm.PyNode(self.param_obj_name)
            for i in self.parts_vertex :
                attname = self.param_obj_name + "." + i
                
                # 各部位の頂点IDを読み込みOR保存
                if pm.objExists(attname) :
                    if pm.getAttr(attname) == None :
                        pm.setAttr(attname, self.parts_vertex[i])
                    self.parts_vertex[i] = pm.getAttr(attname)
                else :
                    pm.addAttr(obj, ln = i, dataType = "Int32Array")
                    pm.setAttr(attname, self.parts_vertex[i])
            
            """
            # メッシュデータのパスを読み込みOR保存
            attname = self.param_obj_name + "." + "mesh_data_path"
            if pm.objExists(attname) :
                self.mesh_data_path = pm.getAttr(attname)
                
            else :
                pm.addAttr(obj, ln = "mesh_data_path", dataType = "string")
                pm.setAttr(attname, self.mesh_data_path)
            """

        else :
            obj = pm.spaceLocator(n = self.param_obj_name)
            for i in self.parts_vertex :
                pm.addAttr(obj, ln = i, dataType = "Int32Array")
                attname = self.param_obj_name + "." + i
                pm.setAttr(attname, self.parts_vertex[i])

        # 所定の名前のカーブオブジェクトがあればカーブオブジェクトを登録
        if pm.objExists("projectionCurve") :
            self.curve = pm.PyNode("projectionCurve")


        # temp
        #self.parts_vertex["mouth"]             = [3654, 4040,4038,4037,4044,4039,3659,3658,2863,3214,3218,3212,3213,3215,2862,2857,2858,2845,2846,3217,3216,4042,4041,4043,3638,3637,3650,3649]
        # パラメタを再設定
        #self.calc_param_mouth(2862)

        
    # -------------------- このクラスの情報を出力 ----------------------------------
    def print_info(self):
        print ("face         : " + self.name)
        print ("parts vertex : " ,)
        print ( self.parts_vertex )
        print ("blend shape  : " + self.blender_name)
        print ("num of vtx   : " + str(len(self.defaultShape)) )
    # ------------------------------------------------------------------------------
        
    
    # -------------- 接続状態とブレンドシェイプの形状をエクスポート -----------------
    def export_mesh_data(self):
        export.expoert_mesh_data(self.mesh_data_path)
    # ------------------------------------------------------------------------------


    # -------------- パラメータを計算 --------------------------------------------
    # 単純に，与えられた頂点インデックス列に対して長さで０～１のパラメータをふる．
    def calc_params_from_vid(self, indexes) :

        pos1   = pm.pointPosition(self.obj.vtx[indexes[0]])
        dist_inc = [0.]
        sumdist = 0
        for i in indexes[1:] :
            pos2 = pm.pointPosition(self.obj.vtx[i])
            dist = (pos2 -pos1).length() 
            pos1 = pos2[:]
            sumdist += dist
            dist_inc.append(sumdist)
            
        
        print dist_inc
        print sumdist

        params = [d / sumdist for d in dist_inc]
        
        print "calc_params : ", params
        return params

    # 0.5にあたるvertexidを与えて，他は長さでパラメータをふる．
    def calc_param_mouth(self, vid50) :
        
        all_id    = self.parts_vertex["mouth"]
        id        = all_id.index(vid50)
        upper_id  = all_id[:id+1]
        lower_id  = all_id[id:]
        lower_id.append(all_id[0])
        print "upper : ", upper_id
        print "lower : ", lower_id

        param_u = self.calc_params_from_vid(upper_id)
        param_l = self.calc_params_from_vid(lower_id)
        
        param_u = [p/2. for p in param_u][0:-1]
        param_l = [p/2. + 0.5 for p in param_l]

        param_u.extend(param_l)
        
        print param_u

    # いったん保留
    def showcurve(self) :
        length = 0.5
        thickness = 0.1
        dist = 1
        
        # カーブ上の点を取得
        resolution = 60
        params   = [i/resolution for i in range(resolution)]
        cv_list  = curvetool.getCurvePoint(self.curve, params, "normal")
        
        # カメラ位置
        cam          =  pm.PyNode(tools.getCamFromModelPanel())
        cam_pos_temp =  pm.getAttr(cam.translate)
        cam_pos      =  om2.MPoint(cam_pos_temp[0],cam_pos_temp[1],cam_pos_temp[2])
        
        # カメラ位置から距離dist，方向各CVとなる点を選ぶ
        points = []
        for cvp in cv_list :
            dl = dist / (cvp - cam_pos).length()
            points.append( dl*cvp + (1-dl)*cam_pos )
        
        # カーブの進行方向，カメラ方向と垂直な方向に上下に目張り
        # シェーダをセット
        print "set shader"
        global shadingEngine
        #pm.sets(shadingEngine, e = 1, forceElement = plane)
        print "fin"



    # 指定したパラメータからカーブ上の位置を表示
    def show_curve_point(self, param, pinMode) :
        p = curvetool.getCurvePoint(self.curve, [param], pinMode)
        print "p : ", p
        tools.makeSphere(p[0])


    def set_context_parts(self, str) :
        self.context_parts = str
        

    # ----- 変数の変更用関数 --------------------------------------
    

    # 頂点をセット
    #def set_parts_vertex(self) :
        
    


#temp = MyFace(
