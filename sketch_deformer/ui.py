# coding:shift-JIS
# pylint: disable=F0401

import pymel.core as pm
import maya.api.OpenMaya as om2
import time
import sys

space = om2.MSpace.kWorld

# import�����ł͎��s���ɍX�V����Ȃ��B�K��reload.
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
    print "pussed"


def shape_initialization() :
    print u"\n- - - �`��������� - - -"
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


def changeAlpha(alphy) :
    myface.alpha = alphy
    doDMP.do_dmp_with_my_face(myface,curvetool.curPosList)
    

def changeBlender(str) :
    global blender
    blender       = pm.PyNode(str)


def change_pin_mode(str) :
    global pinMode
    pinMode          = str
    print "pinMode :", pinMode
    

def changeBase(str) :
    global base
    global base_name
    try :
        base         = pm.PyNode(str)
        base_name    = str
    except :
        print "�I�u�W�F�N�g",str,"�����݂��܂���"
    

def changeRef(str) :
    global ref
    try :
        ref          = pm.PyNode(str)
    except :
        print "�I�u�W�F�N�g",str,"�����݂��܂���"
        
        
def startTool(ctx) :
    [ pm.setAttr(w,0.0) for w in blender.w ]
    pm.setToolTo(ctx)
    tools.deltemp()
    
    
def change_curve_mode(str):
    global curveMode
    curveMode    = str
    print "curve_mode :",curveMode
    

def pin_editor() :
    print "### PIN EDIT MODE ###"
    global base
    baseObj = pm.PyNode(base)
    pm.select(baseObj)
    
    pm.mel.doMenuComponentSelectionExt("base", "vertex", 1)
    pm.setToolTo("selectSuperContext")
    
    global subPinIndexList
    [pm.select(baseObj.vtx[i], add=1) for i in subPinIndexList] 
    
def sub_pin_editor_add() :
    if pm.currentCtx() != "selectSuperContext" :
        print ("ERROR")
        return -1
    global subPinIndexList
    slls = pm.ls(sl=1, fl=1)
    [subPinIndexList.append(v.index()) for v in slls] 
    
def sub_pin_editor_initialization() :
    global subPinIndexList
    subPinIndexList = []
    
    
def changeLamda(lamdy) :
    global lamda
    lamda = lamdy
    dict = {}
    
    myface.lamda = lamdy
    

# ���݂̌`����u�����h�V�F�C�v�Ƃ��ĕۑ�
def save_as_BS() :
    print u"\n- - - ���݂̌`����u�����h�V�F�C�v�Ƃ��ĕۑ� - - -"
    start = time.time()
    
    blender2 = "blendLap"
    dup_name = "expression_" +  str( int(pm.currentTime(q = 1)) )

    base = pm.PyNode("base")
    base_dup = pm.duplicate(base, n = dup_name)

    
    # �u�����h�V�F�C�v�Ƃ��Ēǉ��F�Ƃ肠�����ʂȃZ�b�g�ɁB
    shape_initialization() # �������d��
    
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
    
    
def edit_pin() :
    cur = pm.PyNode("projectionCurve")
    global pinEditor
    
    pinEditor = pinedit.PinEditor(
                            cur,
                            base,
                            myface,
                            pinIndexList, 
                            paramList,
                            prePos,
                            blender,
                            alpha)
    
def edit_pin2() :
    pinEditor = pinedit2.PinEditor(myface)

def finish_edit_pin() :
    global pinEditor    
    global pinIndexList
    pinIndexList = pinEditor.get_pinIndexList()
    global paramList
    paramList = pinEditor.get_paramList()
    # paramList ��p���āAcurvetool.curPosList�@���X�V
    curvetool.curPosList = curvetool.getCurvePoint(pm.PyNode("projectionCurve"),paramList,"normal")
    if pm.window('pinEditUI', ex=1) == True:
        	pm.deleteUI('pinEditUI')
    
    print "aaaaaaa"

    # prePos���X�V
    #shape_initialization()
    global prePos
    #prePos   = [ pm.pointPosition(base.vtx[i]) for i in pinIndexList ]
    prePos  = [ myface.defaultShape[i] for i in pinIndexList ]

    tools.deltemp()
    

def make_pin_list(
            fix = (-1,-1)
            ) :
    global pinIndexList
    global paramList
    
    pinIndexList = []
    paramList    = [0.0]
    
    slls = pm.ls(sl = 1, fl = 1)
    if type(slls[0]) != pm.general.MeshVertex :
        print "ERROR"
        return -1
        
    edgeLengthList = []
    sumLength = 0
    buffer  = 0
    for i,v in enumerate(slls) :
        pinIndexList.append( v.index() )
        pos = pm.pointPosition(v)
        if i != 0 :
            dist = (pos - buffer).length()
            sumLength += dist
            edgeLengthList.append( sumLength )
            
        buffer = pos
        
    
    for p in edgeLengthList :
        paramList.append( p / sumLength )
    
    if fix[0] != -1 :
        print "unfixed  = ",paramList
        id = 0
        idList = []
        param_befor = 0
        for i, p in enumerate(pinIndexList) :
            
            if id == 0 :
                param_befor = paramList[i]
            if p == fix[0]:
                id = 1
            
            idList.append(id)
            
        for i,p in enumerate(pinIndexList) :
            if idList[i] == 0 :
                paramList[i] = paramList[i] * fix[1] / param_befor
            else :
                if param_befor != 1 :
                    k = (fix[1] - 1) / (param_befor - 1)
                    paramList[i] = k * paramList[i] + (1 - k)            
        
    if len(pinIndexList) != len(paramList) :
        print "ERROR"
        return -1
    print "pinIndex = ",pinIndexList
    print "param    = ",paramList


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
    

# - - - G L O B A L - - - -
global alpha
alpha           = 0.1
global pinMode 
pinMode            = "curvature"

if pm.objExists("base") == True :
    global base_name
    base_name        = "base"
    global base 
    base             = pm.PyNode("base")
else :
    print u"ERROR : ���O'base'�����I�u�W�F�N�g�����݂��܂���"
    sys.exit()

if pm.objExists("base_ref") == True :
    global refName
    refName         = "base_ref"
    changeRef(refName) 
else :
    print u"ERROR : ���O'base_ref'�����I�u�W�F�N�g�����݂��܂���"

if pm.objExists("blendShape1") == True :
    global blender
    blender         =  pm.PyNode("blendShape1")
else :
    print u"ERROR : ���O'blendShape1'�����I�u�W�F�N�g�����݂��܂���"

global lamda
lamda           = 1.0
global curveMode
curveMode       = "mouth"

sub_pin_editor_initialization()

paramList       = [ 0, 0.12, 0.25, 0.38, 0.50, 0.65, 0.75, 0.85 ]
pinIndexList     = [ 3654,  4037, 3658, 3212, 2862, 2846, 4042, 3638 ]


global ctx
ctx             = "makeCurveToolCtx"    # �������O�̃R���e�N�X�g�����݂���ƃ����^�C���G���[���N����

num_of_vtx = len(base.vtx)
"""
for i in pinIndexList :
    if num_of_vtx < i :
        print u"ERROR  �s���̒��_�C���f�b�N�X���S�̂̒��_���𒴂��Ă��܂�"
        sys.exit()
"""


# ������Ԃ�ۑ�
#global defaultShape         # ���_���ׂĂ̈ʒu 
global prePos               # �s���̒��_�̈ʒu
[ pm.setAttr(w,0.0) for w in blender.w ]
baseObj = pm.PyNode(base) 
#defaultShape = [ pm.pointPosition(v) for v in baseObj.vtx ]
prePos        = [ pm.pointPosition(base.vtx[i]) for i in pinIndexList ]


##############################
myface = my_face.MyFace()
##############################


# - - - - - - - - - - - - - -

#window���J����Ă�����X�V����
if pm.window('sketch_deformer_ui', ex=1) == True:
	pm.deleteUI('sketch_deformer_ui')


# -------------------------- UI -----------------------------------------------------

with pm.window("sketch_deformer_ui", title="sketch_deformer_ui", width=300 ) as sketch_deformer_ui:
    with pm.columnLayout( adjustableColumn=True, rowSpacing=0):
        
        
        # ----------------------------------------------------------------------------
        pm.separator(height=20, style ="double")
        
        # ��{�I�ȃR�}���h
        with pm.frameLayout( label='basic operation', labelAlign='top',  cll = 1, cl = 0) :
        
            with pm.horizontalLayout(spacing = 10):
                pm.button (label = "clean", c =lambda *args:tools.deltemp())
            
                pm.button (
                        label  = "�`��̏�����",
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


        with pm.frameLayout(label='�X�P�b�`�̓���', labelAlign='top', cll = 1, cl = 0):
            pm.text( label='�X�P�b�`�͎��v����ɓ��͂��Ă�������' , h = 15)
            with pm.horizontalLayout(spacing = 10):
                pm.button (
                    label   = u"�J�[�u���쐬",
                    c       = lambda *args: startTool(ctx),
                    bgc     = [0.3,0,0],
                    h       = 40
                )
                pm.button (
                    label  = u"�J�[�u��\��",
                    c      = lambda *args: 
                                        curvetool.show_sketch_from_name_head( myface ),
                    bgc    = [0,0,0],
                    h      = 40
                )
            with pm.rowLayout(numberOfColumns=2, columnAttach=[(1, 'left', 10)]) :
                saved_curve = pm.textFieldGrp( 
                                text          = u"projectionCurve_save",
                                )
                pm.button(label = u"�J�[�u���Ď擾",
                          command = lambda *args: 
                                    curvetool.reacquisition_curPosList(
                                        pm.PyNode(
                                            pm.textFieldGrp(saved_curve, q=1, text = 1)
                                            ),
                                        paramList,
                                        myface
                                    )
                )
            
        pm.separator(height=20, style ="double")

        #�p�����[�^��ݒ肵�A���C���̊֐������s
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
                label = u"�u�����h�V�F�C�v���X�V",
                c     = lambda *args : myface.export_mesh_data(),
                h = 20
                )
                                    
            
                                    
                
        with pm.columnLayout( adjustableColumn=True, rowSpacing=8):

            with pm.frameLayout( label = u'�ό`����p�[�c', 
                                labelAlign='top', 
                                cll = 1,                       # �܂��݉\���H
                                cl = 0                         # �܂��݂̏������
                                ) :
                    

                with pm.horizontalLayout(spacing = 2):
                    fp1 = my_toggle_button(label=u'��', command=pm.Callback(lambda *args : myface.set_context_parts("mouth")))
                    fp2 = my_toggle_button(label=u'�E��', command=pm.Callback(lambda *args : myface.set_context_parts("eye_r")))
                    fp3 = my_toggle_button(label=u'����', command=pm.Callback(lambda *args : myface.set_context_parts("eye_l")))
                    fp4 = my_toggle_button(label=u'�E��', command=pm.Callback(lambda *args : myface.set_context_parts("eyebrows_r")))
                    fp5 = my_toggle_button(label=u'����', command=pm.Callback(lambda *args : myface.set_context_parts("eyebrows_l")))
                    
                    fp1.set_other_button([fp2,fp3, fp4,fp5])
                    fp2.set_other_button([fp1,fp3, fp4,fp5])
                    fp3.set_other_button([fp1,fp2, fp4,fp5])
                    fp4.set_other_button([fp1,fp2, fp3,fp5])
                    fp5.set_other_button([fp1,fp2, fp3,fp4])

                    fp1.set_bg_acctive()
                

                            
        # ----------------------------------------------------------------------------
        pm.separator(height=10, style ="double")
        
            
        with pm.frameLayout( label='Pins', labelAlign='top', borderVisible =1,cll = 1, cl = 1) :
                        
            pm.text( label='Pin index list' )                        
            pm.scrollField(                         
                                    text          = str(pinIndexList),
                                    bgc           = [0.3,0.3,0.3],
                                    h             = 20,
                                    editable      = 0
                                    )
            pm.text( label='Pin parameter list' )
            pm.scrollField(   
                                    text          = str(paramList),
                                    bgc           = [0.3,0.3,0.3],
                                    h             = 20,
                                    editable      = 0
                                    )
            pm.button (
                label  = "Edit sub_Pin",
                c      = lambda *args: pin_editor(),
                )
                
            pm.button (
                label  = "Add sub_Pin",
                c      = lambda *args: sub_pin_editor_add(),
                )
            pm.button (
                label  = "Del sub_Pin",
                c      = lambda *args: sub_pin_editor_initialization(),
                )
                                    
            pm.button (
                    label  = u"Edit corresponding point",
                    c      = lambda *args: edit_pin(),
                    h = 20
                )
            pm.button (
                    label  = u"Finish",
                    c      = lambda *args: finish_edit_pin(),
                    h = 20
                )
        # ----------------------------------------------------------------------------
        pm.separator(height=10, style ="double")

        with pm.frameLayout( label='Blend Shape', labelAlign='top', borderVisible =0,cll = 1, cl = 0) :
            pm.text( label='Dmp BlendShape setting' , h = 15)
                                            
            # �u�����h�V�F�C�v�̉e���x��UI�Ŏw��
            alphaButton = pm.floatSliderGrp( 
                                    label         = 'alpha',
                                    field         = True,
                                    minValue      = 0.00, 
                                    maxValue      = 1.00, 
                                    fieldMinValue = 0.00,
                                    fieldMaxValue = 10.00,
                                    value         = 0.10,
                                    pre           = 2,        # �����_�ȉ��̌������w��
                                    changeCommand = lambda value:changeAlpha(value),
                                    dragCommand   = lambda value:changeAlpha(value)
                                    # dragCommand�ŃX���C�h�������s����悤�ɂł��� 
                                    )


            # �e���͈͂��w��D
            lower_limit = pm.floatSliderGrp( 
                                    label         = 'lower limit',
                                    field         = True,
                                    minValue      = -1.00, 
                                    maxValue      = 1.00, 
                                    fieldMinValue = -10.00,
                                    fieldMaxValue = 10.00,
                                    value         = 0.0,
                                    pre           = 2,        # �����_�ȉ��̌������w��
                                    # dragCommand�ŃX���C�h�������s����悤�ɂł��� 
                                    )
            upper_limit = pm.floatSliderGrp( 
                                    label         = 'upper limit',
                                    field         = True,
                                    minValue      = 0, 
                                    maxValue      = 1.00, 
                                    fieldMinValue = -10.00,
                                    fieldMaxValue = 10.00,
                                    value         = 1.0,
                                    pre           = 2,        # �����_�ȉ��̌������w��
                                    # dragCommand�ŃX���C�h�������s����悤�ɂł��� 
                                    )

            with pm.horizontalLayout(spacing = 10):
                """
                pm.button (
                        label  = u"�����Ȃ��u�����h�V�F�C�v",
                        c      = lambda *args: doDMP.do_dmp_with_my_face( myface, curvetool.curPosList ),
                        h      = 40,
                        bgc    = [0.3, 0.17, 0.04]
                    )
                """
                pm.button (
                        label  = u"�ꕔ�̂ݕό`",
                        c      = lambda *args: doDMP_constraint.do_dmp( 
                                                            myface,
                                                            curvetool.curPosList,
                                                            pm.floatSliderGrp(alphaButton, q = 1, v = 1),
                                                            pm.floatSliderGrp(lower_limit, q = 1, v = 1),
                                                            pm.floatSliderGrp(upper_limit, q = 1, v = 1)  ),
                        h      = 40,
                        bgc    = [0.3, 0.17, 0.04]
                    )

                pm.button (label = u"�S�̂�ό`",
                    c = lambda *args: multiple.do(myface),
                    h      = 40,
                        bgc    = [0.3, 0.17, 0.04]
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
                    pre           = 2,        # �����_�ȉ��̌������w��
                    changeCommand = lambda value:changeLamda(value)
                    # dragCommand�ŃX���C�h�������s����悤�ɂł��� 
                    )
                    
                serch_area = pm.intSliderGrp( 
                                    label         = 'serch area',
                                    field         = True,
                                    minValue      = 1, 
                                    maxValue      = 20, 
                                    fieldMinValue = 1,
                                    fieldMaxValue = 100,
                                    value         = 8,
                                    # dragCommand�ŃX���C�h�������s����悤�ɂł��� 
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
                        label  = "Laplacian edit(�ꕔ)",
                        c      = lambda *args: limitLap.laplacian_cmd_completion(myface, pm.intSliderGrp(serch_area, q=1, v=1)),
                        h      = 40,
                        bgc    = [0.3, 0.17, 0.04]
                    )
                    pm.button (
                        #label  = "Laplacian edit(completed)",
                        label  = "Laplacian edit(�S��)",
                        c      = lambda *args: multiple.lap(myface, pm.intSliderGrp(serch_area, q=1, v=1)),
                        h      = 40,
                        bgc    = [0.3, 0.17, 0.04]
                    )

                """
                pm.button(
                    label = u"�u�����h�V�F�C�v�Ƃ��ĕۑ�",
                    c     = "save_as_BS()",
                    h     = 20 
                )
                """

        # ----------------------------------------------------------------------------
        """
        with pm.frameLayout( label=u'�œK��', labelAlign='top', borderVisible = 0,cll = 1, cl = 0) : 
            sample = pm.intSliderGrp( 
                                    label         = 'serch area',
                                    field         = True,
                                    minValue      = 1, 
                                    maxValue      = 20, 
                                    fieldMinValue = 1,
                                    fieldMaxValue = 100,
                                    value         = 8,
                                    # dragCommand�ŃX���C�h�������s����悤�ɂł��� 
                                    )   

            sample = 15
            opt_ids = -1
            opt_curpos = -1

            pm.button (
                    label  = u"���������ςȕό`",
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
        
        
            
            
            

        
            
        
curvetool.make_curve_tool(ref,myface, pinIndexList, paramList, pinMode)
pm.showWindow( sketch_deformer_ui )




