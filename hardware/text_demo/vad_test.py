
import Opus
import audio
import utime
from machine import Pin
from usr.logging import getLogger
import osTimer



logger = getLogger(__name__)
volume = 5

# ==================== 音频管理 ====================

class AudioManager(object):

    def __init__(self, channel=0, volume=5, pa_number=29):
        self.aud = audio.Audio(channel)  # 初始化音频播放通道
        self.aud.set_pa(pa_number)
        self.aud.setVolume(volume)  # 设置音量
        self.aud.setCallback(self.audio_cb)
        self.rec = audio.Record(channel)
        self.rec.gain_set(4,9)
        self.__skip = 0

    def setvolume_down(self):
        global volume
        volume -= 1
        if volume < 0: volume = 0
        self.aud.setVolume(volume)
        return volume
        
    def setvolume_up(self):
        global volume
        volume += 1
        if volume > 11: volume = 11
        self.aud.setVolume(volume)
        return volume
    
    def setvolume_close(self):
        self.aud.setVolume(0)
        volume = 0
        return volume

    # ========== 音频文件 ====================

    def audio_cb(self, event):
        if event == 0:
            # logger.info('audio play start.')
            pass
        elif event == 7:
            # logger.info('audio play finish.')
            pass
        else:
            pass

    def play(self, file):
        self.aud.play(0, 1, file)
        
    def stop(self):
        return self.aud.stopAll()

    # ========= opus ====================

    def open_opus(self):
        self.pcm = audio.Audio.PCM(0, 1, 16000, 2, 1, 15)  # 5 -> 25
        self.opus = Opus(self.pcm, 0, 6000)  # 6000 ~ 128000
    
    def close_opus(self):
        self.opus.close()
        self.pcm.close()
        del self.opus
        del self.pcm
    
    def opus_read(self):
        return self.opus.read(60)

    def opus_write(self, data):
        return self.opus.write(data)

    # ========= vad & kws ====================

    def set_kws_cb(self, cb):
        self.rec.ovkws_set_callback(cb)

            
    def set_vad_cb(self, cb):
        def wrapper(state):
            # if self.__skip != 2:
            #     self.__skip += 1
            #     return
            return cb(state)
        self.rec.vad_set_callback(wrapper)

    def end_cb(self, para):
        if(para[0] == "stream"):
            if(para[2] == 1):
                pass
            elif (para[2] == 3):
                pass
            else:
                pass
        else:
            pass
    
    def start_kws(self):
        list=["_xiao_zhi_xiao_zhi","_xiao_tian_xiao_tian"]
        self.rec.ovkws_start("_xiao_zhi_xiao_zhi", 0.7)
 

    def stop_kws(self):
        self.rec.ovkws_stop()
    
    def start_vad(self):
        self.__skip = 0
        self.rec.vad_start()
    
    def stop_vad(self):
        self.rec.vad_stop()


def vad_callback(state):
    print("VAD状态变化:", state)
    # state == 1 表示检测到有人声，0 表示无人声



def main():
    audio_manager = AudioManager()
    audio_manager.set_vad_cb(vad_callback)
    audio_manager.open_opus()
    audio_manager.start_vad()
    print("开始VAD测试，按Ctrl+C退出")
    x=2
    try:
        while True:
            audio_manager.opus_read()
            utime.sleep_ms(10)
    except KeyboardInterrupt:
        print("测试结束")
        audio_manager.stop_vad()
        audio_manager.close_opus()

if __name__ == "__main__":    
    main()