# coding:shift-JIS
# pylint: disable=F0401

import json
import os
import maya.api.OpenMaya as om2
import maya.cmds as cmds
import sys
import pymel.core as pm

space = om2.MSpace.kWorld


from . import tools
reload (tools)

def expoert_mesh_data(path) :

    #------ blendshape�̕ω��ʂ�Json�ɏ����o��! -------------
    """
    �d�l ���L�[�œ���Ă�̂Ŏ����̏��Ԃ͂��̒ʂ�ł͂Ȃ��A�C���f�b�N�X�ŌĂ΂Ȃ��悤��
    {
        data          :
        {
            name_of_BS
        }
        base�@�F�@
        {
            vtx        : [���_���W],
            connection : [�ڑ����_]
        }
        
        target : 
        [
            [���_���Ƃ�blendshape�x�N�g��]
        ]
    }
    ����
    �u�����h�V�F�C�v�Ɠ������O�̃I�u�W�F�N�g���������A��������blendshape�̃x�N�g�����擾���Ă��܂��B
    �u�����h�V�F�C�v�̌��I�u�W�F�N�g�������Ă���Ə����o���Ȃ�
    
    """
    #---------------------------------------------------

    # ���O�̃��X�g�F�u�����h�V�F�C�v�̏��Ԃɒ���

    ObjNameList  = [ "base" ]
    blender      = pm.PyNode('blendShape1')
    #BSlist       = cmds.listAttr(blender + '.w', m=True)
    numOfBS = 0
    for i in blender.w :    # �Ȃ���len���g���Ȃ��ꍇ������D
        numOfBS += 1
        pm.setAttr(i, 0)    # �u�����h�V�F�C�v�̏�����
    #numOfBS = len(blender.w)

    pm.progressWindow( isInterruptable = 1)

    dict         = {}
    dict["data"] = {}

    dict["data"]["name_of_BS"]  = numOfBS


    # �x�[�XOBJ�̏���
    name = ObjNameList[0]
    dagPath = tools.getDagPath(name)


    #---- ���_�̃C�e���[�^���܂킵�A�ۑ� -----
    mitMeshVertIns         = om2.MItMeshVertex(dagPath)    

    v_ls = [] 
    con_ls  = []                                    # .reset�Ō��݂�index���������ł��܂��B
    mitMeshVertIns.reset()
    for n in range(mitMeshVertIns.count()):
        pos = mitMeshVertIns.position(space)     # <type 'OpenMaya.MPoint'>
        v_ls.append( [pos.x, pos.y, pos.z] )     
        # ----- ���[�J���̕��������H -----
        
        #makeSphere(pos, 0.02)
        
        connectList = mitMeshVertIns.getConnectedVertices()
        con_ls.append( [i for i in connectList ])
        mitMeshVertIns.next()


    # �����ɓ����
    base_dic = {}
    base_dic["vtx"] = v_ls
    base_dic["connection"] = con_ls

    dict[name] = base_dic
        

    # �u�����h�V�F�C�v�̃f�[�^���i�[
    # �E�G�C�g�����ۂɕύX���C�x�[�X���f������ʒu���擾�D
    target = []
    for i in blender.w:
        
        for w in blender.w:
            if w == i :
                pm.setAttr(w,1.0)
            else :
                pm.setAttr(w,0.0)
            
        
            
        #dagPath   =  getDagPath(name)    
        #obj_dic   =  {}                 # �@���ȂǕʂȏ���ۑ�����Ƃ��͂��̃I�u�W�F�N�g���Ƃ̎�����
        
        #---- ���_�̃C�e���[�^ -----
        mitMeshVertIns         = om2.MItMeshVertex(dagPath)    
                            
        # BS�x�N�g�����擾
        v_ls = []
        mitMeshVertIns.reset()
        for n in range(mitMeshVertIns.count()):
            
            pos = mitMeshVertIns.position(space)     # <type 'OpenMaya.MPoint'>
            
            
            basePos = dict["base"]["vtx"][n]
            v_ls.append( [
                    pos.x - basePos[0],
                    pos.y - basePos[1],
                    pos.z - basePos[2]   ] )
            # ----- ���[�J���̕��������H -----
            
            mitMeshVertIns.next()
            
            
            #if i.index() == 1 :
            #    makeVector(v_ls[n], basePos)
            
        
        for vi in v_ls :
            for p in vi :
                if -0.0001 < p < 0.0001 :
                    p = 0
        
        
        print "len(v_ls) : ", len(v_ls)    
        target.append( v_ls )
        
        
        
        if pm.progressWindow(q = 1, isCancelled=1) :
            break

    [pm.setAttr(w,0.0) for w in blender.w]
        
    dict["target"] = target    
    print dict

    print u"json�t�@�C��" + path + u"���J���܂��D"
    json_file = open(path, 'w')

    json.dump(dict, json_file)

    json_file.close()

    pm.progressWindow( endProgress = 1)

    """
    json_file = open(path, 'r')
    print type(json.load(json_file)[0])
    json_file.close()
    """
    """
    with open(path, 'r') as json_file:
        data = json.load(json_file)
    """