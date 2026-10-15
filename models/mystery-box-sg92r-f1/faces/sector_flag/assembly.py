"""Cassette assembly at servo 90 / flag 30 degrees; reverse before unplugging parts."""
import math
import numpy as np
from . import kinematics as K, params as P


def steps(interface, common_params):
    neutral=K.transforms(P.ASSEMBLY_SERVO_DEG)
    result=[]
    qin=np.array((0.,0.,-45.))
    qout=np.array((0.,0.,-45.))
    def placed(pid,shift):
        mat=neutral[pid].copy(); mat[:3,3]+=shift
        return mat
    def introduce(pid,title,shift):
        result.append({'id':pid+'-prepare','title':title,'instruction':title,
                       'moving':[pid],'frames':[{pid:placed(pid,shift)} for _ in range(2)]})
    def insert(ids,title,start,end,instruction):
        start=np.array(start); end=np.array(end)
        frames=[{p:placed(p,start*(1-t)+end*t) for p in ids}
                for t in np.linspace(0,1,math.ceil(np.linalg.norm(end-start)/.5)+1)]
        result.append({'id':'-'.join(ids)+'-in-'+str(len(result)),'title':title,'instruction':instruction,'moving':ids,'frames':frames})
    introduce('servo','サーボを90度にして電源を切る',qin)
    insert(['horn'],'付属ホーンを差す',qin+(10,0,0),qin,'長い18mm腕を局所+vからdの浅い側へ14度傾ける。山の刻みは角度補正で合わせる。')
    insert(['input_cup'],'ホーン受けを被せる',qin+(25,0,0),qin,'非対称の受けを合わせる。ねじは使わない。')
    insert(['input_gear'],'入力歯車のキーを合わせる',qin+(25,0,0),qin,'136度方向の角形キーをホーン受けの貫通孔へ通す。')
    insert(['input_spindle'],'固定軸をu正側から差す',qin+(25,0,0),qin,'ホーン受けと歯車の中央丸穴へ通す。軸には回転位相が無い。')
    introduce('support','支持座を置く',np.zeros(3))
    insert(['servo','horn','input_cup','input_gear','input_spindle'],'サーボ一式を支持座に載せる',qin,(0,0,0),'耳を溝に通し、入力軸を開いた軸受けに置く。')
    introduce('servo_cap','旗室の底を面の外で保持する',np.array((0.,0.,-40.)))
    insert(['cap_foot'],'保持足を斜め半ラップへ差す',(-10,0,-40),(0,0,-40),'面の外でu方向へ差し、側壁の間へ保持足の舌を入れる。')
    insert(['servo_cap','cap_foot'],'底と保持足を一緒に支持座へ入れる',(0,0,-40),(0,0,0),'半ラップを合わせたまま、旗より先に底を入れる。配線とコネクタを指定の空間へ収める。')
    introduce('flag','旗を30度の組付け姿勢にする',qout)
    insert(['sector_gear'],'扇形歯車を旗へ差す',qout+(25,0,0),qout,'偏心した角形のキーを差す。軸方向は両側の軸受けで保持する。')
    insert(['flag_cover'],'覆いの右側を差す',qout+(25,0,0),qout,'角形の突起を扇形歯車に合わせる。')
    mesh_start=(0,-2.8,-2.8*(K.O[1]-K.H[1])/(K.O[0]-K.H[0]))
    insert(['flag','sector_gear','flag_cover'],'旗一式を噛合位置の手前へ運ぶ',qout,mesh_start,'骨格から離れた位置で、歯の位相を合わせる。')
    insert(['flag','sector_gear','flag_cover'],'旗一式を噛み合わせる',mesh_start,(0,0,0),'両軸を結ぶ方向へ寄せる。')
    insert(['hinge_pin'],'蝶番ピンを通す',(-60,0,0),(0,0,0),'頭を左側にして、左の軸受けに接近するまで通す。')
    insert(['bearing_bridge'],'旗室の側壁と左軸押さえを入れる',(0,0,-40),(0,0,0),'表から入れ、左側の舌をピンの溝に入れる。')
    insert(['input_bridge'],'入力軸と右軸の押さえを入れる',(0,0,-40),(0,0,0),'表から入れる。面板が2つの押さえを保持する。')
    insert(['panel'],'面板を留める',(0,0,-40),(0,0,0),'支持座の2本の爪を押して面板に掛ける。指を離すと腕が戻る。')
    moving=['horn','input_cup','input_gear','sector_gear','flag','flag_cover']
    result.append({'id':'return-closed','title':'閉じた姿勢へ戻す',
                   'instruction':'90度から60度へ2秒の五次補間で戻す。分解は90度へ戻して逆順。',
                   'moving':moving,'frames':[{p:K.transforms(a)[p] for p in moving} for a in np.linspace(90,60,61)]})
    result.append({'id':'exchange-keys','title':'交換キーを準備する',
                   'instruction':'キーの着脱と面の40mm直進は合成側の交換工程で行う。',
                   'moving':['key_l','key_r'],'frames':[{p:np.eye(4) for p in ('key_l','key_r')} for _ in range(2)]})
    return result


def disassembly(interface,common_params):
    """Explicit reverse trajectory; parts removed after their reversed insertion."""
    source=steps(interface,common_params)
    return [{**s,'id':'remove-'+s['id'],'frames':s['frames'][::-1]} for s in source[::-1]]
