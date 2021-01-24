# coding:shift-JIS
# pylint: disable=F0401

import os
import sys
# numpy等使用のためパスを追加
sys.path.append(os.path.dirname(__file__))

from . import ui
reload(ui)

