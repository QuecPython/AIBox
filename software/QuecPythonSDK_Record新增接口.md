## vad_set_callback

```
Record.vad_set_callback(cb)
```

* 功能：

  该方法用于设置人声检测回调。

* 参数：

  `cb`：回调函数，回调返回说明：int类型，`1`-有人开始讲话，`0`-讲话结束

* 返回值：

`0`：成功，返回其他失败

示例：

```python
from audio import Record

rec = Record(0)
def vad_cb(para):
    print("cb:", para)
    
rec.vad_set_callback(vad_cb)
```

## vad_set_callback_v2

```
Record.vad_set_callback_v2(cb)
```

* 功能：

  该方法用于设置人声检测回调。

* 参数：

  `cb`：回调函数，回调返回说明：返回一个元组`(status, data_len, vol)`，具体说明如下：

  | 参数       | 类型 | 说明                                             |
  | ---------- | ---- | ------------------------------------------------ |
  | `status`   | int  | `1`-有人开始讲话，`0`-讲话结束，`2`-人声音频数据 |
  | `data_len` | int  | 人声音频数据长度                                 |
  | `vol`      | int  | 音量                                             |

* 返回值：

`0`：成功，返回其他失败

示例：

```python
from audio import Record

rec = Record(0)
def vad_v2_cb(para):
    global buff
    global play
    print("cb:", para)
    if para[0] == 1:
        print("start speak")
    elif para[0] == 0:
        print("end speak")
        play = 1
    elif para[0] == 2:
        print("data len =",para[1])
        print("vol =",para[2])
        buf = bytearray(para[1])
        rec.vad_read_data(buf, para[1])
        buff = buff + buf


rec.vad_set_callback_v2(vad_v2_cb)
```

## vad_read_data

```
Record.vad_read_data(read_buf, len)
```

* 功能：

  该方法用于读取人声音频数据。

* 参数：

  `read_buf `- 录音流buf，bytearray型 。

  `len `- 读取的长度，int类型。

* 返回值：

成功返回实际读取的字节数，失败返回`-1`。

> 注意：收到回调通知，应及时读取音频流。目前是采用循环buf，最大缓存8K字节数据，不及时读取，会导致数据丢失。

## vad_start

```
Record.vad_start()
```

* 功能：

  该方法用于开启人声检测。检测结果通过回调返回。

* 参数：

  无

* 返回值：

`0`：成功，返回其他失败

## vad_stop

```
Record.vad_stop()
```

* 功能：

  该方法用于关闭人声检测释放资源。

* 参数：

  无

* 返回值：

`0`：成功，返回其他失败

## vad_get_version

```python
Record.vad_get_version()
```

* 功能：

  该方法用于查询人声检测库版本信息。

* 参数：

  无

* 返回值：

`0`：成功，返回其他失败

## ovkws_set_callback

```python
Record.ovkws_set_callback(cb)
```

* 功能：

  该方法用于设置唤醒词回调。

* 参数：

  `cb`：回调函数，回调返回说明：返回一个元组`(sta, wake_number)`

  `sta`-int类型，`1`-等待唤醒，进入唤醒模式，`0`-被唤醒，进入命令模式

  `wake_number`-int类型，表示是第几个唤醒词，唤醒词从1开始，0表示识别失败

* 返回值：

`0`：成功，返回其他失败

## ovkws_start

```python
Record.ovkws_start(wake_str_list, sensitivity, cmd_mode_time)
```

* 功能：

  该方法用于启动唤醒词唤醒功能。

* 参数：

  `wake_str_list`：唤醒词，list类型，中文唤醒词使用拼音，每个字前必须使用下划线做开始

  `sensitivity`：灵敏度，float类型，`[0.0, 1.0]`，可缺省，默认值为0.7

  `cmd_mode_time`：命令模式持续时间，int类型，单位秒，使用唤醒词唤醒后进入命令模式，命令模式持续时间结束后重新等待唤醒，可缺省，默认值为1

* 返回值：

`0`：成功，返回其他失败

## ovkws_stop

```python
Record.ovkws_stop()
```

* 功能：

  该方法用于关闭唤醒词唤醒功能。

* 参数：

  无

* 返回值：

`0`：成功，返回其他失败



## #####
