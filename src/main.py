"""
提高 CPU 主频: AT+LOG=17,5
"""
import utime
import gc
from machine import ExtInt,Pin
from usr.protocol import WebSocketClient
from usr.utils import ChargeManager, AudioManager, NetManager, TaskManager
from usr.threading import Thread, Event, Condition
from usr.logging import getLogger
import sys_bus
# from usr.ui import lvglManager
from usr.ui import *


logger = getLogger(__name__)


class Application(object):

    def __init__(self):
        Pin(Pin.GPIO33, Pin.OUT, Pin.PULL_PD, 1)
        
        #初始化屏幕
        self.lvgl=lvglManager()
        
        self.prev_emoj = None
        # self.lcd_init = lvglManager()
        
        # 初始化充电管理
        self.charge_manager = ChargeManager()

        # 初始化音频管理
        self.audio_manager = AudioManager()
        self.audio_manager.set_kws_cb(self.on_keyword_spotting)
        self.audio_manager.set_vad_cb(self.on_voice_activity_detection)

        # 初始化网络管理
        self.net_manager = NetManager()

        # 初始化任务调度器
        self.task_manager = TaskManager()

        # 初始化协议
        self.__protocol = WebSocketClient()
        self.__protocol.set_callback(
            audio_message_handler=self.on_audio_message,
            json_message_handler=self.on_json_message
        )

        self.__working_thread = None
        self.__record_thread = None
        self.__record_thread_stop_event = Event()
        self.__voice_activity_event = Event()
        self.__keyword_spotting_event = Event()

    def __record_thread_handler(self):
        """纯粹是为了kws&vad能识别才起的线程持续读音频"""
        logger.debug("record thread handler enter")
        while not self.__record_thread_stop_event.is_set():
            self.audio_manager.opus_read()
            utime.sleep_ms(5)
        logger.debug("record thread handler exit")

    def start_kws(self):
        self.audio_manager.start_kws()
        self.__record_thread_stop_event.clear()
        self.__record_thread = Thread(target=self.__record_thread_handler)
        self.__record_thread.start(stack_size=64)
    
    def stop_kws(self):
        self.__record_thread_stop_event.set()
        self.__record_thread.join()
        self.audio_manager.stop_kws()

    def start_vad(self):
        self.audio_manager.start_vad()
    
    def stop_vad(self):
        self.audio_manager.stop_vad()

    def __working_thread_handler(self):
        t = Thread(target=self.__chat_process)
        t.start(stack_size=64)
        self.__keyword_spotting_event.wait()
        self.stop_kws()
        t.join()
        self.start_kws()

    def __chat_process(self):
        self.start_vad()
        try:
            with self.__protocol:
                self.__protocol.hello()
                self.__protocol.wakeword_detected("小智")
                is_listen_flag = False
                while True:
                    data = self.audio_manager.opus_read()
                    if self.__voice_activity_event.is_set():
                        # 有人声
                        sys_bus.publish("update_status","listening")
                        if not is_listen_flag:
                            self.audio_manager.stop()
                            self.audio_manager.aud.stopPlayStream()
                            # logger.debug("Clear the audio cache:清除播放缓存{}".format(self.audio_manager.stop()))
                            self.__protocol.listen("start")
                            is_listen_flag = True
                        self.__protocol.send(data)
                        # logger.debug("send opus data to server")
                    else:
                        if is_listen_flag:
                            self.__protocol.listen("stop")
                            is_listen_flag = False
                    if not self.__protocol.is_state_ok():
                        break
                    # logger.debug("read opus data length: {}".format(len(data)))
        except Exception as e:
            logger.debug("working thread handler got Exception: {}".format(repr(e)))
        finally:
            self.stop_vad()

    def on_talk_key_click(self, args):
        logger.info("on_talk_key_click: ", args)
        if self.__working_thread is not None and self.__working_thread.is_running():
            return
        self.__working_thread = Thread(target=self.__working_thread_handler)
        self.__working_thread.start()
        
    def on_keyword_spotting(self, state):
        logger.info("on_keyword_spotting: {}".format(state))
        if state[0] == 0:
            # 唤醒词触发
            if self.__working_thread is not None and self.__working_thread.is_running():
                return
            self.__working_thread = Thread(target=self.__working_thread_handler)
            self.__working_thread.start()
            self.__keyword_spotting_event.clear()
        else:
            self.__keyword_spotting_event.set()
        sys_bus.publish("update_screen","main_screen")
        sys_bus.publish("update_emoji","happy")

    def on_voice_activity_detection(self, state):
        gc.collect()
        logger.info("on_voice_activity_detection: {}".format(state))
        if state == 1:
            self.audio_manager.stop()
            self.__voice_activity_event.set()  # 有人声
        else:
            self.__voice_activity_event.clear()  # 无人声

    def on_audio_message(self, raw):
        # raise NotImplementedError("on_audio_message not implemented")
        self.audio_manager.opus_write(raw)

    def on_json_message(self, msg):
        return getattr(self, "handle_{}_message".format(msg["type"]))(msg)

    def handle_stt_message(data, msg):
        raise NotImplementedError("handle_stt_message not implemented")

    def handle_tts_message(self, msg):
        state = msg["state"]
        if state == "start":
            sys_bus.publish("update_status","speaking")
        elif state == "stop":
            sys_bus.publish("update_status","listening")
        else:
            pass
        raise NotImplementedError("handle_tts_message not implemented")

#"happy" "cool"  "angry"  "think"
# ... existing code ...
    def handle_llm_message(data, msg):
        emoj_value = msg["emotion"]
        global perv_emoj
        if 'perv_emoj' not in globals():
            perv_emoj = None

        if perv_emoj != emoj_value:
            print("emoj_value: ", emoj_value)
            sys_bus.publish("update_emoji", emoj_value)
            perv_emoj = emoj_value
    
        raise NotImplementedError("handle_llm_message not implemented")
        
    def handle_iot_message(data, msg):
        raise NotImplementedError("handle_iot_message not implemented")
        

    def run(self):
        self.charge_manager.enable_charge()
        self.audio_manager.open_opus()
        self.start_kws()


if __name__ == "__main__":
    sys_bus.publish("update_screen","init_screen")
    app = Application()
    app.run()
