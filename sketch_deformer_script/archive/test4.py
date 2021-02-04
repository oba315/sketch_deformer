import maya.cmds as cmds
from functools import partial

def applyAndCloseBtm(*args):
    applyBtm()
    closeBtm()
def applyBtm(*args):
    urlList = {
        1:'http://toyota.jp', \
        2:'http://www.nissan.co.jp', \
        3:'http://www.honda.co.jp', \
        4:'http://www.subaru.jp', \
    }
    
    siteIndex = cmds.radioButtonGrp(
                                siteUrl, q=True, \
                                select=True \
                                  )
    cmds.launch(webPage=urlList[siteIndex])                              
def closeBtm(*args):
    cmds.deleteUI(win, window=True)

if cmds.window(win, exists=True):
    cmds.deleteUI(win, window=True)
    

win = cmds.window('test_Windowc', title='TEST WINDOW',widthHeight=(600,350))
mainForm = cmds.formLayout( numberOfDivisions=100 )

b1 = cmds.button( label='Apply and Close', height=26, command=applyAndCloseBtm )
b2 = cmds.button( label='Apply', height=26, command=applyBtm )
b3 = cmds.button( label='Close', height=26, command=closeBtm )

mybtn = cmds.button( label='mybtn', height=26, command=closeBtm )
mybtn2 = cmds.button( label='mybtn2', height=26, command=closeBtm )

with pm.frameLayout( label='MyflameLayout', labelAlign='top', borderVisible =1,cll = 1, cl = 1) :
    mybtn3 = cmds.button( label='mybtn3', height=26, command=closeBtm )

siteUrl = cmds.radioButtonGrp(
                            label='WWW: ',
                            labelArray4=[ 'TOYOTA', \
                                          'NISSAN', \
                                          'HONDA', \
                                          'SUBARU' ], \
                            numberOfRadioButtons=4, \
                            select=1 \
                             )

cmds.formLayout(
            mainForm, edit=True, \
            #フォームの境界にボタンのどのエッジを固定するかの指定。オフセット値を5としている。
            attachForm = ( [ b1, 'left', 5 ], \
                           [ b1, 'bottom', 5 ], \
                           [ b2, 'bottom', 5 ], \
                           [ b3, 'bottom', 5 ], \
                           [ b3, 'right', 5 ], \
                           [ mybtn2, "top", 300],\
                           [ mybtn2, "left", 20],\
                           [ mybtn, 'top', 300]), \
            #ボタンをフォームのどの位置に固定するかの指定。b1の右辺を33%の位置に、b3の左辺を67%の位置に。
            attachPosition = ( [ b1, 'right' , 0, 33], \
                               [ b3, 'left' , 0, 67] ), \
            #真ん中のボタンb2が左右のボタンの隣接する辺に固定ための設定。
            attachControl = ( [ b2, 'left', 4,  b1 ], \
                              [ b2, 'right', 4, b3 ] ),\
            
            #すべてのボタンの上辺は固定しない。
            attachNone = ( [ b1, 'top' ], [ b2, 'top' ], [ b3, 'top' ] )
            )

            

cmds.showWindow(win)