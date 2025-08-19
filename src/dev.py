from misc import PWM_V2
import utime
from machine import Pin
import sys_bus
import audio



tts=audio.TTS(0)
Audio=audio.Audio(0)
lcd=Pin(Pin.GPIO39, Pin.OUT, Pin.PULL_DISABLE, 0)
# 初始化PWM
#50HZ +90°=2ms = 10，+0°=1.5ms，-90°=1ms
#100Hz +90°=2ms, +0°=1ms,-90°=0ms
pwms = [PWM_V2(pwm_v2, 100.0, 10) for pwm_v2 in [PWM_V2.PWM0, PWM_V2.PWM1, PWM_V2.PWM2, PWM_V2.PWM3]]
pwm0=pwms[0]
pwm1=pwms[1]
pwm2=pwms[2]
pwm3=pwms[3]


#100HZ脉宽转占空比
start=15
L_45=20
L_90=25
T_45=10
T_90=5

def smooth_move(pwmx,pwmy,start0,end,steps=5):
    for i in range(steps):
        pwmx.open(100.0,start0+int((end-start0)/(steps)*i))
        pwmy.open(100.0,start0+int((end-start0)/(steps)*i))
        utime.sleep_ms(20)
    


 
def pmw_go():
    for i in range(3):
        smooth_move(pwm0,pwm2,start,T_45)
        smooth_move(pwm0,pwm2,T_45,start)
        smooth_move(pwm1,pwm3,start,T_45)
        smooth_move(pwm1,pwm3,T_45,start)

def pwm_back():
    for i in range(3):
        smooth_move(pwm0,pwm2,start,L_45)
        smooth_move(pwm0,pwm2,L_45,start)
        smooth_move(pwm1,pwm3,start,L_45)
        smooth_move(pwm1,pwm3,L_45,start)
    
def pwm_Left():
    for j in range(3):  # 减少循环次数，避免过度转向
        # 左侧腿前进，右侧腿后退（差速转向）
        for i in range(10):
            pwm0.open(100.0, start + int((L_90 - start)/10 * i))  # 左侧腿大角度前进
            pwm2.open(100.0, start + int((L_90 - start)/10 * i))
            pwm1.open(100.0, start + int((T_90 - start)/10 * i))  # 右侧腿大角度后退
            pwm3.open(100.0, start + int((T_90 - start)/10 * i))
            utime.sleep_ms(20)  # 增加延时，确保舵机响应
        # 保持转向状态短暂时间
        utime.sleep_ms(200)
        # 缓慢复位（可选）
        for i in range(10):
            pwm0.open(100.0, L_90 - int((L_90 - start)/10 * i))
            pwm2.open(100.0, L_90 - int((L_90 - start)/10 * i))
            pwm1.open(100.0, T_90 - int((T_90 - start)/10 * i))
            pwm3.open(100.0, T_90 - int((T_90 - start)/10 * i))
            utime.sleep_ms(20)
        
def pwm_Right():
    for j in range(3):
        # 右侧腿前进，左侧腿后退（差速转向）
        for i in range(10):
            pwm1.open(100.0, start + int((L_90 - start)/10 * i))  # 右侧腿大角度前进（pwm1/pwm3）
            pwm3.open(100.0, start + int((L_90 - start)/10 * i))
            pwm0.open(100.0, start + int((T_90 - start)/10 * i)) # 左侧腿大角度后退（pwm0/pwm2）
            pwm2.open(100.0, start + int((T_90 - start)/10 * i))
            utime.sleep_ms(20)  # 增加延时，确保舵机响应
        # 保持转向状态短暂时间
        utime.sleep_ms(100)
        # 缓慢复位（可选）
        for i in range(10):
            pwm1.open(100.0, L_90 - int((L_90 - start)/10 * i))
            pwm3.open(100.0, L_90 - int((L_90 - start)/10 * i))
            pwm0.open(100.0, T_90 - int((T_90 - start)/10 * i))
            pwm2.open(100.0, T_90 - int((T_90 - start)/10 * i))
            utime.sleep_ms(20)
    
def pwm_sit():
    smooth_move(pwm0,pwm1,start,L_90,5)
    smooth_move(pwm2,pwm3,start,T_90,5)
        


def pwm_handler(topic,msg):
    if msg == "go":
        pmw_go()
    elif msg == "back":
        pwm_back()
    elif msg == "left":
        pwm_Left()
    elif msg == "right":
        pwm_Right()
    elif msg == "sit":
        pwm_sit()




def led_handler(topic,msg):
    if msg == "open":
        Audio.stopPlayStream()
        print("停止所有播放")
        lcd.write(0)
        x=tts.play(4, 0, 2, '灯已打开')
        print("x=",x)
    elif msg == "close":
        Audio.stopPlayStream()
        print("停止所有播放")
        lcd.write(1)
        x=tts.play(4, 0, 2, '灯已关闭')
        print("x=",x)

    


sys_bus.subscribe("dev_pwm",pwm_handler)
sys_bus.subscribe("dev_led",led_handler)
sys_bus.subscribe("act",pwm_handler)