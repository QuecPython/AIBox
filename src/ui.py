import lvgl as lv
import utime
import sys_bus
from usr.lcd import *
from machine import Timer
import log

log.basicConfig(level=log.INFO)
logger = log.getLogger("UI")


screen = lv.obj()
screen.set_size(240,240)
screen.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)

# Set style for screen, Part: lv.PART.MAIN, State: lv.STATE.DEFAULT.
screen.set_style_bg_opa(255, lv.PART.MAIN|lv.STATE.DEFAULT)
screen.set_style_bg_color(lv.color_hex(0x000000), lv.PART.MAIN|lv.STATE.DEFAULT)
screen.set_style_bg_grad_dir(lv.GRAD_DIR.NONE, lv.PART.MAIN|lv.STATE.DEFAULT)

# Create flex flow
screen.center()
screen.set_flex_align(lv.FLEX_ALIGN.SPACE_EVENLY, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)
screen.set_flex_flow(lv.FLEX_FLOW.COLUMN)
# Create screen_gif
screen_gif = lv.gif(screen)
screen_gif.set_src("U:/media/happy.gif")
screen_gif.set_style_bg_color(lv.color_hex(0x000000), 0)  # 黑色背景
screen_gif.set_style_bg_opa(lv.OPA.COVER, 0)
screen_gif.set_size(240, 240)
def update_emoji(topic,msg):
    screen_gif.set_style_opa(lv.OPA.TRANSP, 0)
    if msg == "happy":
        screen_gif.set_src("U:/media/happy.gif")
    elif msg == "cool":
        screen_gif.set_src("U:/media/cool.gif")
    elif msg == "thinking":
        screen_gif.set_src("U:/media/thinking.gif")
    elif msg == "angry":
        screen_gif.set_src("U:/media/angry.gif")
    elif msg == "sleep":
        screen_gif.set_src("U:/media/sleep.gif")
    elif msg == "confident":
        screen_gif.set_src("U:/media/confident.gif")
    elif msg == "crying":
        screen_gif.set_src("U:/media/crying.gif")
    elif msg == "delicious":
        screen_gif.set_src("U:/media/delicious.gif")
    elif msg == "funny":
        screen_gif.set_src("U:/media/funny.gif")
    elif msg == "kissy":
        screen_gif.set_src("U:/media/kissy.gif")
    elif msg == "laughing":
        screen_gif.set_src("U:/media/laughing.gif")
    elif msg == "loving":
        screen_gif.set_src("U:/media/loving.gif")
    elif msg == "neutral":
        screen_gif.set_src("U:/media/neutral.gif")
    elif msg == "sleepy":
        screen_gif.set_src("U:/media/sleep.gif")
    elif msg == "sad":
        screen_gif.set_src("U:/media/sad.gif")
    elif msg == "surprised":
        screen_gif.set_src("U:/media/surprised.gif")
    elif msg == "winking":
        screen_gif.set_src("U:/media/winking.gif")
    elif msg == "silly":
        screen_gif.set_src("U:/media/silly.gif")
    elif msg == "relaxed":
        screen_gif.set_src("U:/media/relaxed.gif")
    elif msg == "embarrassed":
        screen_gif.set_src("U:/media/embarrassed.gif")
    else:
        pass
    utime.sleep_ms(20)
    screen_gif.set_style_opa(lv.OPA.COVER, 0)

sys_bus.subscribe("update_emoji", update_emoji)
        
class lvglManager:
    #@staticmethod
    def __init__(self):
        lv.scr_load(screen)

