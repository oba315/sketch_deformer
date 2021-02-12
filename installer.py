print (u"install my module")

import sketch_deformer_script
reload (sketch_deformer_script)    


# Windows環境でのMaya2019で動作確認しています。
#
# import出来ない場合、Maya.envのPYTHONPATHにsketch_deformer_scriptのあるディレクトリを追加
#   例：PYTHONPATH=D:\sketch_deformer-master;
# 
# するか、以下を実行してください
# import sys
# sys.path.append("sketch_deformer_scriptのあるディレクトリに変更して下さい")
# 
# また、既にnumpyがインストール済みのMayaではうまく使用できない場合があります。

# 2020/2/12
# Maya2020をお使いの方へ
# 通常の方法ではスケッチの入力時にエラーが起きてしまいます。
# 以下の修正が必要です
# sketch_deformer_script/tool/tools.py 374行目
# mitMeshPolygonIns.next(1)              
#   ↓
# mitMeshPolygonIns.next()
