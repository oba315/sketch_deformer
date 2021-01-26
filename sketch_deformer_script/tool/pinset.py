# coding:shift-JIS
# pylint: disable=F0401

import pymel.core as pm
import sys
import time
import maya.api.OpenMaya as om2
import itertools as it


from . import my_face
reload (my_face)
from . import tools
reload (tools)




    

# �����Ƃ��߂��g�ݍ��킹���珇�ԂɂȂ��Ă����D
# ���_��������x���Ԋu�Ŕz�u����Ă���O��D
def calc_chain(myface, indexes) :

    combinations =  list(it.combinations(indexes, 2))
    print "combinations : ", combinations 
    lenlist = []
    for combi in combinations :
        pos1  =  pm.pointPosition(myface.obj.vtx[combi[0]])
        pos2  =  pm.pointPosition(myface.obj.vtx[combi[1]])
        # (�����Cindex1, index2)
        lenlist.append( ( (pos1-pos2).length(), combi[0], combi[1] ) )
        
    # �����������Ƃ��߂����̂���\�[�g
    ls = sorted(lenlist)
    print ls
    
    # �̗p����ڑ��֌W�𔲂��o��
    necessary = []
    once      = []
    twice     = []
    for count, tup in enumerate( ls ) :
        # ���ɓ��g��ꂽ���_���܂ނ��͎̂g��Ȃ��D
        if (tup[1] in twice) or (tup[2] in twice) :
            continue

        for i in [tup[1], tup[2]] :
            if i in once :
                once.remove(i)
                twice.append(i)
            else :
                once.append(i)
        necessary.append((tup[1], tup[2]))
        
        if count >= len(indexes)-1 : break

    print "once : ", once
    print "twice : ", twice
    print "PPPPP necessary : ", necessary
    # �Ō�ɁC�������ă��X�g���쐬
    # �Z�_��index��once�Ɋi�[����C����ł���͂��ł���D
    # ��荶�̓_���̗p
    x1 = pm.pointPosition(myface.obj.vtx[once[0]])[0]
    x2 = pm.pointPosition(myface.obj.vtx[once[1]])[0]
    chain = [once[0]] if x1 < x2 else [once[1]]
    
    for i in range(len(indexes)-1):
        for tup in necessary :
            if chain[-1] in tup :
                next = tup[1] if tup[0]==chain[-1] else tup[0]

                print chain[-1], " ", next
                chain.append(next)
                necessary.remove(tup)

                
                break
    
    if necessary != [] :
        print "ERROR necessary : ", necessary

    #print "chain : ", chain
    return chain
    
# myface�ƁC�ݒ�ۑ��p�I�u�W�F�N�g�ɒ��_��ݒ�
def change_parts_vertex(myface, key) :

    # �I������s����ݒ肷��D
    slls = pm.ls(sl = 1, fl = 1)
    if not type(slls[0]) == pm.general.MeshVertex :
        print (u"ERROR : ���_��I�����Ă��������D")
    
    indexes = [i.index() for i in slls]

    indexes = calc_chain(myface, indexes)

    print "indexes : ", indexes

    myface.parts_vertex[key] = indexes
    
    # �ݒ�ۑ��p�I�u�W�F�N�g�ɐݒ�D
    if pm.objExists(myface.param_obj_name) :
        attname = myface.param_obj_name + "." + key
        if pm.objExists(attname) :
            pm.setAttr(attname, indexes)
        else :
            print "Error no attribute ", attname
    else :
        print "Error no obj named ", myface.param_obj_name
            
        
# ��O�Ɖ��O�̏�񂩂�mouth�̒��_�����Đݒ�
def refresh_mouth(myface) :
    indexes = myface.parts_vertex["upper_mouth"]
    indexes.remove(indexes[-1])

    cp = myface.parts_vertex["lower_mouth"][:]
    cp.reverse()
    indexes.extend(cp)
    indexes.remove(indexes[-1])

    myface.parts_vertex["mouth"] = indexes