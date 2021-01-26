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



def show_sphere(obj_list , name="temp", cur=None, overwrite=True):
    print "スケッチの複製を前に出して見えるようにします．"
    if overwrite :
        if pm.objExists(name) :
            c = pm.PyNode(name)
            pm.delete(c)
    
    for obj in obj_list :
        obj2 = pm.duplicate(obj, n= name )[0]
        
        cam = pm.PyNode(tools.getCamFromModelPanel())

        campos = pm.getAttr(cam.translate)

        ppos = pm.getAttr(obj.translate)
        newpos = ppos + (campos - ppos) * 0.1
        pm.move(obj2, newpos)
    
    
    

class PinEditor() :

    def __init__(self, myface) :
        
        self.myface  = myface
        self.base    = pm.PyNode(self.myface.name)
        self.cur     = myface.curve

        # 口角の位置に球を生成
        self.pinIndexList = myface.parts_vertex[myface.context_parts]
        self.paramList    = myface.param_list
        self.constPinIndexList = self.pinIndexList

        self.mouthcorner_pos  = [pm.pointPosition(self.base.vtx[i]) for i in [self.pinIndexList[0], self.pinIndexList[5]]]
        self.curve_corner_pos = curvetool.getCurvePoint(self.cur, [self.paramList[0],self.paramList[5]])


        self.reflesh_viewer()

        self.ctx             = "paramSetCtx"
        self.make_my_drag_context()
        self.paramProgress   = 0.0
        self.paramProgress_befor = 0.0

        # 現在何番目のピンを操作しているのか
        self.no_of_editing_pin = 0
        self.no_of_editing_pin_max = 1

        pm.setToolTo(self.ctx)
        

    def reflesh_viewer(self) :
        tools.deltemp("temp_pineditor")
        sp  = tools.makeSphere(pos_list= self.mouthcorner_pos, name= "temp_pineditor", r=0.3)
        sp2 = tools.makeSphere(pos_list= self.curve_corner_pos, name= "temp_pineditor", r=0.3)

        show_sphere(sp, "temp_pineditor_p")
        show_sphere(sp2, "temp_pineditor_p")

    # ------------ ドラッグを用いて操作 -------------------
    def make_my_drag_context(self) :
        
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
        
        self.moving_sph       = pm.sphere(n = "temp_pineditor_moving_sph", r=0.1)[0]
        pm.move( self.moving_sph , [pos[0],pos[1],pos[2]] )
        pm.refresh(f = 1)
        
        
    

        
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
            pm.delete(pm.PyNode("temp_pineditor_tempVecMouth"))
        except :
            pass
        # 矢印の描画
        ss = pm.pointPosition(self.base.vtx[ self.constPinIndexList[index] ])
        tools.makeVector( 
                        [pos[0]-ss[0],pos[1]-ss[1],pos[2]-ss[2]],
                        ss,
                        "temp_pineditor_tempVecMouth"
                        )
        
        
        pm.refresh(f = 1)
        
    def release_cmd(self, *args) :
        index = self.no_of_editing_pin

        print "released"
        pm.delete( self.moving_sph )
        self.paramProgress = self.paramProgressTemp

        

        self.myface.param_list = self.paramList

        # DMPを同期
        """
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
        """
       