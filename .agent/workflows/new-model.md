新しい3Dモデル「$ARGUMENTS」のスキャフォールドを作成してください。

## 手順

1. `models/$ARGUMENTS/` ディレクトリを作成する
2. `models/$ARGUMENTS/params.py` を作成する（下記テンプレートを使う）
3. `models/$ARGUMENTS/model.py` を作成する（下記テンプレートを使う）
4. ユーザーに「どんな形・寸法にしますか？」と聞いてデザインの会話を始める

## params.py テンプレート

```python
# $ARGUMENTS dimensions (m)
# TODO: 実際の寸法に置き換える

WALL   = 0.002   # 2mm
TOP    = 0.002   # 2mm
CLEARANCE = 0.0003  # 0.3mm per side
```

## model.py テンプレート

```python
"""$ARGUMENTS"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))
sys.path.insert(0, os.path.dirname(__file__))

import bpy
from blender_utils import clear_scene, export_stl
from params import *

clear_scene()

# --- modeling ---

export_stl("$ARGUMENTS")
```

スキャフォールド作成後、モデルの用途・対象物のサイズ・希望する形状についてユーザーに質問する。
