import lvgl as lv
import utime
import sys_bus
from usr.lcd import *
from machine import Timer
import log
import math

# Create circle style
eye_dsc = lv.draw_arc_dsc_t()
eye_dsc.init()
eye_dsc.color = lv.color_hex(0xffffff)
eye_dsc.width = 31  # 圆的粗细，设置较大值可填充圆形
eye_dsc.opa = lv.OPA.COVER

line_dsc = lv.draw_line_dsc_t()
line_dsc.init()
line_dsc.color = lv.color_hex(0xffffff)
line_dsc.width = 5

# Create circle style for mouth
mouth_dsc = lv.draw_arc_dsc_t()
mouth_dsc.init()
mouth_dsc.color = lv.color_hex(0xffffff)
mouth_dsc.width = 31  # 圆的粗细，设置较大值可填充圆形
mouth_dsc.opa = lv.OPA.COVER
# mouth_dsc.rounded = 1  # 圆角

# 画点
dian_dsc = lv.draw_arc_dsc_t()
dian_dsc.init()
dian_dsc.color = lv.color_hex(0xffffff)
dian_dsc.width = 4  # 圆的粗细，设置较大值可填充圆形
dian_dsc.opa = lv.OPA.COVER

# 黑圆
circle_clear_dsc = lv.draw_arc_dsc_t()
circle_clear_dsc.init()
circle_clear_dsc.color = lv.color_hex(0xffffff)
circle_clear_dsc.width = 5
circle_clear_dsc.opa = lv.OPA.COVER

# Create a style for clearing areas
clear_dsc = lv.draw_rect_dsc_t()
clear_dsc.init()
clear_dsc.bg_opa = lv.OPA.COVER
clear_dsc.bg_color = lv.color_black()  # 使用背景色（白色）来清除内容

# Create circle style
cloud_dsc = lv.draw_arc_dsc_t()
cloud_dsc.init()
cloud_dsc.color = lv.color_hex(0xffffff)
cloud_dsc.width = 3  # 圆的粗细，设置较大值可填充圆形
cloud_dsc.opa = lv.OPA.COVER

question_dsc = lv.draw_arc_dsc_t()
question_dsc.init()
question_dsc.color = lv.color_hex(0xffffff)
question_dsc.width = 4  # 圆的粗细，设置较大值可填充圆形
question_dsc.opa = lv.OPA.COVER

# Create label style
label_dsc = lv.draw_label_dsc_t()
label_dsc.init()
label_dsc.color = lv.palette_main(lv.PALETTE.YELLOW)

# Create  canvas to draw on
_CANVAS_WIDTH = 240
_CANVAS_HEIGHT = 240

canvs_cbuf = bytearray(_CANVAS_WIDTH * _CANVAS_HEIGHT * 4)


#------------------------------------------------------speaking screen------------------------------------------------------
# 创建一个屏幕对象
speaking_screen = lv.obj()
speaking_screen.set_size(240, 240)

speaking_screen.set_style_bg_opa(255, lv.PART.MAIN|lv.STATE.DEFAULT)
speaking_screen.set_style_bg_color(lv.color_hex(0x000000), lv.PART.MAIN|lv.STATE.DEFAULT)
speaking_screen.set_style_bg_grad_dir(lv.GRAD_DIR.NONE, lv.PART.MAIN|lv.STATE.DEFAULT)

speaking_canvas  = lv.canvas(speaking_screen)
speaking_canvas.set_buffer(canvs_cbuf, _CANVAS_WIDTH, _CANVAS_HEIGHT, lv.img.CF.TRUE_COLOR)
speaking_canvas.center()
speaking_canvas.fill_bg(lv.color_black(), lv.OPA.COVER)


speaking_canvas.draw_arc(60, 90, 30, 0, 360, eye_dsc)   # 左眼
speaking_canvas.draw_arc(180, 90, 30, 0, 360, eye_dsc)  # 右眼
#canvas.draw_text(40, 20, 100, label_dsc, "Some text on text canvas")
speaking_canvas.draw_arc(120, 150, 30, 0, 180, mouth_dsc)

# 动画控制变量
eye_closure_height = 0  # 眼睛闭合高度（用于模拟眨眼）
blink_counter = 0       # 眨眼计数器
is_blinking = False     # 是否正在眨眼
blink_phase = 0         # 眨眼阶段：0=不眨眼，1=闭合，2=张开

mouth_closure_height = 30       # 嘴巴初始高度
mouth_counter = 0       # 嘴巴动画计数器
is_mouth_animating = False  # 是否正在嘴巴动画
mouth_phase = 0         # 嘴巴动画阶段：0=不动画，1=张开，2=闭合

def anim_timer_cb(timer):
    global eye_closure_height, blink_counter, is_blinking, blink_phase
    global mouth_closure_height, mouth_counter, is_mouth_animating, mouth_phase
    
    # 控制眨眼 - 每隔一段时间眨一次眼
    if not is_blinking:
        blink_counter += 1
        if blink_counter >= 60:  # 每60帧眨一次眼
            is_blinking = True
            blink_phase = 1  # 进入闭合阶段
            blink_counter = 0
    
    # 控制嘴巴动画 - 每隔一段时间动一次
    if not is_mouth_animating:
        mouth_counter += 1
        if mouth_counter >= 5:  # 每5帧动一次
            is_mouth_animating = True
            mouth_phase = 1  # 进入张开阶段
            mouth_counter = 0
    
    # 实现眨眼动画
    if is_blinking:
        if blink_phase == 1:  # 眼睛闭合阶段
            eye_closure_height += 4  # 增加眼睛闭合高度
            if eye_closure_height >= 25:  # 完全闭合
                eye_closure_height = 25
                blink_phase = 2  # 进入张开阶段
        elif blink_phase == 2:  # 眼睛张开阶段
            eye_closure_height -= 4  # 减少眼睛闭合高度
            if eye_closure_height <= 0:  # 完全张开
                eye_closure_height = 0
                is_blinking = False
                blink_phase = 0  # 重置眨眼阶段
    
    # 实现嘴巴动画 - 通过覆盖上半部分来模拟说话动作
    if is_mouth_animating:
        if mouth_phase == 1:  # 闭嘴阶段（覆盖上半部分）
            mouth_closure_height += 4  # 逐渐增加覆盖高度
            if mouth_closure_height >= 20:  # 覆盖整个嘴巴
                mouth_closure_height = 20
                mouth_phase = 2  # 进入张嘴阶段
        elif mouth_phase == 2:  # 张嘴阶段（恢复完整）
            mouth_closure_height -= 4  # 逐渐减少覆盖高度
            if mouth_closure_height <= 0:  # 完全恢复
                mouth_closure_height = 0
                is_mouth_animating = False
                mouth_phase = 0  # 重置嘴巴动画阶段
    
    # 3. 重绘表情（清除旧内容→重绘眼睛→重绘嘴巴）
    speaking_canvas.draw_rect(0, 60, 240, 60, clear_dsc)  # 清除眼睛画布
    speaking_canvas.draw_rect(0, 150, 240, 60, clear_dsc)  # 清除嘴巴画布
    
    # 绘制眼睛（完整的圆形）
    speaking_canvas.draw_arc(60, 90, 30, 0, 360, eye_dsc)   # 左眼
    speaking_canvas.draw_arc(180, 90, 30, 0, 360, eye_dsc)  # 右眼
    
    # 如果有闭合高度，则用黑色矩形覆盖眼睛上下部分来模拟眨眼
    if eye_closure_height > 0:
        # 使用黑色矩形覆盖眼睛上半部分
        speaking_canvas.draw_rect(30, 60, 60, eye_closure_height, clear_dsc)   # 左眼上半部分
        speaking_canvas.draw_rect(150, 60, 60, eye_closure_height, clear_dsc)  # 右眼上半部分
        # 使用黑色矩形覆盖眼睛下半部分
        speaking_canvas.draw_rect(30, 120 - eye_closure_height, 60, eye_closure_height, clear_dsc)   # 左眼下半部分
        speaking_canvas.draw_rect(150, 120 - eye_closure_height, 60, eye_closure_height, clear_dsc)  # 右眼下半部分
    
    # 绘制动态嘴巴
    # 先绘制完整的半圆嘴巴
    speaking_canvas.draw_arc(120, 150, 30, 0, 180, mouth_dsc)
    
    # 如果有闭合高度，则用黑色矩形覆盖嘴巴上半部分
    if mouth_closure_height > 0:
        # 使用黑色矩形覆盖嘴巴上半部分
        speaking_canvas.draw_rect(90, 150, 60, mouth_closure_height, clear_dsc)

# 创建定时器，每隔10ms触发一次动画回调
speaking_anim_timer = lv.timer_create(anim_timer_cb, 10, None)
speaking_anim_timer.set_repeat_count(-1)  # -1表示无限循环
speaking_anim_timer.pause()  # 暂停定时器，直到切换到angry界面时再启动

#------------------------------------------------------angry screen------------------------------------------------------
angry_screen = lv.obj()
angry_screen.set_style_bg_color(lv.color_hex(0xffffff), lv.PART.MAIN|lv.STATE.DEFAULT)
angry_screen.set_style_bg_opa(lv.OPA.COVER, lv.PART.MAIN|lv.STATE.DEFAULT)
angry_screen.set_style_bg_grad_dir(lv.GRAD_DIR.NONE, lv.PART.MAIN|lv.STATE.DEFAULT)

angry_canvas = lv.canvas(angry_screen)
angry_canvas.set_buffer(canvs_cbuf, _CANVAS_WIDTH, _CANVAS_HEIGHT, lv.img.CF.TRUE_COLOR)
angry_canvas.center()
angry_canvas.fill_bg(lv.color_black(), lv.OPA.COVER)

angry_canvas.draw_arc(60, 90, 30, 0, 360, eye_dsc)   # 左眼
angry_canvas.draw_arc(180, 90, 30, 0, 360, eye_dsc)  # 右眼
angry_canvas.draw_rect(30, 60, 180, 15, clear_dsc) # 清除上端



# 动画控制变量
angry_eye_closure_height = 0  # 眼睛闭合高度（用于模拟眨眼）
angry_blink_counter = 0       # 眨眼计数器
angry_is_blinking = False     # 是否正在眨眼
angry_blink_phase = 0         # 眨眼阶段：0=不眨眼，1=闭合，2=张开

def angry_anim_timer_cb(timer):
    global angry_eye_closure_height, angry_blink_counter, angry_is_blinking, angry_blink_phase
    
    # 控制眨眼 - 每隔一段时间眨一次眼
    if not angry_is_blinking:
        angry_blink_counter += 1
        if angry_blink_counter >= 30:  # 每30帧眨一次眼
            angry_is_blinking = True
            angry_blink_phase = 1  # 进入闭合阶段
            angry_blink_counter = 0
    
    # 实现眨眼动画
    if angry_is_blinking:
        if angry_blink_phase == 1:  # 眼睛闭合阶段
            angry_eye_closure_height += 4  # 增加眼睛闭合高度
            if angry_eye_closure_height >= 25:  # 完全闭合
                angry_eye_closure_height = 25
                angry_blink_phase = 2  # 进入张开阶段
        elif angry_blink_phase == 2:  # 眼睛张开阶段
            angry_eye_closure_height -= 4  # 减少眼睛闭合高度
            if angry_eye_closure_height <= 0:  # 完全张开
                angry_eye_closure_height = 0
                angry_is_blinking = False
                angry_blink_phase = 0  # 重置眨眼阶段
    
    # 重绘表情（清除旧内容→重绘眼睛）
    angry_canvas.draw_rect(0, 60, 240, 60, clear_dsc)  # 清除眼睛画布
    
    # 绘制眼睛
    angry_canvas.draw_arc(60, 90, 30, 0, 360, eye_dsc)   # 左眼
    angry_canvas.draw_arc(180, 90, 30, 0, 360, eye_dsc)  # 右眼
    angry_canvas.draw_rect(30, 60, 180, 15, clear_dsc) # 清除上端
    angry_canvas.draw_rect(30, 110, 180, 15, clear_dsc)# 清除下端
    
    # 重新绘制点和嘴巴
    angry_canvas.draw_arc(180, 55, 3, 0, 360, dian_dsc)
    mouth_point = [{'x': 90, 'y': 165},{'x': 150, 'y': 165}]
    angry_canvas.draw_line(mouth_point, 2, line_dsc)
    

    # 左眉毛 - 从左上到右下倾斜
    angry_canvas.draw_line([{'x': 30, 'y': 50 }, {'x': 80, 'y': 60 }], 3, line_dsc)

    # 右眉毛 - 从右上到左下倾斜
    angry_canvas.draw_line([{'x': 210, 'y': 50 }, {'x': 160, 'y': 60 }], 3, line_dsc)

# 如果有闭合高度，则用黑色矩形覆盖眼睛上下部分来模拟眨眼
if angry_eye_closure_height > 0:
    # 使用黑色矩形覆盖眼睛上半部分
    angry_canvas.draw_rect(30, 60, 60, angry_eye_closure_height, clear_dsc)   # 左眼上半部分
    angry_canvas.draw_rect(150, 60, 60, angry_eye_closure_height, clear_dsc)  # 右眼上半部分
    # 使用黑色矩形覆盖眼睛下半部分
    angry_canvas.draw_rect(30, 120 - angry_eye_closure_height, 60, angry_eye_closure_height, clear_dsc)   # 左眼下半部分
    angry_canvas.draw_rect(150, 120 - angry_eye_closure_height, 60, angry_eye_closure_height, clear_dsc)  # 右眼下半部分
    
    # 如果有闭合高度，则用黑色矩形覆盖眼睛上下部分来模拟眨眼
    if angry_eye_closure_height > 0:
        # 使用黑色矩形覆盖眼睛上半部分
        angry_canvas.draw_rect(30, 60, 60, angry_eye_closure_height, clear_dsc)   # 左眼上半部分
        angry_canvas.draw_rect(150, 60, 60, angry_eye_closure_height, clear_dsc)  # 右眼上半部分
        # 使用黑色矩形覆盖眼睛下半部分
        angry_canvas.draw_rect(30, 120 - angry_eye_closure_height, 60, angry_eye_closure_height, clear_dsc)   # 左眼下半部分
        angry_canvas.draw_rect(150, 120 - angry_eye_closure_height, 60, angry_eye_closure_height, clear_dsc)  # 右眼下半部分

# 创建定时器，每隔10ms触发一次动画回调
angry_anim_timer = lv.timer_create(angry_anim_timer_cb, 10, None)
angry_anim_timer.set_repeat_count(-1)  # -1表示无限循环
angry_anim_timer.pause()  # 暂停定时器，直到切换到angry界面时再启动

#-----------------------------------------------------listening-----------------------------------------------------
listening_screen = lv.obj()
listening_screen.set_style_bg_color(lv.color_hex(0xffffff), 0)
listening_screen.set_style_bg_opa(lv.OPA.COVER, lv.PART.MAIN|lv.STATE.DEFAULT)
listening_screen.set_style_bg_grad_dir(lv.GRAD_DIR.NONE, lv.PART.MAIN|lv.STATE.DEFAULT)

listening_canvas = lv.canvas(listening_screen)
listening_canvas.set_buffer(canvs_cbuf, _CANVAS_WIDTH, _CANVAS_HEIGHT, lv.img.CF.TRUE_COLOR)
listening_canvas.center()
listening_canvas.fill_bg(lv.color_black(), lv.OPA.COVER)

listening_canvas.draw_arc(60, 90, 30, 0, 360, eye_dsc)   # 左眼
listening_canvas.draw_arc(180, 90, 30, 0, 360, eye_dsc)  # 右眼
#listening_canvas.draw_arc(210, 30, 30, 0, 360, question_dsc)

# 动画控制变量
listen_eye_closure_height = 0  # 眼睛闭合高度（用于模拟眨眼）
listen_blink_counter = 0       # 眨眼计数器
listen_is_blinking = False     # 是否正在眨眼
listen_blink_phase = 0         # 眨眼阶段：0=不眨眼，1=闭合，2=张开
listen_quection_counter = 3300    # 圆形动画计数器
listen_quection_flag = True

question_img = lv.img(listening_screen)
question_img.set_src("U:/media/question_mark.png")
question_img.set_size(64, 64)
question_img.set_pos(170, 0)
question_img.set_style_bg_color(lv.color_hex(0xffffff), 0)
def listen_anim_timer_cb(timer):
    global listen_eye_closure_height, listen_blink_counter, listen_is_blinking, listen_blink_phase, listen_quection_counter, listen_quection_flag

    if listen_quection_flag:
        listen_quection_counter += 30
        if listen_quection_counter >= 4200:
            listen_quection_flag = False
    else:
        listen_quection_counter -= 30
        if listen_quection_counter <= 3300:
            listen_quection_flag = True
    # 控制眨眼 - 每隔一段时间眨一次眼
    if not listen_is_blinking:
        listen_blink_counter += 1
        if listen_blink_counter >= 10:  # 每10帧眨一次眼
            listen_is_blinking = True
            listen_blink_phase = 1  # 进入闭合阶段
            listen_blink_counter = 0
    
    # 实现眨眼动画
    if listen_is_blinking:
        if listen_blink_phase == 1:  # 眼睛闭合阶段
            listen_eye_closure_height += 4  # 增加眼睛闭合高度
            if listen_eye_closure_height >= 25:  # 完全闭合
                listen_eye_closure_height = 25
                listen_blink_phase = 2  # 进入张开阶段
        elif listen_blink_phase == 2:  # 眼睛张开阶段
            listen_eye_closure_height -= 4  # 减少眼睛闭合高度
            if listen_eye_closure_height <= 0:  # 完全张开
                listen_eye_closure_height = 0
                listen_is_blinking = False
                listen_blink_phase = 0  # 重置眨眼阶段
    
    # 3. 重绘表情（清除旧内容→重绘眼睛）
    listening_canvas.draw_rect(0, 60, 240, 60, clear_dsc)  # 清除眼睛画布
    
    # 绘制眼睛（完整的圆形）
    listening_canvas.draw_arc(60, 90, 30, 0, 360, eye_dsc)   # 左眼
    listening_canvas.draw_arc(180, 90, 30, 0, 360, eye_dsc)  # 右眼

    # 如果有闭合高度，则用黑色矩形覆盖眼睛上下部分来模拟眨眼
    if listen_eye_closure_height > 0:
        # 使用黑色矩形覆盖眼睛上半部分
        listening_canvas.draw_rect(30, 60, 60, listen_eye_closure_height, clear_dsc)   # 左眼上半部分
        listening_canvas.draw_rect(150, 60, 60, listen_eye_closure_height, clear_dsc)  # 右眼上半部分
        # 使用黑色矩形覆盖眼睛下半部分
        listening_canvas.draw_rect(30, 120 - listen_eye_closure_height, 60, listen_eye_closure_height, clear_dsc)   # 左眼下半部分
        listening_canvas.draw_rect(150, 120 - listen_eye_closure_height, 60, listen_eye_closure_height, clear_dsc)  # 右眼下半部分

    question_img.set_angle(listen_quection_counter)

# 创建定时器，每隔10ms触发一次动画回调
listening_anim_timer = lv.timer_create(listen_anim_timer_cb, 10, None)
listening_anim_timer.set_repeat_count(-1)  # -1表示无限循环
listening_anim_timer.pause()  # 暂停定时器，直到切换到angry界面时再启动

#-------------------------------- Sleep SCREEN ---------------------------------
sleeping_screen = lv.obj()
sleeping_screen.set_style_bg_color(lv.color_hex(0xffffff), 0)
sleeping_screen.set_style_bg_opa(lv.OPA.COVER, 0)

sleeping_canvas = lv.canvas(sleeping_screen)
sleeping_canvas.set_buffer(canvs_cbuf, _CANVAS_WIDTH, _CANVAS_HEIGHT, lv.img.CF.TRUE_COLOR)
sleeping_canvas.center()
sleeping_canvas.fill_bg(lv.color_black(), lv.OPA.COVER)

sleep_point_left = [{'x': 30, 'y': 90},{'x': 90, 'y': 90}]
sleeping_canvas.draw_line(sleep_point_left, 2, line_dsc)
sleep_point_right = [{'x': 150, 'y': 90},{'x': 210, 'y': 90}]
sleeping_canvas.draw_line(sleep_point_right, 2, line_dsc)

# Z字动画控制变量
sleep_z_state = 0       # Z字动画状态: 0=无, 1=小Z, 2=中Z, 3=大Z, 4=清除
sleep_z_counter = 0     # Z字动画计数器

# 创建Z字绘制样式
z_line_dsc = lv.draw_line_dsc_t()
z_line_dsc.init()
z_line_dsc.color = lv.color_hex(0xffffff)
z_line_dsc.width = 3
z_line_dsc.opa = lv.OPA.COVER

def sleep_anim_timer_cb(timer):
    global sleep_z_state, sleep_z_counter
    
    sleep_z_counter += 1
    
    # 控制Z字出现的时序
    if sleep_z_counter >= 10:  # 每30帧变化一次状态
        sleep_z_state += 1
        sleep_z_counter = 0
        
        if sleep_z_state > 4:  # 循环回到开始
            sleep_z_state = 0
    
    # 清除画布上半部分
    sleeping_canvas.draw_rect(0, 0, 240, 70, clear_dsc)
    
    # 根据状态绘制不同大小的Z字
    if sleep_z_state >= 1:  # 绘制小Z
        small_z_points = [
            {'x': 120, 'y': 55},  # 顶部横线起点 
            {'x': 130, 'y': 55},  # 顶部横线终点 
            {'x': 130, 'y': 55},  # 斜线起点 
            {'x': 120, 'y': 65},  # 斜线终点 
            {'x': 120, 'y': 65},  # 底部横线起点 
            {'x': 130, 'y': 65}   # 底部横线终点 
        ]
        for i in range(0, len(small_z_points), 2):
            line_points = [small_z_points[i], small_z_points[i+1]]
            sleeping_canvas.draw_line(line_points, 2, z_line_dsc)
    
    if sleep_z_state >= 2:  # 绘制中Z
        medium_z_points = [
            {'x': 140, 'y': 35},  # 顶部横线起点 
            {'x': 155, 'y': 35},  # 顶部横线终点 
            {'x': 155, 'y': 35},  # 斜线起点 
            {'x': 140, 'y': 50},  # 斜线终点 
            {'x': 140, 'y': 50},  # 底部横线起点 
            {'x': 155, 'y': 50}   # 底部横线终点 
        ]
        for i in range(0, len(medium_z_points), 2):
            line_points = [medium_z_points[i], medium_z_points[i+1]]
            sleeping_canvas.draw_line(line_points, 2, z_line_dsc)
    
    if sleep_z_state >= 3:  # 绘制大Z
        large_z_points = [
            {'x': 170, 'y': 15},  # 顶部横线起点 
            {'x': 195, 'y': 15},  # 顶部横线终点 
            {'x': 195, 'y': 15},  # 斜线起点 
            {'x': 170, 'y': 40},  # 斜线终点 
            {'x': 170, 'y': 40},  # 底部横线起点 
            {'x': 195, 'y': 40}   # 底部横线终点 
        ]
        for i in range(0, len(large_z_points), 2):
            line_points = [large_z_points[i], large_z_points[i+1]]
            sleeping_canvas.draw_line(line_points, 2, z_line_dsc)
    
    sleep_point_left = [{'x': 30, 'y': 90},{'x': 90, 'y': 90}]
    sleeping_canvas.draw_line(sleep_point_left, 2, line_dsc)
    sleep_point_right = [{'x': 150, 'y': 90},{'x': 210, 'y': 90}]
    sleeping_canvas.draw_line(sleep_point_right, 2, line_dsc)

# 创建定时器，每隔10ms触发一次动画回调
sleep_anim_timer = lv.timer_create(sleep_anim_timer_cb, 30, None)  # 100ms间隔更合适观察动画
sleep_anim_timer.set_repeat_count(-1)  # -1表示无限循环
sleep_anim_timer.pause()  

#------------------开机logo----------------------------------------------------------
init_screen = lv.obj()
init_screen.set_size(240, 240)

# 创建一个图片对象
init_img = lv.img(init_screen)
# 设置图片源，这里使用QuecPython.png作为示例，你可以更换为其他图片
init_img.set_src("U:/media/QuecPython.png")  # 占实际使用时需要正确加载图片

# 将图片放在屏幕中央
init_img.align(lv.ALIGN.CENTER, 0, 0)

def set_angle_cb(obj, val):
    obj.set_angle(val)

def set_zoom_cb(obj, val):
    obj.set_zoom(val)

def anim_end_callback():
    init_img.set_angle(0)
    init_img.set_zoom(128)
    

# 创建动画，同时进行旋转和缩放
# 旋转动画
anim_rotation = lv.anim_t()
anim_rotation.init()
anim_rotation.set_var(init_img)
anim_rotation.set_values(0, 3600)
anim_rotation.set_time(1000)  # 2秒完成动画
anim_rotation.set_repeat_count(3)
anim_rotation.set_custom_exec_cb(lambda a, v: set_angle_cb(init_img, v))
lv.anim_t.start(anim_rotation)

# 缩放动画
anim_scale = lv.anim_t()
anim_scale.init()
anim_scale.set_var(init_img)
anim_scale.set_values(64, 256)  # 从一半大小放大到两倍大小
anim_scale.set_time(3000)  # 2秒完成动画
anim_scale.set_repeat_count(1)
anim_scale.set_path_cb(lv.anim_t.path_ease_in_out)
anim_scale.set_custom_exec_cb(lambda a, v: set_zoom_cb(init_img, v))
lv.anim_t.start(anim_scale)

# # 在动画结束后切换到主界面的函数
# def anim_end_callback(anim_scale):
#     # 这里添加切换到主界面的代码
#     sys_bus.publish("update_screen","open_eye_screen")
#     print("anim_end_callback")

# # 设置动画结束回调
# anim_scale.set_ready_cb(anim_end_callback)

#----------------------open eye animation----------------------
open_eye_screen = lv.obj()
open_eye_screen.set_style_bg_color(lv.color_hex(0xffffff), 0)
open_eye_screen.set_style_bg_opa(lv.OPA.COVER, 0)

open_eye_canvas = lv.canvas(open_eye_screen)
open_eye_canvas.set_buffer(canvs_cbuf, _CANVAS_WIDTH, _CANVAS_HEIGHT, lv.img.CF.TRUE_COLOR)
open_eye_canvas.center()
open_eye_canvas.fill_bg(lv.color_black(), lv.OPA.COVER)

# 绘制初始闭合的眼睛（横线状态）
eye_left = [{'x': 30, 'y': 90},{'x': 90, 'y': 90}]
open_eye_canvas.draw_line(eye_left, 2, line_dsc)
eye_right = [{'x': 150, 'y': 90},{'x': 210, 'y': 90}]
open_eye_canvas.draw_line(eye_right, 2, line_dsc)

# 睁眼动画控制变量
open_eye_blink_count = 0     # 眨眼次数计数器
open_eye_state = 0           # 睁眼状态: 0=初始状态, 1=第一次眨眼, 2=第二次眨眼, 3=第三次眨眼
open_eye_counter = 0         # 动画计数器
open_eye_closure_height = 30 # 眼睛闭合高度，初始为完全闭合
open_eye_max_heights = [20, 10, 0]  # 每次眨眼的最大睁开高度，依次增大

def open_eye_anim_timer_cb(timer):
    global open_eye_blink_count, open_eye_state, open_eye_counter, open_eye_closure_height
    
    open_eye_counter += 1
    
    # 根据当前状态控制眨眼过程
    if open_eye_state == 0:  # 初始状态，保持闭眼
        if open_eye_counter >= 30:  # 停留一段时间后开始第一次眨眼
            open_eye_state = 1
            open_eye_counter = 0
            
    elif open_eye_state == 1:  # 第一次眨眼
        if open_eye_counter <= 10:  # 闭眼阶段
            open_eye_closure_height = min(30, 30 - (open_eye_counter * 1))  # 逐渐闭合
        elif open_eye_counter <= 30:  # 睁眼阶段
            open_eye_closure_height = max(open_eye_max_heights[0], 
                                          30 - (30 - open_eye_counter) * (30 - open_eye_max_heights[0]) / 20)
        else:  # 第一次眨眼完成
            open_eye_state = 2
            open_eye_counter = 0
            
    elif open_eye_state == 2:  # 第二次眨眼
        if open_eye_counter <= 10:  # 闭眼阶段
            open_eye_closure_height = min(30, open_eye_closure_height + 1)  # 逐渐闭合
        elif open_eye_counter <= 30:  # 睁眼阶段
            open_eye_closure_height = max(open_eye_max_heights[1], 
                                          open_eye_closure_height - (30 - open_eye_max_heights[1]) / 20 * (open_eye_counter - 10))
        else:  # 第二次眨眼完成
            open_eye_state = 3
            open_eye_counter = 0
            
    elif open_eye_state == 3:  # 第三次眨眼
        if open_eye_counter <= 10:  # 闭眼阶段
            open_eye_closure_height = min(30, open_eye_closure_height + 1)  # 逐渐闭合
        elif open_eye_counter <= 30:  # 睁眼阶段
            open_eye_closure_height = max(open_eye_max_heights[2], 
                                          open_eye_closure_height - (30 - open_eye_max_heights[2]) / 20 * (open_eye_counter - 10))
        else:  # 第三次眨眼完成，完全睁开
            # 动画结束，切换到listening_screen
            sys_bus.publish("update_screen", "listening_screen")
            return
    
    # 重绘眼睛
    open_eye_canvas.draw_rect(0, 60, 240, 60, clear_dsc)  # 清除眼睛区域
    
    # 绘制眼睛（完整的圆形）
    open_eye_canvas.draw_arc(60, 90, 30, 0, 360, eye_dsc)   # 左眼
    open_eye_canvas.draw_arc(180, 90, 30, 0, 360, eye_dsc)  # 右眼
    
    # 使用黑色矩形覆盖眼睛部分来模拟睁开程度
    if open_eye_closure_height > 0:
        # 覆盖眼睛上半部分
        open_eye_canvas.draw_rect(30, 60, 60, int(open_eye_closure_height), clear_dsc)   # 左眼上半部分
        open_eye_canvas.draw_rect(150, 60, 60, int(open_eye_closure_height), clear_dsc)  # 右眼上半部分
        # 覆盖眼睛下半部分
        open_eye_canvas.draw_rect(30, 120 - int(open_eye_closure_height), 60, int(open_eye_closure_height), clear_dsc)   # 左眼下半部分
        open_eye_canvas.draw_rect(150, 120 - int(open_eye_closure_height), 60, int(open_eye_closure_height), clear_dsc)  # 右眼下半部分

# 创建定时器，每隔30ms触发一次动画回调（比其他界面慢一些）
open_eye_anim_timer = lv.timer_create(open_eye_anim_timer_cb, 30, None)
open_eye_anim_timer.set_repeat_count(-1)  # -1表示无限循环
open_eye_anim_timer.pause()  # 默认暂停，需要时再启动


lv.scr_load(listening_screen)
 
        
#-----------------------------------------------------------------------------------------------------------

current_screen = "init_screen"
def update_screen_cb(topic,msg):
    global current_screen
    if current_screen == "speaking_screen":
        speaking_anim_timer.pause()
    elif current_screen == "sleeping_screen":
        sleep_anim_timer.pause()
    elif current_screen == "angry_screen":
        angry_anim_timer.pause()
    elif current_screen == "listening_screen":
        listening_anim_timer.pause()
    elif current_screen == "open_eye_screen":
        open_eye_anim_timer.pause()
    elif current_screen == "init_screen":
        pass
    if msg == "speaking_screen":
        speaking_anim_timer.resume()
        speaking_canvas.draw_rect(0, 0, 240, 240, clear_dsc)
        lv.scr_load(speaking_screen)
    elif msg == "sleeping_screen":
        sleep_anim_timer.resume()
        sleeping_canvas.draw_rect(0, 0, 240, 240, clear_dsc)
        lv.scr_load(sleeping_screen)
    elif msg == "angry_screen":
        angry_anim_timer.resume()
        angry_canvas.draw_rect(0, 0, 240, 240, clear_dsc)
        lv.scr_load(angry_screen)
    elif msg == "listening_screen":
        listening_anim_timer.resume()
        listening_canvas.draw_rect(0, 0, 240, 240, clear_dsc)
        lv.scr_load(listening_screen)
    elif msg == "open_eye_screen":
        open_eye_anim_timer.resume()
        open_eye_canvas.draw_rect(0, 0, 240, 240, clear_dsc)
        lv.scr_load(open_eye_screen)
    current_screen = msg

sys_bus.subscribe("update_screen",update_screen_cb)

class lvglManager:
    def __init__(self):     
        lv.scr_load(init_screen)