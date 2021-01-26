# coding:shift-JIS
# pylint: disable=F0401

import pymel.core as pm
import sys
import json
import numpy as np
import time


from .tool import my_face
reload (my_face)
from .search import doDMP_kensaku2
reload (doDMP_kensaku2)
import housen
reload (housen)
import difference
reload(difference)
import doDMP_kensaku2
reload(doDMP_kensaku2)
import optimize
reload(optimize)
import evaluate
reload(evaluate)




# 口角の位置を手動で指定して実行
#pp =  do_dmp_from_bwm(myface, 20,calc["diff3D"], [3,15])

# 現在のモデル形状で2次元投影誤差を計算
"""
print ":::", difference.do_diff_2D(myface)
"""



# 入力スケッチのサンプル数
sample = 15

print u"\n全探索"
start = time.time() 

# スケッチ指定したサンプル数で全探索
calc  = doDMP_kensaku2.repeat_dmp(myface,sample)
# 計算結果から変形を実行
dif = [0]
pp    = doDMP_kensaku2.do_dmp_from_bwm(myface, sample,calc["diff3D"], distance=dif)

time1 = time.time()-start
print u"口角の位置　　       : ", pp
print u"検索時間　　　       : ", time.time()-start
#print u"二次元投影誤差       : ", evaluate.do_diff_2D(myface)
print u"位置＋角度誤差       : ",dif[0]
print u"\n"

# 全探索の結果からラプラシアンエディット
#ppp = doDMP_kensaku2.lap(myface, 30, [29,13])



print u"\nネルダーミード方による探索"

start = time.time() 
# 全探索の結果を受けてネルダーミード方による探索
ids,curpos = optimize.myoptimize(myface,pp,debug = False, distance=dif)
print u"検索時間(ネルダー/全探索のみ) : ", time.time()-start, " / " , time1

#print u"誤差                : ", evaluate.do_diff_2D(myface)
print u"位置＋角度誤差       : ",dif[0]

# ネルダーミードの結果からラプラシアンエディット
#optimize.lap(myface, ids, curpos)
#print u"誤差                : ", evaluate.do_diff_2D(myface)
#print u"位置＋角度誤差       : ",dif



