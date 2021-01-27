キャラクターモデルの表情をスケッチで操作するスクリプト
====

## Movie
https://drive.google.com/file/d/1xo9MyAmCvqL5ixvSWVuIPuOBSLl4fRF9/view?usp=sharing

## Install
sketch_deformer内sample_scene.mbを開きます．

installer.pyの中の内容をスクリプトエディタのPythonタブにコピーします．
![](https://i.imgur.com/bB7ec3w.png)

module_pathの値をsketch_deformer_scriptのあるディレクトリに変更します．

スクリプトエディタの内容を実行し，少し待つとUIが表示されます．

![](https://i.imgur.com/q9CzKZC.png)

現在，変形するパーツとして[口]が選択されています．

[スケッチを入力]を選択し，モデル上にスケッチを入力します．

![](https://i.imgur.com/Q4WHGn8.png)

スケッチは黒線で表示されます．
ここで，[一部のみ変形]もしくは[全体を変形]を選択すると，スケッチに合わせてブレンドシェイプウエイトが設定されます．

![](https://i.imgur.com/T9MNuKv.png)

同様に，[左目][右目][右眉][左眉]のスケッチ入力が可能です．

**なお，スケッチは下図の始点から，決められた方向に一筆書きで入力する必要があります．**

![](https://i.imgur.com/NCXbmYe.png)

また，スケッチのもっとも曲率が高い点を変形に利用しているので，完全に丸い形状では適切な変形が行われない場合があります．

複数のスケッチを入力した状態で[全体を変形]を選択すると，それぞれについてブレンドシェイプウエイトが最適化されます．
![](https://i.imgur.com/U8cdRTr.png)


また，[Laplacian edit(全体)]を選択することで，より入力スケッチに正確一致した形状を得ることができます．
![](https://i.imgur.com/KC40PUp.png)



## Contribution

## Licence
