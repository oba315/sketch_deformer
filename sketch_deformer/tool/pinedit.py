# coding:shift-JIS
# pylint: disable=F0401

import pymel.core as pm
import maya.api.OpenMaya as om2
import maya.cmds as cmds
import sys

from . import tools
reload (tools)
from . import curvetool
reload (curvetool)
from ..process import doDMP
reload (doDMP) # importだけでは実行時に更新されない。必ずreload.
from . import my_face
reload (my_face)
from ..process import doDMP_constraint
reload (doDMP_constraint)
          
            
class PinEditor() :
    
    def __init__( self, 
                  cur ,                # nt.Transform("name") 
                  base,                # str
                  myface,
                  pinIndexList = [], 
                  paramList = [],
                  prePos = 0,
                  blender = 0,
                  alpha = 0
                  ):
        self.pinIndexList    = pinIndexList
        self.paramList       = paramList
        self.cur             = cur
        self.base_name       = base
        self.base_transform  = pm.PyNode(self.base_name)
        self.ctx             = "paramSetCtx"
        self.paramProgress   = 0.0
        self.paramProgress_befor = 0.0
        
        self.myface = myface

        self.prePos          = prePos
        self.blender         = blender
        self.alpha           = alpha

        self.constParamList    = paramList
        self.constPinIndexList = pinIndexList
        #self.constPinIt        = 0

        # 現在何番目のピンを操作しているのか
        self.no_of_editing_pin = 0
        self.no_of_editing_pin_max = len(pinIndexList)
        
        #self.initialization()
        
        self.make_param_set_cmd()
        pm.setToolTo(self.ctx)
        
        self.make_ui()
        self.update_field(pinIndexList,paramList)
        
        # 現在の口のラインを作成
        self.sph_befor_move = [0]
        self.meke_mouth_line()


        """
        pm.select(self.base_name)
        pm.mel.doMenuComponentSelectionExt("base", "vertex", 1)
        pm.setToolTo("selectSuperContext")
        """
        pm.hilite(self.cur)
          
        
    def make_ui(self,) :
        
        # ストロークプレビュー用のカメラを作成
        try :
            temp = pm.PyNode("pin_edit_cam")
            pm.delete(temp)
        except :
            pass
        self.subCam = cmds.duplicate( 'persp', n= "pin_edit_cam" )
        pm.mel.viewFit( "pin_edit_cam" , self.cur)
        
        
        
        # windowが開かれていたら更新する
        if pm.window('pinEditUI', ex=1) == True:
        	pm.deleteUI('pinEditUI')
        with pm.window("pinEditUI", title="Pin Editor", widthHeight=(470,400) ) as pinEditUI:
            with pm.formLayout() as form :

                # ビュー用UI
                view = cmds.modelEditor(camera="pin_edit_cam")
                cmds.modelEditor( view, edit=True, displayAppearance='wireframe', polymeshes=False)
                
                # 左側UI
                with pm.columnLayout( adjustableColumn=True, rowSpacing=8) as column:
                    pm.button (
                            label  = "次のピンへ",
                            c      = self.next_pin,  # （）をつけた関数は置けない。
                                                    #  →引数が欲しいときはpartialを使う。また、関数には*argsが必要
                            h = 20
                        )
                    pm.button (
                            label  = "前のピンへ",
                            c      = self.previous_pin,  # （）をつけた関数は置けない。
                                                    #  →引数が欲しいときはpartialを使う。また、関数には*argsが必要
                            h = 20
                        )
                    pm.button (
                            label  = "ピンとして追加",
                            c      = self.add_pin,  # （）をつけた関数は置けない。
                                                    #  →引数が欲しいときはpartialを使う。また、関数には*argsが必要
                            h = 20
                        )
                    pm.button (
                            label  = "初期化",
                            c      = self.initialization,
                            h = 20
                        )
                    pm.button (
                            label  = "SHOW",
                            c      = self.show_pin,
                            h = 20
                        )
                    self.dmp_synchronize =  pm.checkBox(
                            label = "BSを同期"
                        )
                    


                    
                
                # 下側UI
                with pm.columnLayout( adjustableColumn=True, rowSpacing=0) as bottom_column :
                    self.pins_field  = pm.scrollField(
                                            text = "temp",
                                            editable = False,
                                            h = 24
                                        )
                    self.param_field = pm.scrollField(
                                            text = "temp",
                                            editable = False,
                                            h = 24
                                        )
                    
                    
                    
                cmds.formLayout( form, edit=True,
                        attachForm=[
                            (column, 'top', 5),
                            (column, 'left', 0), 
                            (view, 'top', 5), 
                            (view, 'right', 0),
                            (bottom_column, 'left', 0),
                            (bottom_column, 'bottom', 0),
                            (bottom_column, 'right', 0)], 
                        attachNone=[
                            (column, 'bottom'),
                            (column, 'right'),
                            (bottom_column, 'top')], 
                        attachControl=[
                            (view, 'left', 0, column),
                            (view, 'bottom', 0, bottom_column)]
                        )

            

                    
        # ウィンドウ位置を指定
        gMainWindow     = pm.mel.eval('$tmpVar=$gMainWindow') # メインを取得
        mainwindow_top  = cmds.window( gMainWindow, q=True,  topEdge = True)
        mainwindow_left = cmds.window( gMainWindow, q=True,  leftEdge = True)
        pm.window( pinEditUI, e = 1, 
                topEdge   = mainwindow_top + 150   ,
                leftEdge  = mainwindow_left + 500
                ) # 位置を移動         


        #pm.showWindow( pinEditUI )
        
    def meke_mouth_line(self, *args) :
        
        # 現在の口の形を出力
        try :
            pm.delete(pm.PyNode("pinEditor_mouth_line"))
        except :
            pass
        cv = [pm.pointPosition(self.base_transform.vtx[i]) for i in self.pinIndexList ]
        cur = pm.curve(p = cv, n="pinEditor_mouth_line", d = 1)  

        """
        cur = 
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
        cur     = pm.curve( p = cv, n=test, d = 1 )   
        """

        # 現在のピン(移動前)を出力
        for i in self.sph_befor_move :
            print i
            try :
                pm.delete(i)
                print "deleted"
            except :
                pass

        
        self.sph_befor_move = [ 
                    tools.makeSphere(
                        pm.pointPosition(self.base_transform.vtx[i])
                        ) for i in self.pinIndexList 
                    ] 

        """
        # 現在のピン(移動後)を出力
        temp = [ tools.makeSphere( 
                        curvetool.getCurvePoint(
                                        self.cur, 
                                        [i]
                        )[0]
                )       
                for i in self.paramList ]
        
        self.sph_after_move = [i[0] for i in temp]
        """
        return cur 


    def next_pin(self, *args) :
        print u" - - - 次のピンへ移動します。- - - "
        self.no_of_editing_pin += 1
        if self.no_of_editing_pin == self.no_of_editing_pin_max :
            self.no_of_editing_pin = 0
        print u"no_of_editing_pin  :", self.no_of_editing_pin
        print u"parameter          :", self.paramList[self.no_of_editing_pin]

        #index = self.constPinIndexList[self.constPinIt]
        
        # 球を強調する
        index = self.constPinIndexList[self.no_of_editing_pin]
        v = pm.PyNode(self.base_name).vtx[index]
        try :
            pm.delete(pm.PyNode("tempmouth"))
        except :
            pass
        pos = pm.pointPosition(v)
        sp = pm.sphere(n = "tempmouth", r=0.3)[0]
        pm.move(sp,[pos[0],pos[1],pos[2]])
        
        #self.constPinIt += 1

    def previous_pin(self, *args) :
        print u" - - - 前のピンへ移動します。- - - "
        if self.no_of_editing_pin != 0 :
            self.no_of_editing_pin -= 1
        else :
            self.no_of_editing_pin = self.no_of_editing_pin_max - 1

        print u"no_of_editing_pin  :", self.no_of_editing_pin
        print u"parameter          :", self.paramList[self.no_of_editing_pin]

        # 球を強調する
        index = self.constPinIndexList[self.no_of_editing_pin]
        v = pm.PyNode(self.base_name).vtx[index]
        try :
            pm.delete(pm.PyNode("tempmouth"))
        except :
            pass
        pos = pm.pointPosition(v)
        sp = pm.sphere(n = "tempmouth", r=0.3)[0]
        pm.move(sp,[pos[0],pos[1],pos[2]])


    # 選択されている頂点を、ピンとして追加する。
    def add_pin(self, *args) :
        print "- - - Add pins - - -"

        index = self.no_of_editing_pin
        
        slls = pm.ls(sl = 1, fl = 1)
        if len(slls) == 1 and str(type(slls[0])) == "<class 'pymel.core.general.MeshVertex'>" :
            self.pinIndexList.insert(index, slls[0].index())
            self.paramList.insert(index, 0.0)
            # 対応点編集モードへ
            pm.setToolTo(self.ctx)
            self.next_pin()
            self.update_field(self.pinIndexList,self.paramList)
            
        else :
            print "頂点を１つだけ選択してください"
    
    
    def initialization(self, *args) :
        self.paramList     = self.constParamList
        tools.deltemp()
        
    def get_pinIndexList(self, *args ) :
        return self.pinIndexList    
        
    def get_paramList(self, ) :
        return self.paramList
        
    def show_pin(self, *args) :
        print self.get_pinIndexList()
        print self.get_paramList()
        
    def update_field(self, pinIndexList, paramList) :
        text1 = u" pins   |"
        text2 = u" params |"
        for i in pinIndexList :
            text1 += "{:>6}".format(i)
        for i in paramList :
            text2 += "{:>6}".format("{:.2f}".format(i))

        pm.scrollField( self.pins_field,  e=1, text = text1 )
        pm.scrollField( self.param_field, e=1, text = text2 )
        
        
        
    #----------パラメータのセット-------------
    def make_param_set_cmd(self, ) :
        
        ctx = self.ctx
        print self.ctx
        if cmds.draggerContext(ctx, exists=True):
            cmds.deleteUI(ctx)                            # すごく大事！これがないとランタイムエラーを起こす
        
        # Define draggerContext with press and drag procedures
        # command に登録できるのは関数名(　()をつけない　)のみ。
        # また、関数定義側の引数に *args が必要？
        # 引数が必要な場合はpartial関数を使う。　
        cmds.draggerContext(             
                ctx,                 
                pressCommand        =  self.press_cmd, 
                dragCommand         =  self.drag_cmd, 
                releaseCommand      =  self.release_cmd, 
                cursor              =  'hand',
                space               =  "screen"
                )                
        # Set the tool to the sample context created
        # Results can be observed by dragging mouse around main window
        
    
    
    def press_cmd(self, *args) :
        
        ctx            = self.ctx
        print "paramProgress_befor", self.paramProgress_befor
        
        pressPosition              = cmds.draggerContext( ctx, query=True, anchorPoint=True)
        self.drag_star_point       = pressPosition
        print ("Press: " + str(pressPosition))
        
        #self.paramProgress = 0.0
        pos            = curvetool.getCurvePoint(
                                self.cur,
                                [self.paramProgress],
                                "normal"
                                )[0]   
                        # 第二引数でターゲットの初期位置を指定
        
        self.moving_sph       = pm.sphere(n = "moving_sph", r=0.1)[0]
        pm.move( self.moving_sph , [pos[0],pos[1],pos[2]] )
        pm.refresh(f = 1)
        
        # ハイライト
        pm.hilite(self.cur)
        list = pm.ls(type = u'transform')
        for i in list :
            if "temp" in i.name() :
                pm.hilite(i)
    

        
    def drag_cmd(self, *args) :
        ctx            = self.ctx
        index          = self.no_of_editing_pin

        speed          = 1.0 / 1400.0

        dragPosition = cmds.draggerContext( ctx, query=True,dragPoint=True)
        print "Drag       :" + str(dragPosition[0])
        message = str(dragPosition[0]) + ", " + str(dragPosition[1])
        cmds.draggerContext( ctx, edit=True, drawString=message)
        
        drag_len = dragPosition[0] - self.drag_star_point[0]
        #len     = ( om2.MPoint(self.sp) - om2.MPoint(dragPosition) ).length()
        print "drag_len   :",drag_len
        
        param   = drag_len * speed
        param   = param + self.paramProgress
        param   = max( [ min([param,1]), 0.0 ] )
        pos     = curvetool.getCurvePoint(self.cur, [param], "normal")[0]
        pm.move( self.moving_sph , [pos[0],pos[1],pos[2]] )
        self.paramProgressTemp = param
        
        try :
            pm.delete(pm.PyNode("tempVecMouth"))
        except :
            pass
        # 矢印の描画
        ss = pm.pointPosition(self.base_transform.vtx[ self.constPinIndexList[index] ])
        tools.makeVector( 
                        [pos[0]-ss[0],pos[1]-ss[1],pos[2]-ss[2]],
                        ss,
                        "tempVecMouth"
                        )
        
        
        pm.refresh(f = 1)
        
    def release_cmd(self, *args) :
        index = self.no_of_editing_pin

        print "released"
        pm.delete( self.moving_sph )
        self.paramProgress = self.paramProgressTemp

        if pm.objExists( "temp_pinedit_"+str(index) ) :
            pm.delete( pm.PyNode("temp_pinedit_"+str(index)) )
        tools.makeSphere( 
            curvetool.getCurvePoint(
                self.cur, [self.paramProgress], "normal"
                )[0] ,
            0.1,
            "temp_pinedit_"+ str(index))
        
        self.paramList[index] = self.paramProgress

        self.update_field(self.pinIndexList,self.paramList)
        
        """
        pm.select(self.base_name)
        pm.mel.doMenuComponentSelectionExt("base", "vertex", 1)
        pm.setToolTo("selectSuperContext")
        """

        self.myface.param_list = self.paramList

        # DMPを同期
        if pm.checkBox(self.dmp_synchronize, q = 1, v = 1) :
            print "- - - synchronize MP - - -"

            # paramList を用いて、curvetool.curPosList　を更新
            curvetool.curPosList = curvetool.getCurvePoint(
                                        pm.PyNode("projectionCurve"),
                                        self.paramList,
                                        "normal"
                                        )
    
            doDMP_constraint.do_dmp(
                self.myface,
                curvetool.curPosList,
                self.alpha
                )

            tools.deltemp("tempvec")

            self.meke_mouth_line()
        
        

#cur = pm.PyNode("projectionCurve")
#test = PinEditor(cur,base)

#pm.setToolTo(test.ctx)





