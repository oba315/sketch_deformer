# coding:shift-JIS
# pylint: disable=F0401


import maya.cmds as cmds
import maya.api.OpenMaya as om2
import pymel.core as pm
import json
import sys

from . import tools
reload (tools)

# - - - G L O B A L - - - -


#u_index = []

'''
ref = pm.PyNode("base_ref")
pinIndexList    = [478, 476,  496,  237,  239, 242,  236,  481] 
paramList       = [0.0, 0.13, 0.25, 0.37, 0.5, 0.68, 0.75, 0.83]
'''

global ctx
ctx             = "makeCurveToolCtx"    # �������O�̃R���e�N�X�g�����݂���ƃ����^�C���G���[���N�����

locus_temp = [
    om2.MPoint(0.0,0.0,0.0),
    om2.MPoint(0.0,0.0,0.0),
    om2.MPoint(0.0,0.0,0.0)
]

def show_sketch_from_name_head(myface) :
    for partname in myface.parts_vertex :
        curvename = myface.projection_curve_name + "_" + partname
        if pm.objExists(curvename) :
            cur = pm.PyNode(curvename)

            show_sketch(myface, cur = cur, name = "curveshow_"+partname)

def show_sketch(myface, cam=None, cur=None, overwrite=True, name =None):
    print "�X�P�b�`�̕�����O�ɏo���Č�����悤�ɂ��܂��D"
    if not cur : cur = myface.curve
    if not name : name = "curveshow" 
    if overwrite :
        if pm.objExists(name) :
            c = pm.PyNode(name)
            pm.delete(c)
    
    print "n"

    cur = pm.duplicate(cur, n = name)[0]

    print "n"

    if not cam : cam = pm.PyNode(tools.getCamFromModelPanel())

    campos = pm.getAttr(cam.translate)

    print cur
    for p in cur.cv :
        ppos = pm.pointPosition(p)
        newpos = ppos + (campos - ppos) * 0.1
        pm.move(p, newpos)

    pm.select(cur)

    # �����_�����O�p�̃V�F�[�_��ݒ�
    pm.setAttr(cur.aiRenderCurve,True)
    pm.setAttr(cur.aiCurveWidth, 0.2)
    # �V�F�[�_���m�F
    if not pm.objExists("ai_line_shader") :
        global shadingEngine
        myShader , shadingEngine = pm.createSurfaceShader("aiFlat")
        pm.rename(myShader, "ai_line_shader")
    else :
        print "���łɃ��C���p�V�F�[�_�����݂��܂��B"
        myShader = pm.PyNode("ai_line_shader")
        
    pm.setAttr(myShader.color, (1,0,0))
    pm.connectAttr(myShader.outColor, cur.aiCurveShader)

    pm.select(cur)


# �ۑ������J�[�u����J�[�u�ʒu���Ď擾
def reacquisition_curPosList(newcur, paramList, myface) :
    print "�J�[�u", newcur.name(), "�𕡐����C�^�[�Q�b�g�J�[�u�Ƃ��܂�."
    
    
    if pm.objExists(myface.projection_curve_name) :
        c = pm.PyNode(myface.projection_curve_name)
        pm.delete(c)
    
    c = pm.duplicate(newcur, n = myface.projection_curve_name)
    myface.curve = c[0]
    
    global curPosList
    curPosList = getCurvePoint(c[0],paramList, "curvature")

def SampleContextPress() :
    print "pressed"
    

# �ŏ��ɍs���R�}���h
def prePressCmd() :
    
    print "***prePressCmd***"
    tools.deltemp()
    global cvList
    cvList = []
    global post
    post   = om2.MPoint(0.0,0.0,0.0)

    # �����C���p�̃V�F�[�_��p��
    if not pm.objExists("projection_line_shader") :
        global shadingEngine
        myShader , shadingEngine = pm.createSurfaceShader("surfaceShader")
        pm.rename(myShader, "projection_line_shader")
    else :
        print "���łɃ��C���p�V�F�[�_�����݂��܂��B"
        myShader = pm.PyNode("projection_line_shader")
        shadingEngine = pm.listConnections(myShader, t='shadingEngine')[0]
        
        

    

# Procedure called on drag
def dragCmd(ref) :

    print "***dragCmd***"
    
    span = 0.5    # CV��ł�̋���
    
    dragPosition = cmds.draggerContext( ctx, query=True, dragPoint=True)
    post2 = om2.MPoint(dragPosition)
    
    global post
    global cvList
    distance = post - post2
    if distance.length() > span :

        
        #print "\n", distance.length(),"-------------------------"
                 
        # �Փ˔���
        dagPath = tools.getDagPath(ref.name())
        camName   =  tools.getCamFromModelPanel()
        cam       =  pm.PyNode(camName)
        #print "Try to make cv / camera is [",camName, "]"
        
        projection = tools.laytomesh(
                        dagPath,          # �Փˌ��m�Ώۂ̃I�u�W�F�N�g�̃p�X
                        post2,            # om2.MPoint �N���X�̃I�u�W�F�N�g / �ړ��Ώ�
                        cam              # �J�����̃g�����X�t�H�[���m�[�h
                      )

        
        #projection = om2.MPoint(0,0,0) 
        cvList.append(projection)
        #cvList.append( om2.MPoint(0,0,0) )
        
        
        post = post2
        
        
        
        
        # - - - ���J�[�u - - - - - - - - - - - - -
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
            ], "temp_locus_plane")
            
            # �V�F�[�_���Z�b�g
            print "set shader"
            global shadingEngine
            pm.sets(shadingEngine, e = 1, forceElement = plane)
            print "fin"
            
        else :
            new_point_d = new_point
            new_point_u = new_point
        
        locus_temp = [
            new_point,
            new_point_u,
            new_point_d
        ]
        
        #pm.refresh(f = 1)

        
        # - - - - - - - - - - - - - 
    #button = cmds.draggerContext( ctx, query=True, button=True)
    #modifier = cmds.draggerContext( ctx, query=True, modifier=True)
    #print ("Drag: " + str(dragPosition) + "  Button is " + str(button) + "  Modifier is " + modifier + "\n")
    message = str(dragPosition[0]) + ", " + str(dragPosition[1]) + "aaaaaaaaaaaa"
    cmds.draggerContext( ctx, edit=True, drawString=message)

    
    pm.refresh()
    
    

# �}�E�X�𗣂����Ƃ��̃R�}���h
def ReleaseCmd(myface, pinMode, leave_curve = False) :

    
    # - - - - - �J�[�u���쐬 - - - - - - - - - - - - - - - 
    global cvList
    cv = [ [i[0],i[1],i[2]] for i in cvList]
    print cv
    

    curvename = myface.projection_curve_name
    
    if pm.objExists(curvename) :
        c = pm.PyNode(curvename)
        pm.delete(c)
        #pm.rename( c, "projectionCurve_backup")
        #pm.hide(c)

        
    # �Ȃ��������ŃG���[�H
    cur = pm.curve(p = cv, n=curvename)
    
    # �o�b�N�A�b�v�p�ɂ�����쐬
    if leave_curve == True :
        pm.curve(p = cv, n=curvename)
        cur = pm.PyNode(curvename) 
    
    

    # ���ꂼ��̃p�[�c���ƂɃJ�[�u��ۑ�
    # multiple.py �Ŏg�p
    name = curvename + "_" + myface.context_parts
    if pm.objExists(name) :
        c = pm.PyNode(name)
        pm.delete(c)
    pm.curve(p = cv, n=name )
    
    #except :
    #    print "ERROR �J�[�u���쐬�ł��܂���"
    
    
    
    global locus_temp   
    locus_temp = [
    om2.MPoint(0.0,0.0,0.0),
    om2.MPoint(0.0,0.0,0.0),
    om2.MPoint(0.0,0.0,0.0)
    ]
    
    #[makeSphere(i, 0.05) for i in curPosList]
    
    myface.curve = cur

    if pm.objExists("show_mysketch") :
        pm.delete(pm.PyNode("show_mysketch"))
    # ���J�[�u������
    lst = []
    for i in pm.ls(type = u'transform') :
        if "temp_locus_plane" in i.name() :
            lst.append(i)
            #pm.delete(i)
    pm.polyCBoolOp(lst, n = "show_mysketch")
    
    # ���C�����폜
    tools.deltemp()
    # �V�F�[�_���폜
    #pm.delete(pm.PyNode("projection_line_shader"))
    
    #do_dmp()

    # �J�[�u��������悤��
    show_sketch_from_name_head( myface )



    
    
    pass        
    
    
def test() :
    curvedayo = pm.PyNode(pm.curve( p=[(0, 0, 0), (3, 5, 6), (5, 6, 7), (9, 9, 9)] ))
    
    
# �J�[�u�̏��� 0~1�̃p�����[�^����,
# �Ή����邃���̍��W��Ԃ�
def getCurvePoint(cur, paramList, pinModes = 0, debug = True) :
    ################
    # pinMode = curvature : �ȗ����犄�蓖��
    # pinMode = normal    : ���̂܂܂̔䗦�Ŋ��蓖��
    ################
    dagPath    =  tools.getDagPath(cur.name())
    curveFn    =  om2.MFnNurbsCurve(dagPath)
    
    if type(pinModes) == str :
        mode  = pinModes
        
    else :
        if debug : print u"ERROR �������s�����[�h��ݒ肵�ĉ����� \n Mode: curvature �Ŏ��s���܂� "
        mode = "curvature"
    
    #--CV�̐�--
    num_of_CV = curveFn.numCVs
    # print "num of CV  :", num_of_CV
    cvs        =  curveFn.length()    # �J�[�u�̒���
    
    
    if mode == "normal" :
        curvePosList = []
        for l in paramList :
            p          =  cvs * l
            param      =  curveFn.findParamFromLength( p ) # ���Ԗڂ�CV�ɂ����邩
            #print "cvs",cvs,"p",p, "param",param
            space      =  om2.MSpace.kWorld                # ���[���h�X�y�[�X��錾
            position   =  curveFn.getPointAtParam(param, space)
            
            curvePosList.append(position)
            #makeSphere(position)
    
      
    # �ȗ�����paramList���C�� - - - - - -
    # �ȗ��͎O��������Ƃ��Ă邱�Ƃɒ���
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
            if debug : print "i          :",i
            """
            �Ȃ����I�_�̃p�����[�^�́@<< num_of_CV�@-�@3 >>�@�ɂȂ�B
            ����ȏ�̒l���p�����[�^�Ƃ��ē��͂���ƁA<< �K�{�^�C�v�̍��ڂ͌�����܂��� >> �������B
            """
            position = curveFn.getPointAtParam(i, om2.MSpace.kWorld)
            
            curvePosList.append(position)                            
            #makeSphere(position)
            
        paramList = newParam
        if debug : print "paramList  :",paramList
        
    
    return curvePosList


# - - - MAIN - - - - -
#     �c�[���̍쐬
# - - - - - - - - - -  
def make_curve_tool(ref,myface, pinMode ) :
    
     
    if cmds.draggerContext(ctx, exists=True):
        cmds.deleteUI(ctx)                            # �������厖�I���ꂪ�Ȃ��ƃ����^�C���G���[���N����
    # Define draggerContext with press and drag procedures
    cmds.draggerContext(             
            ctx,                 
            prePressCommand     =  lambda *args : prePressCmd(), 
            pressCommand        =  lambda *args : SampleContextPress(), 
            dragCommand         =  lambda *args : dragCmd(ref), 
            releaseCommand      =  lambda *args : ReleaseCmd(myface, pinMode), 
            cursor              =  'hand',
            space               =  "world"
            );                """ �����̊֐��̒��̕ϐ��̓O���[�o���ɐ錾����Ă��Ȃ��Ǝg���Ȃ��H�H"""
    # Set the tool to the sample context created
    # Results can be observed by dragging mouse around main window
    
    #cmds.setToolTo(ctx)