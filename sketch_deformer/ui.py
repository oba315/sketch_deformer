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
    print "pushed"


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
        print "�I�u�W�F�N�g",str,"�����݂��܂���"
    

def changeRef(str) :
    global ref
    try :
        ref          = pm.PyNode(str)
    except :
        print "�I�u�W�F�N�g",str,"�����݂��܂���"
        
        
# �J�[�u�`��̊J�n        
def startTool(ctx) :
    [ pm.setAttr(w,0.0) for w in blender.w ]
    pm.setToolTo(ctx)
    tools.deltemp()
   


# - - - - - -  �s���̏C�� - - - - - - - - - - - - - - 
def edit_pin2() :
    pinEditor = pinedit2.PinEditor(myface)

    

# - - - - - - - - - - - - - - - - - - - - - - - - - - -


def changeLamda(lamdy) :
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
    

# - - - - - -  �ό`����p�[�c���w�� - - - - - - - - - - - - - - 
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

# - - - - - - - -  ���݊m�F - - - - - - - - - - - - - - - - -
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



global ctx
ctx             = "makeCurveToolCtx"    # �������O�̃R���e�N�X�g�����݂���ƃ����^�C���G���[���N����


##############################
myface = my_face.MyFace()
##############################


# - - - - - - - -  ������Ԃ�ۑ� - - - - - - - - - - - - - - - - -
#global defaultShape         # ���_���ׂĂ̈ʒu 
[ pm.setAttr(w,0.0) for w in blender.w ]
baseObj = pm.PyNode(base) 
#defaultShape = [ pm.pointPosition(v) for v in baseObj.vtx ]

# - - - - - - - - - - - - - - - - - - - - - - - - - - -

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
            pm.text( label='�X�P�b�`�͏���̌����ɓ��͂��Ă�������' , h = 15)
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
                                        myface.param_list,
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
                                    #changeCommand = lambda value:changeAlpha(value),
                                    #dragCommand   = lambda value:changeAlpha(value)
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
                    label   = u"�ꕔ�̂ݕό`",
                    c       = lambda *args: multiple.do_only_one_parts( 
                                                    myface,
                                                    pm.floatSliderGrp(alphaButton, q = 1, v = 1),
                                                    pm.floatSliderGrp(lower_limit, q = 1, v = 1),
                                                    pm.floatSliderGrp(upper_limit, q = 1, v = 1)  ),
                    h       = 40,
                    bgc     = [0.3, 0.17, 0.04]
                    )

                pm.button (label = u"�S�̂�ό`",
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
        
        
            
            
            

        
            
        
curvetool.make_curve_tool(ref,myface, "curvature")
pm.showWindow( sketch_deformer_ui )




