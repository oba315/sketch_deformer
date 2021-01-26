# coding:shift-JIS
# pylint: disable=F0401

import pymel.core as pm

def donothing(*args) :
    print "pussed"

#windowが開かれていたら更新する
if pm.window('test_Windowc', exists=True):
    pm.deleteUI('test_Windowc', window=True)


with pm.window('test_Windowc', title='TEST WINDOW',widthHeight=(600,350)) :
    with pm.columnLayout( adjustableColumn=True, rowSpacing=8):

        with pm.frameLayout( label = u'face', 
                             labelAlign='top', 
                             borderVisible =1,
                             backgroundColor = [0.2,0,0],
                             cll = 1,                       # 折り畳み可能か？
                             cl = 1                         # 折り畳みの初期状態
                             ) :
                

            with pm.formLayout( numberOfDivisions=100, h = 100 ) as myForm :

                eyetop = 0
                gray1 = [0.1,0.1,0.1]
                width1 = 20
                eyeLleft = 20
                

                eye_L = pm.button (label = "\n\neye_L", height=55,  c ='donothing()')
                eye_L_u = pm.button (label = "", height=15,  bgc=gray1, c ='donothing()')
                eye_L_l = pm.button (label = "", height=15,  bgc=gray1, c ='donothing()')

                eye_R = pm.button (label = "\n\neye_R", height=55, c ='donothing()')
                eye_R_u = pm.button (label = "", height=15,  bgc=gray1, c ='donothing()')
                eye_R_l = pm.button (label = "", height=15, bgc=gray1,  c ='donothing()')
                
                

                # formlayout内では位置を指定しないと全て左上に重なる．
                pm.formLayout(
                            myForm, edit=True, \
                            

                            # ボタンのエッジを，全体幅の相対で固定[ボタン，辺，オフセット，固定する位置(numberOfDIvisionに対して)]
                            attachPosition = (  [ eye_L,   'top'  , 5,  eyetop ],
                                                [ eye_L_u, 'top'  , 10, eyetop ],
                                                [ eye_L_l, 'top'  , 25, eyetop ],
                                                [ eye_L,   'left' , 0,  eyeLleft],
                                                [ eye_L_u, 'left' , 5,  eyeLleft],
                                                [ eye_L_l, 'left' , 5,  eyeLleft],
                                                [ eye_L,   'right', 0,  eyeLleft + width1],  
                                                [ eye_L_u, 'right', 5,  eyeLleft + width1],  
                                                [ eye_L_l, 'right', 5,  eyeLleft + width1],

                                                [ eye_R,   'top'  , 5,  eyetop ],
                                                [ eye_R_u, 'top'  , 10, eyetop ],
                                                [ eye_R_l, 'top'  , 25, eyetop ],
                                                [ eye_R,   'left' , 0,  100-eyeLleft-width1],
                                                [ eye_R_u, 'left' , 5,  100-eyeLleft-width1],
                                                [ eye_R_l, 'left' , 5,  100-eyeLleft-width1],
                                                [ eye_R,   'right', 0,  100-eyeLleft],  
                                                [ eye_R_u, 'right', 5,  100-eyeLleft],  
                                                [ eye_R_l, 'right', 5,  100-eyeLleft]


                                             ) 
                            
                            )
