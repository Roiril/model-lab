"""90 degree assembly. All incoming parts follow the face normal."""
import numpy as np
from . import params as P


def steps(interface, common_params):
    result=[{'id':'support-base','title':'支持枠を置く','instruction':'前板の裏側が上になる向きに置きます。',
             'moving':['support'],'frames':[{'support':np.eye(4)},{'support':np.eye(4)}]}]
    def insert(pid,title,distance,instruction):
        frames=[]
        for d in np.linspace(-distance,0,int(distance*2)+1):
            m=np.eye(4); m[2,3]=d; frames.append({pid:m})
        result.append({'id':pid+'-in','title':title,'instruction':instruction,'moving':[pid],'frames':frames})
    insert('guide','案内板を置く',40,'前から入れ、2枚の舌をサーボ座の手前に載せます。')
    insert('servo','90度にしたサーボを入れる',45,'PWM源で90度に合わせて電源を切ります。線は後方の開いた空間へ逃がします。')
    insert('servo_cap','サーボと案内板の押さえを留める',40,'右の長い腕を先端で5mm、左の腕を0.6mm外へ開いて保持します。最後まで差してから腕を戻します。')
    insert('horn','付属ホーンを付ける',20,'18mmの長腕を局所uの正方向へ向けます。ねじは使いません。')
    insert('cam_lower','下カムを置く',30,'平らな背面を案内板の3mm厚の座へ向けます。')
    for i in (1,2,3):
        insert(f'pixel_{i}',f'画素{i}を差す',35,'4mm角の茎を案内穴へ差し、放射ピンを下カムに載せます。')
    insert('cam_upper','上カムをかぶせる',30,'90度の基準位置で、ホーンの長短の腕と各ピンの溝を合わせます。')
    for i in (1,2):
        insert(f'cam_key_{i}',f'カム結合キー{i}を差す',20,'二股の先を片側0.15mm縮め、下カムのくぼみまで差します。')
    insert('panel','面板を留める',35,'3つの画素穴を合わせ、支持枠の腕を押して留めます。')
    for pid in ('key_l','key_r'):
        result.append({'id':pid+'-prepare','title':'交換キーを準備する',
                       'instruction':'キーの挿入と回転は合成側が生成します。単体では基準位置に置きます。',
                       'moving':[pid],'frames':[{pid:np.eye(4)},{pid:np.eye(4)}]})
    result.append({'id':'closed-neutral','title':'面一の位置を確認する',
                   'instruction':'組付け角と閉角はいずれも90度です。3画素が0mmの位置になります。',
                   'moving':list(P.PART_IDS),'frames':[{p:np.eye(4) for p in P.PART_IDS} for _ in range(2)]})
    return result
