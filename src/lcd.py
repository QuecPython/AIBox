# Copyright (c) Quectel Wireless Solution, Co., Ltd.All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

INIT_RAW_DATA = (
    2, 0, 120,
    0, 0, 0x11,
    0, 1, 0x36,
    1, 1, 0x00,
    # 0, 1, 0x36,
    # 1, 1, 0x00,
    0, 1, 0x3A,
    1, 1, 0x05,
    0, 0, 0x21,
    0, 5, 0xB2,
    1, 1, 0x05,
    1, 1, 0x05,
    1, 1, 0x00,
    1, 1, 0x33,
    1, 1, 0x33,
    0, 1, 0xB7,
    1, 1, 0x23,
    0, 1, 0xBB,
    1, 1, 0x22,
    0, 1, 0xC0,
    1, 1, 0x2C,
    0, 1, 0xC2,
    1, 1, 0x01,
    0, 1, 0xC3,
    1, 1, 0x13,
    0, 1, 0xC4,
    1, 1, 0x20,
    0, 1, 0xC6,
    1, 1, 0x0F,
    0, 2, 0xD0,
    1, 1, 0xA4,
    1, 1, 0xA1,
    0, 1, 0xD6,
    1, 1, 0xA1,
    0, 14, 0xE0,
    1, 1, 0x70,
    1, 1, 0x06,
    1, 1, 0x0C,
    1, 1, 0x08,
    1, 1, 0x09,
    1, 1, 0x27,
    1, 1, 0x2E,
    1, 1, 0x34,
    1, 1, 0x46,
    1, 1, 0x37,
    1, 1, 0x13,
    1, 1, 0x13,
    1, 1, 0x25,
    1, 1, 0x2A,
    0, 14, 0xE1,
    1, 1, 0x70,
    1, 1, 0x04,
    1, 1, 0x08,
    1, 1, 0x09,
    1, 1, 0x07,
    1, 1, 0x03,
    1, 1, 0x2C,
    1, 1, 0x42,
    1, 1, 0x42,
    1, 1, 0x38,
    1, 1, 0x14,
    1, 1, 0x14,
    1, 1, 0x27,
    1, 1, 0x2C,
    0, 0, 0x29,
    0, 4, 0x2a,
    1, 1, 0x00,
    1, 1, 0x00,
    1, 1, 0x00,
    1, 1, 0xef,
    0, 4, 0x2b,
    1, 1, 0x00,
    1, 1, 0x00,
    1, 1, 0x01,
    1, 1, 0x3f,
    0, 0, 0x2c,

)

XSTART_H = 0xf0
XSTART_L = 0xf1
YSTART_H = 0xf2
YSTART_L = 0xf3
XEND_H = 0xE0
XEND_L = 0xE1
YEND_H = 0xE2
YEND_L = 0xE3

XSTART = 0xD0
XEND = 0xD1
YSTART = 0xD2
YEND = 0xD3


LCD_INIT_DATA = bytearray(INIT_RAW_DATA)


LCD_INVALID = bytearray((
    0, 4, 0x2a,
    1, 1, XSTART_H,
    1, 1, XSTART_L,
    1, 1, XEND_H,
    1, 1, XEND_L,
    0, 4, 0x2b,
    1, 1, YSTART_H,
    1, 1, YSTART_L,
    1, 1, YEND_H,
    1, 1, YEND_L,
    0, 0, 0x2c,
))


LCD_DISPLAY_OFF = bytearray((
    0, 0, 0x28,
    2, 0, 120,
    0, 0, 0x10,
))


LCD_DISPLAY_ON = bytearray((
    0, 0, 0x11,
    2, 0, 20,
    0, 0, 0x29,
))


LCD_WIDTH = 240
LCD_HEIGHT = 240


LCD_CLK = 26000
DATA_LINE = 1
LINE_NUM = 4
LCD_TYPE = 0
LCD_SET_BRIGHTNESS = None

CONTROL_PIN_NUMBER = 20
TE_PIN_NUMBER = 37

from machine import LCD
from machine import Pin

lcd = LCD()

lcd.lcd_init(
            LCD_INIT_DATA,
            LCD_WIDTH,
            LCD_HEIGHT,
            LCD_CLK,
            DATA_LINE,
            LINE_NUM,
            LCD_TYPE,
            LCD_INVALID,
            LCD_DISPLAY_ON,
            LCD_DISPLAY_OFF,
            LCD_SET_BRIGHTNESS,
            )
lcd.lcd_clear(0x0000)

import lvgl as lv
lv.init()
disp_buf1 = lv.disp_draw_buf_t()
buf1_1 = bytearray(LCD_WIDTH * LCD_HEIGHT * 2)
disp_buf1.init(buf1_1, None, len(buf1_1))
disp_drv = lv.disp_drv_t()
disp_drv.init()
disp_drv.draw_buf = disp_buf1
disp_drv.flush_cb =lcd.lcd_write
disp_drv.hor_res = LCD_WIDTH
disp_drv.ver_res = LCD_HEIGHT
disp_drv.sw_rotate = 1
disp_drv.rotated = lv.DISP_ROT._180  # 旋转角度
disp_drv.register()

# image cache
lv.img.cache_invalidate_src(None)
lv.img.cache_set_size(50)

lv.tick_inc(5)
lv.task_handler()
