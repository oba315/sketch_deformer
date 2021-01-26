# coding:shift-JIS
# pylint: disable=F0401

import pymel.core as pm
import sys
import json
import numpy as np
import time
import itertools

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

def search_parts(myface):
    n = 5 # カーブの数
    cnames = ["projectionCurvemo",
            "projectionCurveel",
            "projectionCurveer",
            "projectionCurvebr",
            "projectionCurvebl",
            ]
    parts = [u"mouth",u"eye_l",u"eye_r",u"eyebrows_l",u"eyebrows_r"]
    paramsall = [myface.param_list,
                myface.param_list,
                myface.param_list,
                myface.param_list,
                myface.param_list]
    
    curs = [pm.PyNode(nn) for nn in cnames]
    
    
    #curpos = [None]*3
    #curpos[0] = curvetool.getCurvePoint(cur1, [0,0.5], "normal")
    #curpos[1] = curvetool.getCurvePoint(cur2, [0,0.5], "normal")
    #curpos[2] = curvetool.getCurvePoint(cur3, [0,0.5], "normal")

    # すべてのカーブの0,0.5の点の座標を集めたもの
    curpos = [curvetool.getCurvePoint(curs[i], [0,0.5], "normal") for i in range(n)]
    

    #pinID0 = myface.parts_vertex["mouth"]
    #pinID1 = myface.parts_vertex["eye_l"]
    #pinID2 = myface.parts_vertex["eye_r"]
    #pinID = [pinID0[0],pinID0[5],pinID1[0],pinID1[5],pinID2[0],pinID2[5]]

    pinIDall = []
    pinID = []
    for part in parts :
        pinIDtemp = myface.parts_vertex[part]
        
        print part
        print " - - - " , myface.parts_vertex[part] 
        print pinIDall
        print pinIDtemp
        pinIDall += pinIDtemp
        pinID += [pinIDtemp[0], pinIDtemp[5]] # すべてのカーブの0,0.5の点の座標
        

    
    combi =  list(itertools.permutations(range(n)))   # 組み合わせ
    print combi
    dists = []
    for c in combi :
        print c,
        cp = []
        for cc in c:
            cp += curpos[cc]
        
        """
        #　対象が5カーブになると120通り？重い．てかＤＭＰ適用前で比べても良くない？
        weight, cost, pos, Bmw = doDMP_constraint.do_dmp( myface,
                            cp,
                            pinIndex = pinID, 
                            ap = False,
                            alpha= 0.1,
                            ret_info = True
                            )
        """
        pos = [myface.defaultShape[i] for i in pinID]
        dist = difference.diff_pos(myface, pinIndexList=pinID, vpos=pos, curpos=cp)
        dists.append(dist)

        print dist
        #time.sleep(1)
        #pm.refresh()


    # もっとも誤差が小さい組み合わせを選出
    i = dists.index(min(dists))
    mc = combi[i]
    print "mc : ", mc
    #cp = curpos[mc[0]] + curpos[mc[1]] + curpos[mc[2]]
    
    #pinIDs = [0]*3
    #pinIDs[0] = myface.parts_vertex["mouth"]
    #pinIDs[1] = myface.parts_vertex["eye_l"]
    ##pinIDs[2] = myface.parts_vertex["eye_r"]
    #pinIDall = pinIDs[mc[0]] + pinIDs[mc[1]] + pinIDs[mc[2]]
    #pinIDall = []
    #for cc in mc :
    #    pinIDall += myface.parts_vertex[parts[cc]]
    #print pinIDall
    
    #params0 = myface.param_list
    #params1 = myface.param_list
    #params2 = myface.param_list

    #curPoss = [0]*3
    #curPoss[0] = curvetool.getCurvePoint(cur1,  params0)
    #curPoss[1] = curvetool.getCurvePoint(cur2, params1)
    #curPoss[2] = curvetool.getCurvePoint(cur3, params2)
    #curPosall = curPoss[mc[0]] + curPoss[mc[1]] + curPoss[mc[2]]
    curPosall = []
    for cc in mc :
        curPosall +=curvetool.getCurvePoint(curs[cc], paramsall[cc])
    
    w = doDMP_constraint.do_dmp( myface,
                        curPosall,
                        pinIndex = pinIDall, 
                        ap = True,
                        alpha= 0.5,
                        )
    return curPosall,pinIDall,paramsall,curs



def do(myface) :
    myface.curve = pm.PyNode("projectionCurvemo")
    myface.curve1 = pm.PyNode("projectionCurveel")
    myface.curve2 = pm.PyNode("projectionCurveer")

    pinID0 = myface.parts_vertex["mouth"]
    pinID1 = myface.parts_vertex["eye_l"]
    pinID2 = myface.parts_vertex["eye_r"]

    params0 = myface.param_list
    params1 = myface.param_list
    params2 = myface.param_list

    pinID = pinID0 + pinID1 + pinID2
    print "pinID[", len(pinID), "] ", pinID

    params = params0+params1+params2

    curPos0 = curvetool.getCurvePoint(myface.curve,  params0)
    curPos1 = curvetool.getCurvePoint(myface.curve1, params1)
    curPos2 = curvetool.getCurvePoint(myface.curve2, params2)
    curPos = curPos0 + curPos1 + curPos2
    
    print len(curPos0)
    print len(params0)
    print len(pinID0)
    
    doDMP_constraint.do_dmp( myface,
                            curPos,
                            pinIndex = pinID, 
                            ap = True,
                            alpha= 0.1
                            )

    return curPos,pinID,params
    
def lap(myface, params, pinID, curs, area=8):
    # ------- ブレンドシェイプをフリーズ ----------
    tools.freeze_blend_shape(
                    myface.obj, 
                    myface.blender, 
                    myface.defaultShape)  # 重い
    # --------------------------------------------
    
    # --------- ピンを補完 -----------------------
    pinID0_comp, params0_comp = tools.complete_pinIndenList(myface,pinID[:8],params[0])
    pinID1_comp, params1_comp = tools.complete_pinIndenList(myface,pinID[8:16],params[1])
    pinID2_comp, params2_comp = tools.complete_pinIndenList(myface,pinID[16:24],params[2])
    pinID3_comp, params3_comp = tools.complete_pinIndenList(myface,pinID[24:32],params[3])
    pinID4_comp, params4_comp = tools.complete_pinIndenList(myface,pinID[32:40],params[4])
    
    print "aaa"
    
    curpos0_comp = curvetool.getCurvePoint(curs[0],  params0_comp, "normal")
    curpos1_comp = curvetool.getCurvePoint(curs[1], params1_comp, "normal")
    curpos2_comp = curvetool.getCurvePoint(curs[2], params2_comp, "normal")
    curpos3_comp = curvetool.getCurvePoint(curs[4], params3_comp, "normal")
    curpos4_comp = curvetool.getCurvePoint(curs[3], params4_comp, "normal")
    
    print "bbb"
    # --------- ラプラシアンエディットを実行 -------
    limitLap.do_lap_limit(
            myface,
            pinID0_comp,
            area, 
            curpos0_comp, 
            debug=True
            )
    limitLap.do_lap_limit(
            myface,
            pinID1_comp,
            3, 
            curpos1_comp, 
            )
    limitLap.do_lap_limit(
            myface,
            pinID2_comp,
            3, 
            curpos2_comp, 
            )
    limitLap.do_lap_limit(
            myface,
            pinID3_comp,
            1, 
            curpos3_comp, 
            debug = True
            )
    limitLap.do_lap_limit(
            myface,
            pinID4_comp,
            1, 
            curpos4_comp,
            debug = True 
            )
    # ---------------------------------------------
    

#curpos, pinID, params = do(myface)
#lap(myface, params, pinID)
#curvetool.show_sketch(myface, pm.PyNode("persp"), myface.curve, False)
#curvetool.show_sketch(myface, pm.PyNode("persp"), myface.curve1, False)
#curvetool.show_sketch(myface, pm.PyNode("persp"), myface.curve2, False)

curpos, pinID, params, curs = search_parts(myface)
#lap(myface, params, pinID,curs)



