# coding:shift-JIS
# pylint: disable=F0401

import pymel.core as pm
import maya.api.OpenMaya as om2
import time
import sys

space = om2.MSpace.kWorld

# importだけでは実行時に更新されない。必ずreload.
from .tool import tools
reload (tools)
from .tool import curvetool
reload (curvetool)
from .process import doDMP
reload (doDMP)      
from .process import limitLap
reload (limitLap)
from .tool import pinedit
reload (pinedit)
from .process import doDMP_constraint
reload (doDMP_constraint)
from .tool import pinset
reload (pinset)
from .tool import my_face
reload(my_face)
from .search import optimize
reload(optimize)
from .tool import pinedit2
reload (pinedit2)
from .process import multiple
reload(multiple)



def donothing(*args) :
    print "pushed"


def shape_initialization() :
    print u"\n- - - 形状を初期化 - - -"
    start = time.time()
    [ pm.setAttr(w,0.0) for w in blender.w ]
    dagPath = tools.getDagPath(base_name)
    mitMeshVertIns         = om2.MItMeshVertex(dagPath)
    mitMeshVertIns.reset()
    #count = 0
    for n in range(mitMeshVertIns.count()):
        currPos =  mitMeshVertIns.position(space) # <type 'OpenMaya.MPoint'>     
        defPos  =  om2.MPoint(myface.defaultShape[n])
        if currPos != defPos :
            
            mitMeshVertIns.setPosition(defPos, space)
            #count += 1
        
        mitMeshVertIns.next()

    print "[time]  ", time.time() - start
    #print "count ", count


def reset() :
    shape_initialization()
    tools.deltemp()
    tools.deltemp("projectionCurve")
    tools.deltemp("curveshow")


def changeBlender(str) :
    global blender
    blender       = pm.PyNode(str)
    myface.blender = pm.PyNode(str)
    myface.blender_name = str


def changeBase(str) :
    global base
    global base_name
    try :
        base         = pm.PyNode(str)
        base_name    = str
        myface.name = str
        myface.obj = pm.PyNode(str)
    except :
        print "オブジェクト",str,"が存在しません"
    

def changeRef(str) :
    global ref
    try :
        ref          = pm.PyNode(str)
    except :
        print "オブジェクト",str,"が存在しません"
        
        
# カーブ描画の開始        
def startTool(ctx) :
    [ pm.setAttr(w,0.0) for w in blender.w ]
    pm.setToolTo(ctx)
    tools.deltemp()
   


# - - - - - -  ピンの修正 - - - - - - - - - - - - - - 
def edit_pin2() :
    pinEditor = pinedit2.PinEditor(myface)

    

# - - - - - - - - - - - - - - - - - - - - - - - - - - -


def changeLamda(lamdy) :
    myface.lamda = lamdy
  

# 現在の形状をブレンドシェイプとして保存
def save_as_BS() :
    print u"\n- - - 現在の形状をブレンドシェイプとして保存 - - -"
    start = time.time()
    
    blender2 = "blendLap"
    dup_name = "expression_" +  str( int(pm.currentTime(q = 1)) )

    base = pm.PyNode("base")
    base_dup = pm.duplicate(base, n = dup_name)

    
    # ブレンドシェイプとして追加：とりあえず別なセットに。
    shape_initialization() # ここが重い
    
    if not pm.objExists(blender2) :
        pm.select(base_dup)
        pm.select(base, add = 1)
        pm.blendShape(n = blender2)
    else :
        print base_name
        print dup_name
        print blender2
        index = len( pm.getAttr(pm.PyNode(blender2).w) )
        pm.blendShape(blender2, e=True, t=(base_name, index+1, dup_name , 1),)

    pm.delete(base_dup)
    print "[time]  ", time.time() - start
    

# - - - - - -  変形するパーツを指定 - - - - - - - - - - - - - - 
class my_toggle_button(object):
    ot = []
    def __init__(self, label, command):
        self.command = command
        self.n = 0
        self.inactive_col = [0.4,0.4,0.4]
        self.active_col   = [0.1,0.1,0.1]
        self.b = pm.button(label=label, command=pm.Callback(self.click))
        self.b.setBackgroundColor(self.inactive_col)

    def set_other_button(self, other_button_list) :
        self.ot = other_button_list
    
    def click(self):
        self.b.setBackgroundColor(self.active_col)
        self.command()
        for i in range(len(self.ot)) :
            self.ot[i].b.setBackgroundColor(self.inactive_col)  

    def set_bg_acctive(self):
        self.b.setBackgroundColor(self.active_col)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

# - - - - - - - -  存在確認 - - - - - - - - - - - - - - - - -
if pm.objExists("base") == True :
    global base_name
    base_name        = "base"
    global base 
    base             = pm.PyNode("base")
else :
    print u"ERROR : 名前'base'を持つオブジェクトが存在しません"
    sys.exit()

if pm.objExists("base_ref") == True :
    global refName
    refName         = "base_ref"
    changeRef(refName) 
else :
    print u"ERROR : 名前'base_ref'を持つオブジェクトが存在しません"

if pm.objExists("blendShape1") == True :
    global blender
    blender         =  pm.PyNode("blendShape1")
else :
    print u"ERROR : 名前'blendShape1'を持つオブジェクトが存在しません"



global ctx
ctx             = "makeCurveToolCtx"    # 同じ名前のコンテクストが存在するとランタイムエラーが起きる


##############################
myface = my_face.MyFace()
##############################


# - - - - - - - -  初期状態を保存 - - - - - - - - - - - - - - - - -
#global defaultShape         # 頂点すべての位置 
[ pm.setAttr(w,0.0) for w in blender.w ]
baseObj = pm.PyNode(base) 
#defaultShape = [ pm.pointPosition(v) for v in baseObj.vtx ]

# - - - - - - - - - - - - - - - - - - - - - - - - - - -

#windowが開かれていたら更新する
if pm.window('sketch_deformer_ui', ex=1) == True:
	pm.deleteUI('sketch_deformer_ui')


# -------------------------- UI -----------------------------------------------------

with pm.window("sketch_deformer_ui", title="sketch_deformer_ui", width=300 ) as sketch_deformer_ui:
    with pm.columnLayout( adjustableColumn=True, rowSpacing=0):
        
        
        # ----------------------------------------------------------------------------
        pm.separator(height=20, style ="double")
        
        # 基本的なコマンド
        with pm.frameLayout( label='basic operation', labelAlign='top',  cll = 1, cl = 0) :
        
            with pm.horizontalLayout(spacing = 10):
                pm.button (label = "clean", c =lambda *args:tools.deltemp())
            
                pm.button (
                        label  = "形状の初期化",
                        c      = lambda *args: shape_initialization(),
                        h = 40
                    )

                pm.button(
                    label = "Reset",
                    c = lambda *args : reset(),
                    h = 40
                )

        
        # ----------------------------------------------------------------------------
        pm.separator(height=20, style ="double")


        with pm.frameLayout(label='スケッチの入力', labelAlign='top', cll = 1, cl = 0):
            pm.text( label='スケッチは所定の向きに入力してください' , h = 15)
            with pm.horizontalLayout(spacing = 10):
                pm.button (
                    label   = u"カーブを作成",
                    c       = lambda *args: startTool(ctx),
                    bgc     = [0.3,0,0],
                    h       = 40
                )
                pm.button (
                    label  = u"カーブを表示",
                    c      = lambda *args: 
                                        curvetool.show_sketch_from_name_head( myface ),
                    bgc    = [0,0,0],
                    h      = 40
                )
            with pm.rowLayout(numberOfColumns=2, columnAttach=[(1, 'left', 10)]) :
                saved_curve = pm.textFieldGrp( 
                                text          = u"projectionCurve_save",
                                )
                pm.button(label = u"カーブを再取得",
                          command = lambda *args: 
                                    curvetool.reacquisition_curPosList(
                                        pm.PyNode(
                                            pm.textFieldGrp(saved_curve, q=1, text = 1)
                                            ),
                                        myface.param_list,
                                        myface
                                    )
                )
            
        pm.separator(height=20, style ="double")

        #パラメータを設定し、メインの関数を実行
        with pm.frameLayout( label='Setting', labelAlign='top', borderVisible =1,cll = 1, cl = 1) :
        
            inputBase = pm.textFieldGrp( 
                                    label         = 'base object name',
                                    text          = "base",
                                    changeCommand = lambda value : changeBase(value)
                                    )
            inputRef = pm.textFieldGrp( 
                                    label         = 'reference object name',
                                    text          = "base_ref",
                                    changeCommand = lambda value : changeRef(value)
                                    )
            
            inputBlender = pm.textFieldGrp( 
                                    label         = 'Blendshape set', 
                                    text          = "blendShape1",
                                    changeCommand = lambda value : changeBlender(value)
                                    )
            pm.button ( 
                label = u"ブレンドシェイプを更新",
                c     = lambda *args : myface.export_mesh_data(),
                h = 20
                )
                                    
            
                                    
                
        with pm.columnLayout( adjustableColumn=True, rowSpacing=8):

            with pm.frameLayout( label = u'変形するパーツ', 
                                labelAlign='top', 
                                cll = 1,                       # 折り畳み可能か？
                                cl = 0                         # 折り畳みの初期状態
                                ) :
                    

                with pm.horizontalLayout(spacing = 2):
                    fp1 = my_toggle_button(label=u'口', command=pm.Callback(lambda *args : myface.set_context_parts("mouth")))
                    fp2 = my_toggle_button(label=u'右目', command=pm.Callback(lambda *args : myface.set_context_parts("eye_r")))
                    fp3 = my_toggle_button(label=u'左目', command=pm.Callback(lambda *args : myface.set_context_parts("eye_l")))
                    fp4 = my_toggle_button(label=u'右眉', command=pm.Callback(lambda *args : myface.set_context_parts("eyebrows_r")))
                    fp5 = my_toggle_button(label=u'左眉', command=pm.Callback(lambda *args : myface.set_context_parts("eyebrows_l")))
                    
                    fp1.set_other_button([fp2,fp3, fp4,fp5])
                    fp2.set_other_button([fp1,fp3, fp4,fp5])
                    fp3.set_other_button([fp1,fp2, fp4,fp5])
                    fp4.set_other_button([fp1,fp2, fp3,fp5])
                    fp5.set_other_button([fp1,fp2, fp3,fp4])

                    fp1.set_bg_acctive()
                

                            
        # ----------------------------------------------------------------------------
        pm.separator(height=10, style ="double")
        
            
        
        # ----------------------------------------------------------------------------
        pm.separator(height=10, style ="double")

        with pm.frameLayout( label='Blend Shape', labelAlign='top', borderVisible =0,cll = 1, cl = 0) :
            pm.text( label='Dmp BlendShape setting' , h = 15)
                                            
            # ブレンドシェイプの影響度をUIで指定
            alphaButton = pm.floatSliderGrp( 
                                    label         = 'alpha',
                                    field         = True,
                                    minValue      = 0.00, 
                                    maxValue      = 1.00, 
                                    fieldMinValue = 0.00,
                                    fieldMaxValue = 10.00,
                                    value         = 0.10,
                                    pre           = 2,        # 小数点以下の桁数を指定
                                    #changeCommand = lambda value:changeAlpha(value),
                                    #dragCommand   = lambda value:changeAlpha(value)
                                    # dragCommandでスライド中も実行するようにできる 
                                    )


            # 影響範囲を指定．
            lower_limit = pm.floatSliderGrp( 
                                    label         = 'lower limit',
                                    field         = True,
                                    minValue      = -1.00, 
                                    maxValue      = 1.00, 
                                    fieldMinValue = -10.00,
                                    fieldMaxValue = 10.00,
                                    value         = 0.0,
                                    pre           = 2,        # 小数点以下の桁数を指定
                                    # dragCommandでスライド中も実行するようにできる 
                                    )
            upper_limit = pm.floatSliderGrp( 
                                    label         = 'upper limit',
                                    field         = True,
                                    minValue      = 0, 
                                    maxValue      = 1.00, 
                                    fieldMinValue = -10.00,
                                    fieldMaxValue = 10.00,
                                    value         = 1.0,
                                    pre           = 2,        # 小数点以下の桁数を指定
                                    # dragCommandでスライド中も実行するようにできる 
                                    )

            with pm.horizontalLayout(spacing = 10):
                """
                pm.button (
                        label  = u"制限なしブレンドシェイプ",
                        c      = lambda *args: doDMP.do_dmp_with_my_face( myface, curvetool.curPosList ),
                        h      = 40,
                        bgc    = [0.3, 0.17, 0.04]
                    )
                """
                pm.button (
                    label   = u"一部のみ変形",
                    c       = lambda *args: multiple.do_only_one_parts( 
                                                    myface,
                                                    pm.floatSliderGrp(alphaButton, q = 1, v = 1),
                                                    pm.floatSliderGrp(lower_limit, q = 1, v = 1),
                                                    pm.floatSliderGrp(upper_limit, q = 1, v = 1)  ),
                    h       = 40,
                    bgc     = [0.3, 0.17, 0.04]
                    )

                pm.button (label = u"全体を変形",
                    c       = lambda *args: multiple.do(myface,   pm.floatSliderGrp(alphaButton, q = 1, v = 1),
                                                            pm.floatSliderGrp(lower_limit, q = 1, v = 1),
                                                            pm.floatSliderGrp(upper_limit, q = 1, v = 1)  ),
                    h       = 40,
                    bgc     = [0.3, 0.17, 0.04]
                    )
        
                                
        # ----------------------------------------------------------------------------
        pm.separator(height=10, style ="double")

        with pm.frameLayout( label='Laplacian Edit', labelAlign='top', borderVisible = 0,cll = 1, cl = 0) :
            pm.text( label='LapSurface edit setting' , h = 15)
            with pm.columnLayout( adjustableColumn=True, rowSpacing=5, cw = 5000):
                
                pm.floatSliderGrp( 
                    label         = 'lambda',
                    field         = True,
                    minValue      = 0.00, 
                    maxValue      = 5.00, 
                    fieldMinValue = 0.00,
                    fieldMaxValue = 20.00,
                    value         = 1.0,
                    pre           = 2,        # 小数点以下の桁数を指定
                    changeCommand = lambda value:changeLamda(value)
                    # dragCommandでスライド中も実行するようにできる 
                    )
                    
                serch_area = pm.intSliderGrp( 
                                    label         = 'serch area',
                                    field         = True,
                                    minValue      = 1, 
                                    maxValue      = 20, 
                                    fieldMinValue = 1,
                                    fieldMaxValue = 100,
                                    value         = 8,
                                    # dragCommandでスライド中も実行するようにできる 
                                    )
                
                
                with pm.horizontalLayout(spacing = 10):
                    
                    """
                    pm.button (
                        label  = "Laplacian edit",
                        c      = 'laplacian_cmd()',
                        h      = 40,
                        bgc    = [0.3, 0.17, 0.04]
                    )
                    """

                    pm.button (
                        #label  = "Laplacian edit(completed)",
                        label  = "Laplacian edit(一部)",
                        c      = lambda *args: limitLap.laplacian_cmd_completion(myface, pm.intSliderGrp(serch_area, q=1, v=1)),
                        h      = 40,
                        bgc    = [0.3, 0.17, 0.04]
                    )
                    pm.button (
                        #label  = "Laplacian edit(completed)",
                        label  = "Laplacian edit(全体)",
                        c      = lambda *args: multiple.lap(myface, pm.intSliderGrp(serch_area, q=1, v=1)),
                        h      = 40,
                        bgc    = [0.3, 0.17, 0.04]
                    )

                """
                pm.button(
                    label = u"ブレンドシェイプとして保存",
                    c     = "save_as_BS()",
                    h     = 20 
                )
                """

        # ----------------------------------------------------------------------------
        """
        with pm.frameLayout( label=u'最適化', labelAlign='top', borderVisible = 0,cll = 1, cl = 0) : 
            sample = pm.intSliderGrp( 
                                    label         = 'serch area',
                                    field         = True,
                                    minValue      = 1, 
                                    maxValue      = 20, 
                                    fieldMinValue = 1,
                                    fieldMaxValue = 100,
                                    value         = 8,
                                    # dragCommandでスライド中も実行するようにできる 
                                    )   

            sample = 15
            opt_ids = -1
            opt_curpos = -1

            pm.button (
                    label  = u"おおざっぱな変形",
                    c      = lambda *args: optimize.DMP_search(sample, myface, opt_ids, opt_curpos),
                    h      = 20,
                    bgc    = [0.3, 0.17, 0.04]
                )
            
            pm.button (
                    label  = u"Laplacian edit",
                    c      = lambda *args: optimize.lap(myface, opt_ids, opt_curpos),
                    h      = 20,
                    bgc    = [0.3, 0.17, 0.04]
                )

            pm.button(c = lambda *args : edit_pin2())

        """
        # ----------------------------------------------------------------------------
        pm.separator(height=10, style ="double")
        
        
            
            
            

        
            
        
curvetool.make_curve_tool(ref,myface, "curvature")
pm.showWindow( sketch_deformer_ui )




