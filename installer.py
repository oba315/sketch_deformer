print (u"install my module")

import sys

# sketch_deformer_scriptのあるディレクトリに変更して下さい！
sys.path.append("C:/Work/Sketch/sketch_deformer_m")

import sketch_deformer_script
reload (sketch_deformer_script)    