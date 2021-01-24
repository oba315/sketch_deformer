# coding:shift-JIS
# pylint: disable=F0401


import maya.cmds as cmds
import maya.api.OpenMaya as om2
import pymel.core as pm
import json
import sys

myfanc_path = "C:/Program Files/Autodesk/Maya2019/Python/Lib/site-packages"
if not myfanc_path in sys.path :
    sys.path.append( myfanc_path )

import tools
reload (tools)

# - - - G L O B A L - - - -


#u_index = []

'''
ref = pm.PyNode("base_ref")
pinIndexList    = [478, 476,  496,  237,  239, 242,  236,  481] 
paramList       = [0.0, 0.13, 0.25, 0.37, 0.5, 0.68, 0.75, 0.83]
'''

global ctx
ctx             = "makeCurveToolCtx"    # 同じ名前のコンテクストが存在するとランタイムエラーが起きるよ

locus_temp = [
    om2.MPoint(0.0,0.0,0.0),
    om2.MPoint(0.0,0.0,0.0),
    om2.MPoint(0.0,0.0,0.0)
]

# 保存したカーブからカーブ位置を再取得
def reacquisition_curPosList(cur, paramList) :
    global curPosList
    curPosList    = getCurvePoint(cur,paramList) # 位置 (MayaAPI) 
    print "curPosLsit (",len(curPosList),") :", curPosList


def SampleContextPress() :
    print "pressed"
    

# 最初に行うコマンド
def prePressCmd() :
    
    print "***prePressCmd***"
    tools.deltemp()
    global cvList
    cvList = []
    global post
    post   = om2.MPoint(0.0,0.0,0.0)

    # 可視ライン用のシェーダを用意
    if not pm.objExists("projection_line_shader") :
        global shadingEngine
        myShader , shadingEngine = pm.createSurfaceShader("surfaceShader")
        pm.rename(myShader, "projection_line_shader")
    else :
        print "すでにライン用シェーダが存在します。"
        myShader = pm.PyNode("projection_line_shader")
        shadingEngine = pm.listConnections(myShader, t='shadingEngine')[0]
        
        

    

# Procedure called on drag
def dragCmd(ref) :
    
    
    span = 0.5    # CVを打つ基準の距離
    
    dragPosition = cmds.draggerContext( ctx, query=True, dragPoint=True)
    post2 = om2.MPoint(dragPosition)
    
    global post
    distance = post - post2
    if distance.length() > span :
        #print "\n", distance.length(),"-------------------------"
                 
        # 衝突判定
        dagPath = tools.getDagPath(ref.name())
        camName   =  tools.getCamFromModelPanel()
        cam       =  pm.PyNode(camName)
        #print "Try to make cv / camera is [",camName, "]"
        projection = tools.laytomesh(
                        dagPath,          # 衝突検知対象のオブジェクトのパス
                        post2,            # om2.MPoint クラスのオブジェクト / 移動対象
                        cam              # カメラのトランスフォームノード
                      )

        
        cvList.append(projection)
        #cvList.append( om2.MPoint(0,0,0) )
        
        
        post = post2
        
        
        
        
        # - - - 可視カーブ - - - - - - - - - - - - -
        length = 0.5
        thickness = 0.1
        cam_pos_temp = pm.getAttr(cam.translate)
        cam_pos  =  om2.MPoint(cam_pos_temp[0],cam_pos_temp[1],cam_pos_temp[2])
        source = projection # om2.MVector
        vec = source - cam_pos
        new_point = cam_pos + (length * vec)
        #tools.makeSphere(new_point, 0.1)

        global locus_temp

        locus = new_point - locus_temp[0]
        normal = (locus ^ vec).normal()
        
        if locus_temp[0] != om2.MPoint([0.0,0.0,0.0]):
            new_point_d = new_point+(thickness*normal)
            new_point_u = new_point-(thickness*normal)
            
            plane = tools.makePlane([
                locus_temp[1],
                new_point_u,
                new_point_d,
                locus_temp[2]
            ])
            
            # シェーダをセット
            global shadingEngine
            pm.sets(shadingEngine, e = 1, forceElement = plane)
        
        else :
            new_point_d = new_point
            new_point_u = new_point

        locus_temp = [
            new_point,
            new_point_u,
            new_point_d
        ]
        
        



        pm.refresh(f = 1)

        # - - - - - - - - - - - - - 
    #button = cmds.draggerContext( ctx, query=True, button=True)
    #modifier = cmds.draggerContext( ctx, query=True, modifier=True)
    #print ("Drag: " + str(dragPosition) + "  Button is " + str(button) + "  Modifier is " + modifier + "\n")
    message = str(dragPosition[0]) + ", " + str(dragPosition[1]) + "aaaaaaaaaaaa"
    cmds.draggerContext( ctx, edit=True, drawString=message)

    print "end"
    pm.refresh()



# マウスを離したときのコマンド
def ReleaseCmd(mode, pinIndexList, paramList, alpha, pinMode) :

    
    #sys.exit()
    
    # - - - - - カーブを作成 - - - - - - - - - - - - - - - 
    cv = [ [i[0],i[1],i[2]] for i in cvList]
    print cv
    try :
        temp = pm.PyNode("projectionCurve")
        pm.delete(temp)
    except :
        pass

    # 謎のエラーが起きてる？
    try :
        cur = pm.curve(p = cv, n="projectionCurve")
    
        global curPosList
        curPosList    = getCurvePoint(cur,paramList) # 位置 (MayaAPI) 
        print "*curPosLsit (",len(curPosList),") :", curPosList


    
    except :
        print "ERROR カーブを作成できません"
    

    global locus_temp   
    locus_temp = [
    om2.MPoint(0.0,0.0,0.0),
    om2.MPoint(0.0,0.0,0.0),
    om2.MPoint(0.0,0.0,0.0)
    ]
    
    #[makeSphere(i, 0.05) for i in curPosList]
    
    

    tools.deltemp()
    
    #do_dmp()

    

    
        
    
    
    
    
    
# カーブの処理 0~1のパラメータから,
# 対応するｃｖの座標を返す
def getCurvePoint(cur, paramList, pinModes = 0) :
    ################
    # pinMode = curvature : 曲率から割り当て
    # pinMode = normal    : そのままの比率で割り当て
    ################
    dagPath    =  tools.getDagPath(cur.name())
    curveFn    =  om2.MFnNurbsCurve(dagPath)
    
    if type(pinModes) == str :
        mode  = pinModes
        
    else :
        print u"ERROR 正しくピンモードを設定して下さい \n Mode: curvature で実行します "
        mode = "curvature"
    
    #--CVの数--
    num_of_CV = curveFn.numCVs
    print "num of CV  :", num_of_CV
    cvs        =  curveFn.length()    # カーブの長さ
    
    
    if mode == "normal" :
        curvePosList = []
        for l in paramList :
            p          =  cvs * l
            param      =  curveFn.findParamFromLength( p ) # 何番目のCVにあたるか
            #print "cvs",cvs,"p",p, "param",param
            space      =  om2.MSpace.kWorld                # ワールドスペースを宣言
            position   =  curveFn.getPointAtParam(param, space)
            
            curvePosList.append(position)
            #makeSphere(position)
    
      
    # 曲率からparamListを修正 - - - - - -
    # 曲率は三次元からとってることに注意
    elif mode == "curvature" :
        curvePosList = []
        p = tools.getMostBend(cur) -1 #WHY
        #print p
        p = float(p)
        max = len(cur.cv) - 3
        #print "p =",p
        newParam = []
        for i in paramList :
            if i <= 0.5 :
                i = 2*p*i
            else :
                i = 2*(max-p)*i + (2*p - max)
            newParam.append(i)
            print "i          :",i
            """
            なぜか終点のパラメータは　<< num_of_CV　-　3 >>　になる。
            それ以上の値をパラメータとして入力すると、<< 必須タイプの項目は見つかりません >> が発生。
            """
            position = curveFn.getPointAtParam(i, om2.MSpace.kWorld)
            
            curvePosList.append(position)                            
            #makeSphere(position)
            
        paramList = newParam
        print "paramList  :",paramList
        
    
    return curvePosList


# - - - MAIN - - - - -
#     ツールの作成
# - - - - - - - - - -  
def make_curve_tool(mode) :
    
     
    if cmds.draggerContext(ctx, exists=True):
        cmds.deleteUI(ctx)                            # すごく大事！これがないとランタイムエラーを起こす
    # Define draggerContext with press and drag procedures
    cmds.draggerContext(             
            ctx,                 
            prePressCommand     =  "curvetool.prePressCmd()", 
            pressCommand        =  "curvetool.SampleContextPress()", 
            dragCommand         =  'curvetool.dragCmd(ref)', 
            releaseCommand      =  'curvetool.ReleaseCmd(mode, pinIndexList, paramList, alpha, pinMode)', 
            cursor              =  'hand',
            space               =  "world"
            );                """ これらの関数の中の変数はグローバルに宣言されていないと使えない？？"""
    # Set the tool to the sample context created
    # Results can be observed by dragging mouse around main window
    
    #cmds.setToolTo(ctx)