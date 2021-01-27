# coding:shift-JIS
# pylint: disable=F0401

import pymel.core as pm
import sys
import json
import numpy as np
import time

myfanc_path = ["C:/Users/piedp/OneDrive/Labo/Sketch/Script/BlendLap/myfanc",
               "C:/Users/piedp/OneDrive/Labo/Sketch/Script/BlendLap",
               "C:/Users/piedp/OneDrive/Labo/Sketch/Script/BlendLap/myfanc/kensaku"]
for path in myfanc_path :
    if not path in sys.path :
        sys.path.append( path )

import my_face
reload (my_face)
import tools
reload (tools)
import curvetool
reload (curvetool)
import limitLap
reload (limitLap)
import doDMP_completed
reload (doDMP_completed)
import doDMPwithM
reload (doDMPwithM)
import doDMP_constraint
reload (doDMP_constraint)
import difference
reload (difference)
import housen
reload (housen)
import doDMP_constraint_pre
reload (doDMP_constraint_pre)
import limitLap
reload (limitLap)
"""
総当たり計算．
旧DMPアルゴリズムを用い高速化できるかテスト．
"""

def prev_sample(myface, sample=30) :
    sampling_point = [ i * (1. / sample) for i in range(sample)]
    cp =  curvetool.getCurvePoint(myface.curve, sampling_point, "normal")
    tools.makeSphere(pos_list=cp)



def repeat_dmp(myface, sample = 30) :
    
    cam_info = tools.cam_info()

    # ピンの数
    n = len(myface.parts_vertex[myface.context_parts])
    nu = 5  # 両端を含む，上唇のピンの数
    nl = 5  # 両端を含む，下唇のピンの数
    
    # 検索の解像度
    sampling_point = [ i * (1. / sample) for i in range(sample)]
    print sampling_point

    costs = []
    w2   = []
    bwm = []
    diff3D = []
    
    pinID_comp_pre, params_comp_pre = doDMP_completed.complete_pin(myface)
    dmp = doDMPwithM.DmpBlendShape(myface,pinID_comp_pre)
    
    for p1, point1 in enumerate( sampling_point ) :

        cost_row = []
        w2_row   = []
        bwm_row  = []
        diff3D_row = []
        for p2, point2 in enumerate( sampling_point ) :
            
            
            # 近すぎる部分を回避
            if abs(p1-p2) < 6 :
                cost_row.append(np.nan)
                w2_row.append(np.nan)
                bwm_row.append(np.nan)
                diff3D_row.append(np.nan)
                continue
            
            
            if point2 < point1 :
                point2 += 1

            params = []
            # パラメータを検索
            # 上唇
            for i in range(nu - 1) :
                param = point1 + ( ((point2-point1)/(nu-1.)) * float(i) )
                params.append(param - int(param))

            # 下唇
            point1 += 1
            
            for i in range(nl - 1) :
                param = point2 + ( ((point1-point2)/(nl-1.)) * float(i) )
                params.append(param - int(param))

            #print "id     : ", p1, ", ", p2
            #print "params : ", params
            point1 -= 1
   
            curPosList =  curvetool.getCurvePoint(myface.curve, params, "normal")
            
            # x座標を比較
            if curPosList[0][0] >= curPosList[nu][0] :
                cost_row.append(np.nan)
                w2_row.append(np.nan)
                bwm_row.append(np.nan)
                diff3D_row.append(np.nan)
                continue


            # - - - ピンを補完してDMPを実行 - - - - - - - - - - - - - -  - - - - - -
            pinID_comp, params_comp = doDMP_completed.complete_pin(myface, params=params)
            curPosList_comp = curvetool.getCurvePoint(myface.curve, params_comp, "normal")
            
            weight, cost, pos, Bmw = dmp.calc_weight(curPosList_comp,True)
            
            """
            weight, cost, pos, Bmw = doDMP_constraint.do_dmp( myface,
                                            curPosList_comp, 
                                            pinIndex = pinID_comp,
                                            ap = False,
                                            ret_info = True)
            """
            # --------------------------------------------------------------------
            
            
            cost_row.append(cost)
            w2_row.append(w2)
            bwm_row.append(Bmw)
            #dist = 0
            #diff3D_row.append(difference.diff_3D_max(myface))
            #diff3D_row.append(difference.do_diff_2D(myface))
            #dist = difference.diff_pos(myface, pinIndexList=pinID_comp, vpos=pos, params=params_comp, curpos=curPosList_comp)
            #dist = difference.diff_pos2d(myface, pinIndexList=pinID_comp, vpos=pos, params=params_comp, curpos=curPosList_comp, cam_info=cam_info)
            #dist = difference.diff_3D(myface, pinIndexList=pinID_comp, pos = pos)
            #dist = difference.diff_3D_max(myface, pinIndexList=pinID_comp, pos = pos)
            #dist = ]]  difference.do_diff_2D(myface)
            #dist = housen.diff_nom(myface, pins=pinID_comp, curpos=curPosList_comp, mouthpos=pos, params=params_comp, cam_info=cam_info)
            #dist = housen.diff_angle(myface, pinID_comp, pos, curPosList_comp, params_comp)
            #dist = housen.angle_normal(myface, pinIndexList= pinID_comp, mouthpos= pos, curpos= curPosList_comp, params= params_comp, cam_info=cam_info, pins=pinID_comp)
            #dist = housen.angle_2dpos(myface, vpos = pos, curpos=curPosList_comp, cam_info=cam_info)
            dist = housen.angle_2dposplus(myface, vpos = pos, curpos=curPosList_comp, cam_info=cam_info)
            print p1, " ", p2, " : ", dist

            diff3D_row.append(dist)
            
            
             

        costs.append(cost_row)
        w2.append(w2_row)
        bwm.append(bwm_row)
        diff3D.append (diff3D_row)

        print "progress : ", p1, " / ", sample

    ret = {}
    ret["sample"] = sample
    ret["cost"]   = cost
    ret["w2"]     = w2
    ret["Bw-m"]   = bwm
    ret["diff3D"] = diff3D

    tools.deltemp("tempvec")

    # print ret["Bw-m"]
    return ret


def do_dmp_from_bwm(myface, sample, bwm, idin = [-1,-1]) :
    print u"もっともBw-mが小さい点について実行"
    
    minimum = 100000
    id = [-1,-1]
    if idin[0] == -1 :
        for i,bwm_row in enumerate(bwm) :
            for j,b in enumerate(bwm_row) :
                if b < minimum :
                    minimum  = b
                    id = [i,j]
    else :
        id = idin
        
    sampling_point = [ i * (1. / sample) for i in range(sample)]
    point1 = sampling_point[id[0]]
    point2 = sampling_point[id[1]]
    
    print "id", id, minimum
    
    # ピンの数
    n = len(myface.parts_vertex[myface.context_parts])
    nu = 5  # 両端を含む，上唇のピンの数
    nl = 5  # 両端を含む，下唇のピンの数
    
    # 検索の解像度
          
    if point2 < point1 :
        point2 += 1
    
    params = []
    # パラメータを検索
    # 上唇
    for i in range(nu - 1) :
        param = point1 + ( ((point2-point1)/(nu-1.)) * float(i) )
        params.append(param - int(param))

    # 下唇
    point1 += 1    
    for i in range(nl - 1) :
        param = point2 + ( ((point1-point2)/(nu-1.)) * float(i) )
        #print " - - - ",point1," ",point2," ",param
        params.append(param - int(param))
    print "params : ", params
    point1 -= 1

    curPosList =  curvetool.getCurvePoint(myface.curve, params, "curvature")

    
    pinID_comp, params_comp = doDMP_completed.complete_pin(myface, params=params)
    #pinID_comp = myface.parts_vertex[myface.context_parts]
    curPosList_comp = curvetool.getCurvePoint(myface.curve, params_comp, "normal")
    #curPosList_comp = curvetool.getCurvePoint(myface.curve, myface.param_list, "curvature")
    #curPosList_comp = curvetool.getCurvePoint(myface.curve, params, "curvature")
    weight, cost, pos, Bmw = doDMP_constraint.do_dmp( myface,
                             curPosList_comp,
                             pinIndex = pinID_comp, 
                             ap = True,
                             alpha= 0.001,
                             ret_info=True
                             )

    # 誤差を表示
    difference.diff_pos(myface, pinIndexList=pinID_comp, vpos=pos, params=params_comp, curpos=curPosList_comp, debug = True)
            
    #tools.deltemp("tempvec")

    #housen.diff_nom(myface, pins=pinID_comp, params=params_comp, cam_info=tools.cam_info())
    
    #return pinID_comp, params_comp

def lap(myface, sample = 30, id = [-1,-1]) :

    # ------- ブレンドシェイプをフリーズ ----------
    tools.freeze_blend_shape(
                    myface.obj, 
                    myface.blender, 
                    myface.defaultShape)  # 重い
    # --------------------------------------------

    sampling_point = [ i * (1. / sample) for i in range(sample)]
    point1 = sampling_point[id[0]]
    point2 = sampling_point[id[1]]
    
    # ピンの数
    n = len(myface.parts_vertex[myface.context_parts])
    nu = 5  # 両端を含む，上唇のピンの数
    nl = 5  # 両端を含む，下唇のピンの数
    
    if point2 < point1 :
        point2 += 1
    params = []
    # 上唇
    for i in range(nu - 1) :
        param = point1 + ( ((point2-point1)/(nu-1.)) * float(i) )
        params.append(param - int(param))

    # 下唇
    point1 += 1    
    for i in range(nl - 1) :
        param = point2 + ( ((point1-point2)/(nu-1.)) * float(i) )
        #print " - - - ",point1," ",point2," ",param
        params.append(param - int(param))
    print "params : ", params
    point1 -= 1

    curPosList =  curvetool.getCurvePoint(myface.curve, params, "normal")

    pinID_comp, params_comp = doDMP_completed.complete_pin(myface, params=params)
    curPosList_comp = curvetool.getCurvePoint(myface.curve, params_comp, "normal")
    
    #temp
    print "len", len(curPosList_comp)
    vtxPos = [pm.pointPosition(myface.obj.vtx[i]) for i in pinID_comp]
    print "len", len(vtxPos),  " ", len(vtxPos[0])
    mv = [tools.makeVector([curPosList_comp[i][j]-vtxPos[i][j] for j in range(3)], vtxPos[i]) for i in range(len(curPosList_comp))]
    print len(mv)
    

    print "id : ", pinID_comp
    print "param : ",params
    print "param_comp : ", params_comp
    limitLap.do_lap_limit(myface, pinID_comp, 12, curPosList_comp, debug = True)

    return pinID_comp, params_comp


prev_sample(myface, sample=30)
start = time.time() 
calc  = repeat_dmp(myface,30)
print u"検索時間 : ", time.time()-start
pp    = do_dmp_from_bwm(myface, 30,calc["diff3D"])


#pp =  do_dmp_from_bwm(myface, 30,calc["diff3D"], [29,9])
#ppp = lap(myface, 30, [29,13])
print u"jsonに保存します"
tools.json_export(calc["diff3D"], "C:\Users\piedp\OneDrive\Labo\Sketch\Script\BlendLap\Graph\image.test.json")

print u"検索時間 : ", time.time()-start

#print ":::", difference.do_diff_2D(myface)
