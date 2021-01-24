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
ctx             = "makeCurveToolCtx"    # �������O�̃R���e�N�X�g�����݂���ƃ����^�C���G���[���N�����

locus_temp = [
    om2.MPoint(0.0,0.0,0.0),
    om2.MPoint(0.0,0.0,0.0),
    om2.MPoint(0.0,0.0,0.0)
]

# �ۑ������J�[�u����J�[�u�ʒu���Ď擾
def reacquisition_curPosList(cur, paramList) :
    global curPosList
    curPosList    = getCurvePoint(cur,paramList) # �ʒu (MayaAPI) 
    print "curPosLsit (",len(curPosList),") :", curPosList


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
    
    
    span = 0.5    # CV��ł�̋���
    
    dragPosition = cmds.draggerContext( ctx, query=True, dragPoint=True)
    post2 = om2.MPoint(dragPosition)
    
    global post
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
            ])
            
            # �V�F�[�_���Z�b�g
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



# �}�E�X�𗣂����Ƃ��̃R�}���h
def ReleaseCmd(mode, pinIndexList, paramList, alpha, pinMode) :

    
    #sys.exit()
    
    # - - - - - �J�[�u���쐬 - - - - - - - - - - - - - - - 
    cv = [ [i[0],i[1],i[2]] for i in cvList]
    print cv
    try :
        temp = pm.PyNode("projectionCurve")
        pm.delete(temp)
    except :
        pass

    # ��̃G���[���N���Ă�H
    try :
        cur = pm.curve(p = cv, n="projectionCurve")
    
        global curPosList
        curPosList    = getCurvePoint(cur,paramList) # �ʒu (MayaAPI) 
        print "*curPosLsit (",len(curPosList),") :", curPosList


    
    except :
        print "ERROR �J�[�u���쐬�ł��܂���"
    

    global locus_temp   
    locus_temp = [
    om2.MPoint(0.0,0.0,0.0),
    om2.MPoint(0.0,0.0,0.0),
    om2.MPoint(0.0,0.0,0.0)
    ]
    
    #[makeSphere(i, 0.05) for i in curPosList]
    
    

    tools.deltemp()
    
    #do_dmp()

    

    
        
    
    
    
    
    
# �J�[�u�̏��� 0~1�̃p�����[�^����,
# �Ή����邃���̍��W��Ԃ�
def getCurvePoint(cur, paramList, pinModes = 0) :
    ################
    # pinMode = curvature : �ȗ����犄�蓖��
    # pinMode = normal    : ���̂܂܂̔䗦�Ŋ��蓖��
    ################
    dagPath    =  tools.getDagPath(cur.name())
    curveFn    =  om2.MFnNurbsCurve(dagPath)
    
    if type(pinModes) == str :
        mode  = pinModes
        
    else :
        print u"ERROR �������s�����[�h��ݒ肵�ĉ����� \n Mode: curvature �Ŏ��s���܂� "
        mode = "curvature"
    
    #--CV�̐�--
    num_of_CV = curveFn.numCVs
    print "num of CV  :", num_of_CV
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
            print "i          :",i
            """
            �Ȃ����I�_�̃p�����[�^�́@<< num_of_CV�@-�@3 >>�@�ɂȂ�B
            ����ȏ�̒l���p�����[�^�Ƃ��ē��͂���ƁA<< �K�{�^�C�v�̍��ڂ͌�����܂��� >> �������B
            """
            position = curveFn.getPointAtParam(i, om2.MSpace.kWorld)
            
            curvePosList.append(position)                            
            #makeSphere(position)
            
        paramList = newParam
        print "paramList  :",paramList
        
    
    return curvePosList


# - - - MAIN - - - - -
#     �c�[���̍쐬
# - - - - - - - - - -  
def make_curve_tool(mode) :
    
     
    if cmds.draggerContext(ctx, exists=True):
        cmds.deleteUI(ctx)                            # �������厖�I���ꂪ�Ȃ��ƃ����^�C���G���[���N����
    # Define draggerContext with press and drag procedures
    cmds.draggerContext(             
            ctx,                 
            prePressCommand     =  "curvetool.prePressCmd()", 
            pressCommand        =  "curvetool.SampleContextPress()", 
            dragCommand         =  'curvetool.dragCmd(ref)', 
            releaseCommand      =  'curvetool.ReleaseCmd(mode, pinIndexList, paramList, alpha, pinMode)', 
            cursor              =  'hand',
            space               =  "world"
            );                """ �����̊֐��̒��̕ϐ��̓O���[�o���ɐ錾����Ă��Ȃ��Ǝg���Ȃ��H�H"""
    # Set the tool to the sample context created
    # Results can be observed by dragging mouse around main window
    
    #cmds.setToolTo(ctx)