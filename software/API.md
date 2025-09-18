# 主要API功能与参数说明

## 1. AudioManager 类

**文件位置**：`utils.py`

### 主要功能

负责音频的录制、播放、Opus编解码、VAD（语音活动检测）、KWS（关键词唤醒）等音频相关操作。

------

### 构造方法

def __init__(self, channel=0, volume=10, pa_number=29)

- **channel**：音频通道号，默认0。
- **volume**：音量，默认10。
- **pa_number**：功放控制引脚编号，默认29。

------

### 主要方法

#### 音频文件播放相关

```python
def play(self, file)
```

- **file**：音频文件路径。
  播放指定音频文件。

```python
def stop(self)
```

停止所有音频播放。

------

#### Opus编解码相关

```python
def open_opus(self)
```

初始化Opus编解码器和PCM。

```python
def close_opus(self)
```

关闭Opus编解码器和PCM。

```python
def opus_read(self)
```

读取一帧Opus编码音频数据。

```python
def opus_write(self, data)
```

- **data**：Opus编码音频数据。
  写入一帧Opus编码音频数据进行播放。

------

#### VAD（语音活动检测）与KWS（关键词唤醒）

```python
def set_kws_cb(self, cb)
```

- **cb**：关键词唤醒回调函数。
  设置KWS回调。

```python
def set_vad_cb(self, cb)
```

- **cb**：语音活动检测回调函数。
  设置VAD回调。

```python
def start_kws(self)
```

启动关键词唤醒检测。

```python
def stop_kws(self)
```

停止关键词唤醒检测。

```python
def start_vad(self)
```

启动语音活动检测。

```python
def stop_vad(self)
```

停止语音活动检测。

------

### 典型用法举例

在 _main.py 的 Application 类中，音频管理的典型调用如下：

```python
self.audio_manager = AudioManager()

self.audio_manager.set_kws_cb(self.on_keyword_spotting)

self.audio_manager.set_vad_cb(self.on_voice_activity_detection)

self.audio_manager.open_opus()

self.audio_manager.play("test.wav")

self.audio_manager.stop()
```



------

### 相关API在主流程中的调用

在 _main.py 的 __chat_process 方法中：

```python
if self.__voice_activity_event.is_set():

  # 有人声

  sys_bus.publish("update_status","listening")

  if not is_listen_flag:
 	self.__protocol.abort()
	self.__protocol.listen("start")
	is_listen_flag = True
  self.__protocol.send(data)

else:

  if is_listen_flag:
	self.__protocol.listen("stop")
	is_listen_flag = False
```



- 检测到人声时，self.__protocol.abort()停止音频流播放

------

## 2. WebSocketClient类

**文件**：protocol.py

### 主要功能

与服务器建立WebSocket连接，收发音频和JSON消息，处理协议交互。

### 主要方法

- **`__init__(self, host=WSS_HOST, debug=WSS_DEBUG)`**
  初始化WebSocket客户端。
  
- **`set_callback(self, audio_message_handler, json_message_handler)`**
  设置音频和JSON消息回调。
  - audio_message_handler: 处理音频消息的回调
  - json_message_handler: 处理JSON消息的回调
  
- **connect(self)**
  建立/断开WebSocket连接。
  
- **`send(self, data)`**
  发送数据到服务器。
  
- **recv(self)**
  接收服务器数据。
  
- **hello(self)**
  发送hello握手消息，获取服务器响应。
  
- **`listen(self, state, mode="auto", session_id="")`**
  控制服务器监听状态。
  - `state`: "start"（开始识别）、"stop"（停止识别）、"detect"（唤醒词检测）
  - `mode`: 监听模式（"auto"、"manual"、"realtime"）
  
- **`wakeword_detected(self, wakeword, session_id="")`**
  通知服务器唤醒词被检测到。
  - `wakeword`: 唤醒词文本
  
- **`mcp_initialize(self)`**
  响应服务器mcp的连接请求

- **`mcp_tools_list(self)`**

  告知智能体本地有哪些可调用的方法，并说明方法的调用场景

- **`mcp_tools_call(self)`**

  响应服务器的方法调用请求

- **`mcp_notify(self)`**

  设备主动发送mcp消息



## 3. Application（主流程）

**文件**：_main.py

### 主要功能

整合音频、网络、协议、UI、任务等模块，管理主流程。

### 主要方法

- **run(self)**
  启动应用，开启充电、音频、关键词唤醒。

- **`on_keyword_spotting(self, state)`**
  关键词唤醒回调。

- **`on_voice_activity_detection(self, state)`**
  语音活动检测回调。

- **`on_audio_message(self, raw)`**
  处理音频消息。

- **`on_json_message(self, msg)`**
  处理JSON消息。

- **__chat_process(self)**
  主对话流程，负责音频流读取、状态切换、协议交互。

  - 典型片段：

    ```python
    if self.__voice_activity_event.is_set():
        sys_bus.publish("update_status","listening")
        if not is_listen_flag:
    		self.audio_manager.stop()
    		self.audio_manager.aud.stopPlayStream()
    		self.__protocol.listen("start")
            is_listen_flag = True
        self.__protocol.send(data)
    else:
        if is_listen_flag:
    	    self.__protocol.listen("stop")
    	    is_listen_flag = False
    ```

    

## 4. UI相关（表情与状态显示）

**文件**：**`ui.py`**

### 主要功能

负责屏幕UI初始化、表情动画、界面切换等。

### 主要方法

- **`update_emoji(topic, msg)`**
  根据消息切换表情动画。
  
- **`lv.scr_load(screen)`**

  加载屏幕对象到显示缓冲区

- **`sys_bus.subscribe("update_emoji", update_emoji)`**

  会话总线，接收智能体下发的表情标签

## 5. 其他管理器

### ChargeManager（充电管理）

- **enable_charge(self)**
  使能充电。
- **disable_charge(self)**
  禁用充电。

### NetManager（网络管理）

- **wait_network_ready(self)**
  等待网络准备好，自动处理无卡、无信号等情况。

### TaskManager（任务调度）

- `submit(self, func, args=(), kwargs={}, priority=0, title="anon")`

  提交任务到队列。

  - func: 任务函数
  - args: 参数
  - priority: 优先级



## 6. 典型调用说明

- self.__protocol.abort()
  停止所有音频播放，常用于切换识别状态时清理音频缓存。