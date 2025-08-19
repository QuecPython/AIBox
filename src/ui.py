import lvgl as lv
import utime
import sys_bus
from usr.lcd import *
from machine import Timer
import log

log.basicConfig(level=log.INFO)
logger = log.getLogger("UI")



# ------------------------------------------------Create init screen---------------------------------------------------
init_screen = lv.obj()
init_screen.set_size(240,240)
init_screen.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)

# Set style for screen, Part: lv.PART.MAIN, State: lv.STATE.DEFAULT.
init_screen.set_style_bg_opa(255, lv.PART.MAIN|lv.STATE.DEFAULT)
init_screen.set_style_bg_color(lv.color_hex(0x000000), lv.PART.MAIN|lv.STATE.DEFAULT)
init_screen.set_style_bg_grad_dir(lv.GRAD_DIR.NONE, lv.PART.MAIN|lv.STATE.DEFAULT)

# Create init_screen_top
init_screen_top = lv.obj(init_screen)
init_screen_top.set_size(240, 35)
init_screen_top.set_style_bg_color(lv.color_hex(0x000000), lv.PART.MAIN|lv.STATE.DEFAULT)
init_screen_top.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
init_screen_top.set_style_border_width(0, lv.PART.MAIN|lv.STATE.DEFAULT)  
init_screen_top.set_style_pad_all(0, lv.PART.MAIN|lv.STATE.DEFAULT)        
init_screen_top.set_style_radius(0, lv.PART.MAIN|lv.STATE.DEFAULT)  

init_screen_top.set_flex_align(lv.FLEX_ALIGN.SPACE_BETWEEN, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)
init_screen_top.set_flex_flow(lv.FLEX_FLOW.ROW)

# Create screen_signal
init_topsignal = lv.img(init_screen_top)
init_topsignal.set_src("U:/media/nosignal.png")
init_topsignal.set_size(32, 32)

# Create screen_electric
init_electric = lv.img(init_screen_top)
init_electric.set_src("U:/media/electric.png")
init_electric.set_size(32, 32)

# Create init screen label
init_label = lv.label(init_screen)
init_label.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
init_label.set_style_text_color(lv.color_hex(0xffffff), lv.PART.MAIN|lv.STATE.DEFAULT)
init_label.set_style_text_font(lv.font_montserrat_14, lv.PART.MAIN|lv.STATE.DEFAULT)
init_label.set_size(240, 30)
init_label.set_text("Initializing...")
init_label.center()
# ------------------------------------------------Create main screen---------------------------------------------------
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

# Create screen_top
screen_top = lv.obj(screen)
screen_top.set_size(240, 32)
screen_top.set_style_bg_color(lv.color_hex(0x000000), lv.PART.MAIN|lv.STATE.DEFAULT)
screen_top.set_flex_align(lv.FLEX_ALIGN.SPACE_BETWEEN, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)
screen_top.set_flex_flow(lv.FLEX_FLOW.ROW)
screen_top.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
screen_top.set_style_border_width(0, lv.PART.MAIN|lv.STATE.DEFAULT)  
screen_top.set_style_pad_all(0, lv.PART.MAIN|lv.STATE.DEFAULT)        
screen_top.set_style_radius(0, lv.PART.MAIN|lv.STATE.DEFAULT)       

# Create screen_signal
topsignal = lv.img(screen_top)
topsignal.set_src("U:/media/signal.png")
topsignal.set_size(32, 32)

# Create screen_time
toptime = lv.label(screen_top)
toptime.set_text("00:00")
toptime.set_style_text_font(lv.font_montserrat_14, lv.PART.MAIN|lv.STATE.DEFAULT)
toptime.set_style_text_color(lv.color_hex(0xffffff), lv.PART.MAIN|lv.STATE.DEFAULT)

# Create screen_electric
electric = lv.img(screen_top)
electric.set_src("U:/media/electric.png")
electric.set_size(32, 32)

# Create a separator line 
separator_line = lv.line(screen)
separator_line.set_points([{"x":0, "y":0}, {"x":240, "y":0}], 2)
separator_line.set_style_line_width(8, lv.PART.MAIN)
separator_line.set_style_line_color(lv.color_hex(0xffffff), lv.PART.MAIN)
separator_line.set_style_line_width(1, lv.PART.MAIN|lv.STATE.DEFAULT)
separator_line.align_to(screen_top, lv.ALIGN.OUT_BOTTOM_LEFT, 0, 0)

# Create screen_gif
screen_gif = lv.gif(screen)
screen_gif.set_src("U:/media/happy_min.gif")
screen_gif.set_style_bg_color(lv.color_hex(0x000000), 0)  # 黑色背景
screen_gif.set_style_bg_opa(lv.OPA.COVER, 0)
screen_gif.set_size(150, 150)

# Create screen_word
screen_word = lv.label(screen)
screen_word.set_text("listening...")
screen_word.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
screen_word.set_style_text_color(lv.color_hex(0xffffff), lv.PART.MAIN|lv.STATE.DEFAULT)
screen_word.set_style_text_font(lv.font_montserrat_14, lv.PART.MAIN|lv.STATE.DEFAULT)
screen_word.set_size(157, 31)

def update_emoji(topic,msg):
    screen_gif.set_style_opa(lv.OPA.TRANSP, 0)
    if msg == "happy":
        screen_gif.set_src("U:/media/happy_min.gif")
        #print("update_emoji: happy screen")
    elif msg == "cool":
        screen_gif.set_src("U:/media/cool_min.gif")
        #print("update_emoji: cool screen")
    elif msg == "thinking":
        screen_gif.set_src("U:/media/think_min.gif")
        #print("update_emoji: think screen")
    elif msg == "angry":
        screen_gif.set_src("U:/media/angry_min.gif")
        #print("update_emoji: angry screen")
    elif msg == "sleep":
        screen_gif.set_src("U:/media/sleep_min.gif")
        #print("update_emoji: happy screen")
    utime.sleep_ms(20)
    screen_gif.set_style_opa(lv.OPA.COVER, 0)

def update_status(topic, msg):
    screen_word.set_text(msg+"...")

def update_screen(topic, msg):
    try:
        lcd.lcd_clear(0x0000)
        if msg == "init_screen":
            lv.scr_load(init_screen)
            logger.info("change init_screen")
        elif msg == "main_screen":
            lv.scr_load(screen)
            logger.info("change main_screen")
    except Exception as e:
        logger.error("update_screen error: {}".format(e))

def update_time(arg):
    year, month, day, hour, minute, second = utime.localtime()[0:6]
    toptime.set_text("{}:{}".format(hour,minute))
    #logger.info("time update")

# subscribe topic to update emoji and status
sys_bus.subscribe("update_emoji",update_emoji)
sys_bus.subscribe("update_status",update_status)
sys_bus.subscribe("update_screen",update_screen)

class lvglManager:
    #@staticmethod
    def __init__(self):
        #lv.scr_load(init_screen)
        update_time(None)
        timer1 = Timer(Timer.Timer1)
        timer1.start(period=10000, mode=timer1.PERIODIC, callback= update_time)
        utime.sleep(3)
        #lv.scr_load(screen)



        

