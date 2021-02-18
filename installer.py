print (u"install my module")

import sketch_deformer_script
reload (sketch_deformer_script)    


# Windows環境でのMaya2019,Maya2020で動作確認しています。
#
# import出来ない場合、Maya.envのPYTHONPATHにsketch_deformer_scriptのあるディレクトリを追加
#   例：PYTHONPATH=D:\sketch_deformer-master;
# 
# するか、以下を実行してください
# import sys
# sys.path.append("sketch_deformer_scriptのあるディレクトリに変更して下さい")
# 
# また、既にnumpyがインストール済みのMayaではうまく使用できない可能性があります。

