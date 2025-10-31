import audio
import _thread
import utime
import Opus
import gc
rec = audio.Record(0)
pcm = audio.Audio.PCM(0, 1, 16000, 2, 1)

pcm.setVolume(10)

def kws_cb(para):
    print("kws cb:", para)
    print("kws cb:", para)
# 唤醒词
list = ["_xiao_zhi_xiao_zhi","_xiao_mu_xiao_mu","_xiao_yuan_xiao_yuan"]
memory_hog = []
    

rec.ovkws_set_callback(kws_cb)
rec.ovkws_start(list, 0.7)

def pcm_fun_test(para):
    pcm_buf = pcm.read(640)
    opus = Opus(pcm, 0, 16000)  # 6000 ~ 128000 

    while True:
        memory_hog.append(bytearray(1024)) 
        print("mem_free:", gc.mem_free())
        # utime.sleep_ms(200)
        if gc.mem_free() < 100000:
            break
            
    while True:
            print(gc.mem_free())
            opus.read(60)
            utime.sleep_ms(5)
            if gc.mem_free() < 10000:
                print("gc")
                gc.collect()

    


def fun_start(func):
    _thread.start_new_thread(func, (1,))


fun_start(pcm_fun_test)
