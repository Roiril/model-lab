"""Assembly at servo 90 degrees, closed recovery, and reversible disassembly path."""
import math
import numpy as np
from . import kinematics as K


def steps(interface, common_params):
    neutral=K.transforms(90)
    result=[]
    stage=np.array([0.,0.,-60.])
    def move(pid, title, distance, direction, instruction, offset=None):
        count=math.ceil(abs(distance)/.5)+1
        frames=[]
        for t in np.linspace(0,1,count):
            mat=neutral[pid].copy()
            if offset is not None:
                mat[:3,3]+=np.asarray(offset)
            mat[:3,3]+=np.array(direction)*distance*(1-t)
            frames.append({pid:mat})
        result.append({'id':pid+'-in','title':title,'instruction':instruction,'moving':[pid],'frames':frames})
    result.append({'id':'support-base','title':'支持座を置く','instruction':'配線を逃がす側を確認して支持座を置く。',
                   'moving':['support'],'frames':[{'support':np.eye(4)},{'support':np.eye(4)}]})
    lid_stage=neutral['lid'].copy(); lid_stage[:3,3]+=stage+np.array([70,0,0])
    result.append({'id':'lid-base','title':'蓋を組立姿勢に置く','instruction':'支持座とは別に27.4775度の蓋を置く。',
                   'moving':['lid'],'frames':[{'lid':lid_stage},{'lid':lid_stage}]})
    move('link','蓋へリンクを差す',25,(-1,0,0),'蓋の耳へBピンを差す。片側の先端撓みは0.15mm。',stage+np.array([70,0,0]))
    servo_stage=neutral['servo'].copy(); servo_stage[:3,3]+=stage
    result.append({'id':'servo-base','title':'サーボを90度にする','instruction':'PWM源で90度へ合わせて電源を切る。',
                   'moving':['servo'],'frames':[{'servo':servo_stage},{'servo':servo_stage}]})
    move('horn','付属ホーンを差す',10,(1,0,0),'18mmの長腕の向きを図と合わせる。印刷スプラインとねじは使わない。',stage)
    move('crank','ホーン受けを差す',20,(1,0,0),'中央と短腕の溝へ付属ホーンを入れる。',stage)
    frames=[]
    for distance in np.linspace(70,0,141):
        frame={}
        for p in ('lid','link'):
            mat=neutral[p].copy(); mat[:3,3]+=stage+np.array([distance,0,0]); frame[p]=mat
        frames.append(frame)
    result.append({'id':'linkage-connect','title':'蓋とリンクをクランクへ付ける','instruction':'Aピンへリンクを差し、先端の爪が戻るまで入れる。',
                   'moving':['lid','link'],'frames':frames})
    frames=[]
    for distance in np.linspace(60,0,121):
        frame={}
        for p in ('servo','horn','crank','link','lid'):
            mat=neutral[p].copy(); mat[:3,3]+=np.array([0,0,-distance]); frame[p]=mat
        frames.append(frame)
    result.append({'id':'cradle-in','title':'機構一式を支持座へ入れる','instruction':'サーボ耳とクランク軸を開放溝へ入れる。',
                   'moving':['servo','horn','crank','link','lid'],'frames':frames})
    move('servo_cap','押さえと遮蔽壁を差す',50,(0,1,0),'蓋を動かさず、押さえを面の下側から上へ滑らせる。')
    move('hinge_pin','蝶番ピンを通す',60,(-1,0,0),'平らな側を表側にする。両端の抜け止めは最後に付ける面板が受け持つ。')
    move('panel','面板を留める',45,(0,0,-1),'支持座の2本の腕を解除窓から操作する。')
    moving=['horn','crank','link','lid']
    frames=[{p:K.transforms(deg)[p] for p in moving} for deg in np.linspace(90,K.CLOSED_SERVO,71)]
    result.append({'id':'return-closed','title':'90度から閉指令へ戻す','instruction':'2秒の五次補間。個体の角度補正はスロット別に保存する。',
                   'moving':moving,'frames':frames})
    for pid in ('key_l','key_r'):
        move(pid,'交換キーを入れる',10,(0,0,-1),'骨格に着座した後で挿入する。単体の組立では置かない。')
    return result
