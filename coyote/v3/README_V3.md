## Coyote Pulse Host V3 (mostly auto-translated)

### Bluetooth Features

| Service UUID | Characteristic UUID | Attributes | Name | Size (BYTE) | Description |
|:-------:| :----: |:----:|:----------------:|:--------: | :----------------: |
| 0x180C | 0x150A | Write | WRITE | Up to 20 bytes | All commands are entered in this feature |
| 0x180C | 0x150B | Notification | NOTIFY | Maximum length: 20 bytes | All response messages are returned in this feature |
| 0x180A | 0x1500 | READ/NOTIFY | 1 byte | Battery information |

> Base UUID: 0000`xxxx`-0000-1000-8000-00805f9b34fb (replace xxxx with the service/characteristic UUID)

### Bluetooth name

Pulse Host 3.0 : 47L121000
Wireless sensor: 47L120100

### Basic Principles

Coyote has two built-in independent pulse generation modules, corresponding to channels A and B respectively. 

Each pulse generation module consists of two parts: channel strength and channel waveform data.

The pulse generation module is controlled by six variables: channel strength, channel strength soft upper limit, waveform frequency, waveform strength, frequency balance parameter 1, and frequency balance parameter 2.

### Bluetooth Commands
Unlike the V2 protocol, data does not need to be converted to big and small endian.


#### B0 Instructions

The B0 instruction writes the channel intensity change and channel waveform data. The instruction data length is 20 bytes and is written every 100ms. The data of both channels are in the same instruction.


```
0xB0 (1-byte command HEAD) + serial number (4 bits) + intensity change method (4 bits) + A channel intensity value (1 byte) + B channel intensity value (1 byte) + A channel waveform frequency 4 lines (4 bytes) + A channel waveform intensity 4 lines (4 bytes) + B channel waveform frequency 4 lines (4 bytes) + B channel waveform intensity 4 lines (4 bytes)
```


##### Serial Number
The serial number range is (0b0000 \~ 0b1111). If the channel strength of the pulse host is modified in the input data, set the serial number>0, and the pulse host will return the modified channel strength from feature 0x150B with the same serial number in the B1 response message. If feedback is not needed, set the serial number to 0b0000.

It is recommended to wait for response on 150B with the same sequence number before modifying the strenght further to avoid problems.

[comment]: # Test problem cases

###### How to set the intensity
The 4 bits of intensity value interpretation are divided into two parts. The upper two bits represent channel A, and the lower two bits represent channel B.

Change method: 
0b00 -> means  the intensity of the corresponding channel does not change regardless of the intensity value

0b11 -> sets the value of the corresponding channel. If the intensity setting value of channel A is 32, then the intensity of channel A is set to 32.

0b01 -> increases intensity for corrosponding channel relatively. E.g. if the intensity setting of channel A is 15 (decimal), then the intensity of channel A is increased by 15.

0b10 -> increases intensity for corrosponding channel relatively. If the intensity setting value of channel A is 17 (decimal), then the intensity of channel A is decreased by 17.


> For example,  assume that the current pulse host's A and B channel intensity is both 10

Apart from the 0xB0 (1-byte command HEAD), the serial number (4 bits) and the waveform data, we have:

1. intensity change method: 0b0000, A value :5,  B value:5
(0b0000 0b00000000 0b00000000)   =>   intensity A: 10, intensity B: 10 (Do not change A, do not change B)

2. intensity change method: 0b0100, intensity value A: 5, intensity value B: 8
(0b0100 0b00000000 0b00000000) => intensity A: 15, intensity B: 10 (Increase A by 5, do not change B) 

3. intensity change method: 0b0010,  intensity value A: 5, intensity value B:8
(0b0010 0b00000101 0b00001000) => intensity A: 10, intensity B: 2 (Do not change A, decrease B by 8)

4. intensity change method: 0b0011, intensity value A: 5, intensity value B: 8
(0b0011 0b00000101 0b00001000) => intensity A: 10, intensity B: 8 (Do not change A, set B to 8)


5. intensity change method: 0b0110, intensity value A: 5, intensity value B: 8
(0b0110 0b00000101 0b00001000) => intensity A: 15, intensity B: 2 (Increase A by 5, decrase B by 8)

6. intensity change  method = 0b1101, intensity value A:  5, intensity value B: 8
(0b1101 0b00000101 0b00001000) => intensity A: 5, intensity B: 18 (Set A to 5, increase B by 8)

[comment]: # Check all examples

##### Channel intensity value
The channel intensity  value is 1 byte long, with a valid range of (0~200). Values ​​outside the input range are treated as 0. The absolute range of the strength of each channel of the Coyote host is also (0~200).


> eg 
Assume that the current intensity of channel A is 10 
1. intensity change method: 0b0100, intensity value A: 195
(0b0100 0b11000011 0b00000000) => intensity value A: 200 (increase A by 195 to 205, but the ceiling is 200)


2. intensity change method: 0b1000, intensity value A: 20
(0b1000 0b00010100 0b00000000) => intensity value A: 0 (decrease by 20 to -10, but the floor is 0)

3. intensity change method: 0b0100 intensity value A: 201
(0b0100 0b11001001 0b00000000) => intensity value A: 10 (increase by 201 - which is treated as 0)

4. intensity change method: 0b1100, intensity value A: 201
(0b1100 0b11001001 0b00000000) => intensity value A: 0 (set to 201 - which is treated as 0)

[comment]: # Check all examples

##### Channel waveform frequency/channel waveform intensity

The channel waveform frequency length is 1 byte, and the value range is (10 ~ 240).
The channel waveform intensity is 1 byte, and the value range is (0 ~ 100).


In the B0 instruction, 4 sets of waveform frequencies and waveform intensities are sent to each channel every 100ms.

Each set of frequency-intensity represents 25ms of waveform output, and the 4 sets of data represent 100ms of data.
If one value of the waveform date is not in the valid range, the host will discard all 4 sets of data for that
channel. This can be used to only change the frequency-intensity of one channel.

[comment]: # Test if this feature can be used to not output waveforms at all


In addition, for the channel waveform frequency, you can limit the value range to (10 ~ 1000) in your program, and then convert it to the channel waveform frequency to be sent through the following algorithm:


```
Input value range (10 ~ 1000)
waveform frequency = when(input value){
    in 10..100 -> {
        Input value
    }
    in 101..600 -> {
        (Input value - 100)/5 + 100
    }
    in 601..1000 -> {
        (Input value - 600)/10 + 200
    }
    else -> {
        10
    }
}
```

[comment]: # Check why this is useful

> For example, 
the following is an example of waveform data for channel A: 

1. The waveform frequency is 4 = {10,10,20,30}, the waveform intensity is {0,5,10,50},
=> channel A outputs the waveform normally.

2. The waveform frequency is 4 = {10,10,20,30}, the waveform intensity is {0,5,10,101}
=> channel A abandons all 4 sets of data and does not output the waveform.



#### BF Instructions

The BF command writes the channel intensity soft upper limit + waveform frequency balance parameter + waveform intensity balance parameter of the pulse host. The command data length is 7 bytes.
```
0xBF (1 byte command HEAD) + AB two-channel strength soft upper limit (2 bytes) + AB two-channel waveform frequency balance parameter (2 bytes) + AB two-channel waveform strength balance parameter (2 bytes)
```

##### Channel strength soft cap
The soft upper limit of channel strength can limit the maximum value that the pulse host channel strength can reach, and the setting is saved when the power is off. The value range is (0~200). The value outside the input range will not modify the soft upper limit.

Assuming that the soft upper limits of the AB channels are set to 150 and 30, then no matter how the intensity is modified by turning the wheel or the B0 command, the channel intensity of channel A will only be in the range (0 ~ 150), and the channel intensity of channel B will only be in the range (0 \~ 30), and the channel intensity of the pulse host will never exceed the soft upper limit.


##### Frequency balance parameters 1
The waveform frequency balance parameter will adjust the feeling of high and low frequencies of the waveform, and the setting is saved when the power is turned off. The value range is (0 \~ 255)
This parameter controls the relative sensory intensity of different frequency waveforms under fixed channel intensity. The larger the value, the stronger the impact of the low-frequency waveform.

[comment]: # Find out more about this parameter

##### Frequency balance parameters 2
The waveform intensity balance parameter will adjust the waveform pulse width, and the setting is saved when the power is turned off. The value range is (0 \~ 255)
This parameter controls the relative sensory intensity of waveforms of different frequencies under fixed channel intensity. The larger the value, the stronger the stimulation of low-frequency waveforms.

### Bluetooth response message
All data callbacks of the pulse host are returned through the characteristic Notify of 0x180C->0x150B. Please bind the notify to this characteristic after successfully connecting to the pulse host.

[comment]: # Find out more about this parameter

#### B1 Message
When the pulse host strength changes, the current strength value will be immediately returned through the B1 message. If the strength change is caused by the B0 command, the sequence number returned in the B1 command will be the same as the sequence number contained in the command that caused the change, otherwise the sequence number is 0.

```
0xB1 (1-byte command HEAD) + sequence number (1-byte) + current actual strength of channel A (1-byte) + current actual strength of channel B (1-byte)
```
#### BE Message
The BE message returns the current AB channel strength soft upper limit + AB channel waveform frequency balance parameter + AB channel waveform strength balance parameter of the pulse host after the corresponding setting of BF input.
```
0xBE (1 byte command HEAD) + AB two-channel strength soft upper limit (2 bytes) + AB two-channel waveform frequency balance parameter (2 bytes) + AB two-channel waveform strength balance parameter (2 bytes)
```

### More Examples
In summary, unlike the channel intensity/waveform data of V2, the two-channel intensity and two-channel waveform data of V3 are combined in the instruction B0. Here are some examples:


>Data = command HEAD + serial number + intensity change method + channel A intensity value + channel B intensity value + channel A waveform frequency {x,x,x,x} + channel A waveform intensity {x,x,x,x} + channel B waveform frequency {x,x,x,x} + channel B waveform intensity {x,x,x,x}

No.1 Do not modify the channel strength, channel A continuously outputs waveform: 
1-> 0xB0+0b0000+0b0000+0+0+{10,10,10,10}+{0,10,20,30}+{0,0,0,0}+{0,0,0,101} 
(HEX:0xB00000000A0A0A0A000A141E000000000000065)


2-> 0xB0+0b0000+0b0000+0+0+{15,15,15,15}+{40,50,60,70}+{0,0,0,0}+{0,0,0,101} 
(HEX:0xB00000000F0F0F0F28323C460000000000000065) 

3-> 0xB0+0b0000+0b0000+0+0+{30,30,30,30}+{80,90,100,100}+{0,0,0,0}+{0,0,0,101} 
(HEX:0xB00000001E1E1E1E505A64640000000000000065) 

4-> 0xB0+0b0000+0b0000+0+0+{40,60,80,100}+{100,90,90,90}+{0,0,0,0}+{0,0,0,101} 
(HEX:0xB0000000283C5064645A5A5A0000000000000065) 

...


No.2 The current A channel strength of the pulse host is 10, and the A channel continuously outputs waveform: 

1-> 0xB0+0b0000+0b0100+5+0+{10,10,10,10}+{0,10,20,30}+{0,0,0,0}+{0,0,0,101} 
(HEX:0xB00405000A0A0A0A000A141E0000000000000065) 

2-> 0xB0+0b0000+0b0000+0+0+{15,15,15,15}+{40,50,60,70}+{0,0,0,0}+{0,0,0,101} 
(HEX:0xB00000000F0F0F0F28323C460000000000000065) 

3-> 0xB0+0b0000+0b0000+0+0+{30,30,30,30}+{80,90,100,100}+{0,0,0,0}+{0,0,0,101} 
(HEX:0xB00000001E1E1E1E505A64640000000000000065) 

4-> 0xB0+0b0001+0b0100+10+0+{40,60,80,100}+{100,90,90,90}+{0,0,0,0}+{0,0,0,101} 
(HEX:0xB0140A00283C5064645A5A5A0000000000000065) 

... 

In 1, the A channel intensity  is set to +5. After setting, the pulse host A channel intensity will be +5, and the pulse host channel intensity will become 15, but the modified intensity will not be returned through 150B, because the sequence number is 0.

In 4, the A channel intensity is set to +10. After setting, the pulse host A channel intensity be +10, and the pulse host channel intensity A become 25. The A channel intensity:25 is returned through 150B, and the sequence number = 1.


No.3 The current A channel strength of the pulse host is 10, and the A channel continuously outputs waveform:

1-> 0xB0+0b0000+0b0000+0+0+{10,10,10,10}+{0,10,20,30}+{0,0,0,0}+{0,0,0,101} 
(HEX:0xB00000000A0A0A0A000A141E000000000000065) 

2-> 0xB0+0b0000+0b0000+0+0+{15,15,15,15}+{40,50,60,70}+{0,0,0,0}+{0,0,0,101} 
(HEX:0xB00000000F0F0F0F28323C460000000000000065) 

3-> Move the A channel dial up once and release it. 
4-> 0xB0+0b0000+0b0000+0+0+{30,30,30,30}+{80,90,100,100}+{0,0,0,0}+{0,0,0,101} 
(HEX:0xB00000001E1E1E1E505A6464000000000000065) 

5-> 0xB0+0b0000+0b0000+0+0+{40,60,80,100}+{100,90,90,90}+{0,0,0,0}+{0,0,0,101} 
(HEX:0xB0000000283C5064645A5A5A0000000000000065) 

... 

In 3, if you push the A channel dial upward once and then release it, the pulse host A channel intensity will increase by 1, and the A channel intensity will be returned through 150B = 11, and the serial number = 0.
[comment]: # Why is the serial number 0 here?


No.4 Without modifying the channel strength, both channels A and B output waveforms continuously: 

1-> 0xB0+0b0000+0b0000+0+0+{10,10,10,10}+{0,10,20,30}+{10,10,10,10}+{0,0,0,0} 
(HEX:0xB00000000A0A0A0A000A141E0A0A0A0A0000000) 

2-> 0xB0+0b0000+0b0000+0+0+{15,15,15,15}+{40,50,60,70}+{10,10,10,10}+{10,10,10,10} 
(HEX:0xB00000000F0F0F0F28323C460A0A0A0A0A0A0A0A) 

3-> 0xB0+0b0000+0b0000+0+0+{30,30,30,30}+{80,90,100,100}+{10,10,10,10}+{0,0,0,10} 
(HEX:0xB00000001E1E1E1E505A64640A0A0A0A0000000A) 

4-> 0xB0+0b0000+0b0000+0+0+{40,60,80,100}+{0,90,90,90}+{10,10,10,10}+{0,0,0,10} 
(HEX:0xB0000000283C5064005A5A5A0A0A0A0A0000000A)

...

Examples of serial number and intensity input (taking channel A as an example):
```


isInputAllowed = true (Whether input intensity is currently allowed)
accumulatedStrengthValueA = 0 (the accumulated intensity change value not written to channel A)
deviceStrengthValueA = 0 (current A channel intensity value of the pulse host)
orderNo = 0 (sequence number)
inputOrderNo = 0 (the sequence number written in B0)
strengthParsingMethod = 0b0000 (intensity value interpretation method)
strengthSettingValueA = 0 (intensity setting value of channel A)

A channel intensity related data processing function
fun strengthDataProcessingA():Unit{
    if(isInputAllowed == true) {
         strengthParsingMethod = if(accumulatedStrengthValueA > 0){
             0b0100
         }else if(accumulatedStrengthValueA < 0){
             0b1000
         }else{
             0b0000
         }
         orderNo += 1
         inputOrderNo = orderNo
         isInputAllowed = false
         strengthSettingValueA = abs(accumulatedStrengthValueA) (absolute value)
         accumulatedStrengthValueA = 0
     }else{
         orderNo = 0
         strengthParsingMethod = 0b0000
         strengthSettingValueA = 0
     }
}
A channel strength response message processing function
fun strengthDataCallback(returnOrderNo : Int,returnStrengthValueA : Int):Unit{
    //returnOrderNo returns the input sequence number
    //returnStrengthValueA returns the current strength of channel A of the pulse host
    
    deviceStrengthValueA = returnStrengthValueA
    if(returnOrderNo == inputNo){
         isInputAllowed = true
         strengthParsingMethod = 0b0000
         strengthSettingValueA = 0
         inputOrderNo = 0
     }
}
A channel intensity is set to 0
fun strengthZero():Unit{
    strengthParsingMethod = 0b1100
    strengthSettingValueA = 0
    orderNo = 1
    inputOrderNo = orderNo
}


[comment]: # Get code to run
```

The following sequence is chronological, but the sequence numbers do not represent a specific moment:

```
1 -> Press the A channel intensity '+' button
     accumulatedStrengthValueA += 1(value=1)

2 -> (100ms period) B0 is ready to write
     strengthDataProcessingA()
BLE WRITE 150A(0xB0 + orderNo(0b0001) + strengthParsingMethod(0b0100) + strengthSettingValueA(1) + ...)
3 -> (100ms period) B0 is ready to write
     strengthDataProcessingA()
     BLE WRITE 150A(0xB0 + orderNo(0b0000) + strengthParsingMethod(0b0000) + strengthSettingValueA(1) + ...)
3 -> 150B Returns the intensity value of channel A
     BLE NOTIFY 150B(0xB1 + returnOrderNo(1) + returnStrengthValueA(1) + ...)
     Returned sequence number = 1, returned A channel strength = 1
     strengthDataCallback(1,1)
4 -> Press the A channel intensity '+' button    
     accumulatedStrengthValueA += 1(value=1)
5 -> Press the A channel intensity '+' button
     accumulatedStrengthValueA += 1(value=2)
6 -> Press the A channel intensity '+' button
     accumulatedStrengthValueA += 1(value=3)
7 -> (100ms period) B0 is ready to write
     strengthDataProcessingA()
     BLE WRITE 150A(0xB0 + orderNo(0b0001) + strengthParsingMethod(0b0100) + strengthSettingValueA(3) + ...)
8 -> Press the A channel intensity '+' button
     accumulatedStrengthValueA += 1(value=1)  
9 -> (100ms period) B0 is ready to write
     strengthDataProcessingA()
     BLE WRITE 150A(0xB0 + orderNo(0b0000) + strengthParsingMethod(0b0000) + strengthSettingValueA(0) + ...)     
10->150B Returns the intensity value of channel A
     BLE NOTIFY 150B(0xB1 + returnOrderNo(1) + returnStrengthValueA(4) + ...)
     Returned sequence number = 1, returned A channel strength = 4
     strengthDataCallback(1,4)     
11->Press the A channel intensity '+' button
     accumulatedStrengthValueA += 1(value=2)
12-> (100ms cycle) B0 is ready to write
     strengthDataProcessingA()
     BLE WRITE 150A(0xB0 + orderNo(0b0001) + strengthParsingMethod(0b0100) + strengthSettingValueA(2) + ...)
13-> Press the A channel intensity '-' button
     accumulatedStrengthValueA -= 1(value= -1)
14->150B Returns the intensity value of channel A
     BLE NOTIFY 150B(0xB1 + returnOrderNo(1) + returnStrengthValueA(6) + ...)
     Returned sequence number = 1, returned channel A strength = 6
     strengthDataCallback(1,6)
15-> (100ms period) B0 is ready to write
     strengthDataProcessingA()
     BLE WRITE 150A(0xB0 + orderNo(0b0010) + strengthParsingMethod(0b1000) + strengthSettingValueA(1) + ...)
16->150B Returns the intensity value of channel A
     BLE NOTIFY 150B(0xB1 + returnOrderNo(2) + returnStrengthValueA(5) + ...)
     Returned sequence number = 2, returned channel A strength = 5
     strengthDataCallback(1,5)
17-> (100ms period) B0 is ready to write
     strengthZero()
     BLE WRITE 150A(0xB0 + orderNo(0b0001) + strengthParsingMethod(0b1100) + strengthSettingValueA(0) + ...)
18->150B Returns the intensity value of channel A
     BLE NOTIFY 150B(0xB1 + returnOrderNo(1) + returnStrengthValueA(0) + ...)
     Returned sequence number = 1, returned A channel strength = 0
     strengthDataCallback(1,0)
......     
```

[comment]: # Check example



## 郊狼情趣脉冲主机V3

### 蓝牙特性

| 服务UUID  | 特性UUID |  属性  |      名称      | 大小(BYTE) |       说明       |
|:-------:| :----: |:----:|:------------:|:--------:| :------------: |
| 0x180C  | 0x150A |  写   |    WRITE     |  最长20字节  |  所有的指令都在该特性输入  |
| 0x180C  | 0x150B |  通知  |    NOTIFY    |  最长20字节  | 所有的回应消息都在该特性返回 |
|  0x180A | 0x1500 | 读/通知 |  READ/NOTIFY | 1字节 |   电量信息   |

> 基础UUID：0000`xxxx`-0000-1000-8000-00805f9b34fb(将xxxx替换为服务/特性UUID)

### 蓝牙名称

脉冲主机3.0 : 47L121000

无线传感器 : 47L120100

### 基本原理

郊狼内置了两组独立的脉冲生成模块，分别对应A，B两个通道。<br />每组脉冲生成模块由通道强度和通道波形数据两部分构成。<br />通过通道强度，通道强度软上限，波形频率，波形强度，频率平衡参数1，频率平衡参数2 六个变量来控制脉冲生成模块

### 蓝牙指令
与V2协议不同的是，数据无需进行大小端转换

#### B0指令

B0指令写入通道强度变化和通道波形数据,指令数据长度为20字节，每100ms写入。两通道的数据都在同一条指令中。
```
0xB0(1byte指令HEAD)+序列号(4bits)+强度值解读方式(4bits)+A通道强度设定值(1byte)+B通道强度设定值(1byte)+A通道波形频率4条(4bytes)+A通道波形强度4条(4bytes)+B通道波形频率4条(4bytes)+B通道波形强度4条(4bytes)
```
##### 序列号

序列号范围(0b0000 \~ 0b1111),如果输入的数据中修改了脉冲主机的通道强度，设置序列号 >0,脉冲主机会通过B1回应消息以相同的序列号将修改后的通道强度从特性0x150B返回，如果不需要脉冲主机反馈通道强度，则序列号设置0b0000即可。
另外，为避免产生问题，当通过B0指令修改通道强度且序列号不为0时，建议等待150B返回B1且为相同序列号的信息后，再对通道强度进行修改。

##### 强度值解读方式

强度值解读方式的4bits分为两个部分，高两位bits代表A通道解读方式，低两位bits代表B通道解读方式。<br />解读方式:<br />0b00 -> 代表对应通道强度不做改变，对应通道的强度设定值无论是什么都无效<br />0b01 -> 代表对应通道强度相对增加变化，若A通道强度设定值为15(10进制)，那么A通道强度增加15<br />0b10 -> 代表对应通道强度相对减少变化，若A通道强度设定值为17(10进制)，那么A通道强度减少17<br />0b11 -> 代表对应通道强度绝对变化，若A通道强度设定值为32，那么A通道强度设置为32

> e.g<br />假设当前脉冲主机的A通道强度为10，B通道强度为10。<br />1.  强度值解读方式=0b0000，A通道强度设定值=5，B通道强度设置定=8，B0指令输入后，脉冲主机的A通道强度 = 10，B通道强度 = 10<br />2. 强度值解读方式=0b0100，A通道强度设定值=5，B通道强度设定值=8，B0指令输入后，脉冲主机的A通道强度 = 15，B通道强度 = 10<br />3. 强度值解读方式=0b0010，A通道强度设定值=5，B通道强度设定值=8，B0指令输入后，脉冲主机的A通道强度 = 10，B通道强度 = 2<br />4. 强度值解读方式=0b0011，A通道强度设定值=5，B通道强度设定值=8，B0指令输入后，脉冲主机的A通道强度 = 10，B通道强度 = 8<br />5. 强度值解读方式=0b0110，A通道强度设定值=5，B通道强度设定值=8，B0指令输入后，脉冲主机的A通道强度 = 15，B通道强度 = 2<br />6. 强度值解读方式=0b1101，A通道强度设定值=5，B通道强度设定值=8，B0指令输入后，脉冲主机的A通道强度 = 5，B通道强度 = 18

##### 通道强度设定值

通道强度设定值长度为1字节，值有效范围(0~ 200),输入范围外的值均以0处理。郊狼主机每个通道的强度绝对范围也是(0 ~ 200)。

> e.g<br />假设当前脉冲主机的A通道强度为10<br />1. 强度值解读方式=0b0100，A通道强度设定值=195，B0指令输入后，脉冲主机的A通道强度 = 200<br />2. 强度值解读方式=0b1000，A通道强度设定值=20，B0指令输入后，脉冲主机的A通道强度 = 0<br />3. 强度值解读方式=0b0100，A通道强度设定值=201，B0指令输入后，脉冲主机的A通道强度 = 10<br />4. 强度值解读方式=0b1100，A通道强度设定值=201，B0指令输入后，脉冲主机的A通道强度 = 0<br />

##### 通道波形频率/通道波形强度

通道波形频率长度1byte,值范围(10~ 240)，通道波形强度1byte，值范围(0 ~ 100)。
在B0指令中，每100ms要发送两通道各4组波形频率和波形强度，每组频率-强度代表了25ms的波形输出，4组数据代表了100ms数据。
在波形数据中，若某通道的输入值不在有效范围，则脉冲主机会放弃掉该通道全部4组数据。

另外对于通道波形频率，在您的程序中可以将值范围限制在(10 ~ 1000),然后通过以下算法换算为要发送的通道波形频率：
```
输入值范围(10 ~ 1000)
波形频率 = when(输入值){
    in 10..100 -> {
        输入值
    }
    in 101..600 -> {
        (输入值 - 100)/5 + 100
    }
    in 601..1000 -> {
        (输入值 - 600)/10 + 200
    }
    else -> {
        10
    }
}
```

> e.g<br />以下举例A通道波形数据<br />1. 波形频率4条={10,10,20,30}，波形强度={0,5,10,50}，B0指令输入后，A通道正常输出波形<br />2. 波形频率4条={10,10,20,30}，波形强度={0,5,10,101}，B0指令输入后，A通道放弃全部4组数据，不输出波形

*   Tips 如果当前只想向单个通道输出波形，则将另一个通道的数据中输入至少一个非有效数据(一条大于100的波形强度值)，如上e.g所示。

#### BF指令

BF指令写入脉冲主机的通道强度软上限+波形频率平衡参数+波形强度平衡参数，指令数据长度为7字节。
```
0xBF(1byte指令HEAD)+AB两通道强度软上限(2bytes)+AB两通道波形频率平衡参数(2btyes)+AB两通道波形强度平衡参数(2bytes)
```
##### 通道强度软上限

通道强度软上限可以限制脉冲主机通道强度能达到的最大值，并且该设置断电保存，值范围(0~ 200)，输入范围外的值则不会修改软上限。
假设设置AB通道软上限为150和30，那么通过拨动滚轮或B0指令无论如何修改强度，A通道的通道强度只会在范围(0 ~ 150),B通道的通道强度只会在范围(0 \~ 30)，脉冲主机的通道强度一定不会超过软上限。

##### 频率平衡参数1

波形频率平衡参数会调整波形高低频的感受，并且该设置断电保存，值范围(0 \~ 255)
本参数控制固定通道强度下，不同频率波形的相对体感强度。值越大，低频波形冲击感越强。

##### 频率平衡参数2

波形强度平衡参数会调整波形脉冲宽度，并且该设置断电保存，值范围(0 \~ 255)
本参数控制固定通道强度下，不同频率波形的相对体感强度。值越大，低频波形刺激越强。

### 蓝牙回应消息

脉冲主机所有的数据回调都通过0x180C->0x150B的特性Notify返回，请在成功连接脉冲主机后对该特性绑定notify。

#### B1消息

当脉冲主机强度发生变化时，会立刻通过B1消息返回当前的强度值。如果是由于B0指令导致的强度变化，返回B1指令中序列号将会与引起此变化的命令所包含的序列号相同，否则序列号为0。
```
0xB1(1byte指令HEAD)+序列号(1byte)+A通道当前实际强度(1byte)+B通道当前实际强度(1byte)
```
#### BE消息

BE消息返回BF输入的对应设置后脉冲主机当前的AB通道强度软上限+AB通道波形频率平衡参数+AB通道波形强度平衡参数。
```
0xBE(1byte指令HEAD)+AB两通道强度软上限(2bytes)+AB两通道波形频率平衡参数(2btyes)+AB两通道波形强度平衡参数(2bytes)
```

### 更多例子
综上所述，不同于V2的通道强度/波形数据的是，V3的两通道强度和两通道波形数据都捏合在了B0这一个指令中，以下举若干例子：
>数据 = 指令HEAD + 序列号 + 强度值解读方式 + A通道强度设定值 + B通道强度设定值 + A通道波形频率{x,x,x,x} + A通道波形强度{x,x,x,x} + B通道波形频率{x,x,x,x} + B通道波形强度{x,x,x,x}

No.1 不修改通道强度，A通道连续输出波形:<br/>
1-> 0xB0+0b0000+0b0000+0+0+{10,10,10,10}+{0,10,20,30}+{0,0,0,0}+{0,0,0,101}<br/>(HEX:0xB00000000A0A0A0A000A141E0000000000000065)<br/>
2-> 0xB0+0b0000+0b0000+0+0+{15,15,15,15}+{40,50,60,70}+{0,0,0,0}+{0,0,0,101}<br/>(HEX:0xB00000000F0F0F0F28323C460000000000000065)<br/>
3-> 0xB0+0b0000+0b0000+0+0+{30,30,30,30}+{80,90,100,100}+{0,0,0,0}+{0,0,0,101}<br/>(HEX:0xB00000001E1E1E1E505A64640000000000000065)<br/>
4-> 0xB0+0b0000+0b0000+0+0+{40,60,80,100}+{100,90,90,90}+{0,0,0,0}+{0,0,0,101}<br/>(HEX:0xB0000000283C5064645A5A5A0000000000000065)<br/>
...<br/>

No.2 脉冲主机当前A通道强度=10，A通道连续输出波形:<br/>
1-> 0xB0+0b0000+0b0100+5+0+{10,10,10,10}+{0,10,20,30}+{0,0,0,0}+{0,0,0,101}<br/>(HEX:0xB00405000A0A0A0A000A141E0000000000000065)<br/>
2-> 0xB0+0b0000+0b0000+0+0+{15,15,15,15}+{40,50,60,70}+{0,0,0,0}+{0,0,0,101}<br/>(HEX:0xB00000000F0F0F0F28323C460000000000000065)<br/>
3-> 0xB0+0b0000+0b0000+0+0+{30,30,30,30}+{80,90,100,100}+{0,0,0,0}+{0,0,0,101}<br/>(HEX:0xB00000001E1E1E1E505A64640000000000000065)<br/>
4-> 0xB0+0b0001+0b0100+10+0+{40,60,80,100}+{100,90,90,90}+{0,0,0,0}+{0,0,0,101}<br/>(HEX:0xB0140A00283C5064645A5A5A0000000000000065)<br/>
...<br/>
1中设置A通道强度+5,设置后脉冲主机A通道强度会+5，脉冲主机通道强度变为15，但不会通过150B返回修改后的通道强度，因为序列号=0.<br/>
4中设置A通道强度+10，设置后脉冲主机A通道强度会+10，脉冲主机通道强度变为25，并通过150B返回A通道强度 = 25，序列号 = 1.<br/>

No.3 脉冲主机当前A通道强度=10，A通道连续输出波形:<br/>
1-> 0xB0+0b0000+0b0000+0+0+{10,10,10,10}+{0,10,20,30}+{0,0,0,0}+{0,0,0,101}<br/>(HEX:0xB00000000A0A0A0A000A141E0000000000000065)<br/>
2-> 0xB0+0b0000+0b0000+0+0+{15,15,15,15}+{40,50,60,70}+{0,0,0,0}+{0,0,0,101}<br/>(HEX:0xB00000000F0F0F0F28323C460000000000000065)<br/>
3-> 向上拨动一次A通道拨轮后放开<br/>
4-> 0xB0+0b0000+0b0000+0+0+{30,30,30,30}+{80,90,100,100}+{0,0,0,0}+{0,0,0,101}<br/>(HEX:0xB00000001E1E1E1E505A64640000000000000065)<br/>
5-> 0xB0+0b0000+0b0000+0+0+{40,60,80,100}+{100,90,90,90}+{0,0,0,0}+{0,0,0,101}<br/>(HEX:0xB0000000283C5064645A5A5A0000000000000065)<br/>
...<br/>
3中向上拨动一次A通道拨轮后放开，脉冲主机A通道强度会+1，并通过150B返回A通道强度 = 11，序列号 = 0.<br/>

No.4 不修改通道强度，AB两通道均连续输出波形:<br/>
1-> 0xB0+0b0000+0b0000+0+0+{10,10,10,10}+{0,10,20,30}+{10,10,10,10}+{0,0,0,0}<br/>(HEX:0xB00000000A0A0A0A000A141E0A0A0A0A00000000)<br/>
2-> 0xB0+0b0000+0b0000+0+0+{15,15,15,15}+{40,50,60,70}+{10,10,10,10}+{10,10,10,10}<br/>(HEX:0xB00000000F0F0F0F28323C460A0A0A0A0A0A0A0A)<br/>
3-> 0xB0+0b0000+0b0000+0+0+{30,30,30,30}+{80,90,100,100}+{10,10,10,10}+{0,0,0,10}<br/>(HEX:0xB00000001E1E1E1E505A64640A0A0A0A0000000A)<br/>
4-> 0xB0+0b0000+0b0000+0+0+{40,60,80,100}+{0,90,90,90}+{10,10,10,10}+{0,0,0,10}<br/>(HEX:0xB0000000283C5064005A5A5A0A0A0A0A0000000A)<br/>
...

关于序列号与强度输入的例子(以A通道举例):
```
isInputAllowed = true(当前是否允许输入强度)
accumulatedStrengthValueA = 0(A通道未写入的累计强度变化值)
deviceStrengthValueA = 0(脉冲主机当前A通道强度值)
orderNo = 0(序列号)
inputOrderNo = 0(B0写入的序列号)
strengthParsingMethod = 0b0000(强度值解读方式)
strengthSettingValueA = 0(A通道强度设定值)

A通道强度相关数据处理函数
fun strengthDataProcessingA():Unit{
    if(isInputAllowed == true) {
         strengthParsingMethod = if(accumulatedStrengthValueA > 0){
             0b0100
         }else if(accumulatedStrengthValueA < 0){
             0b1000
         }else{
             0b0000
         }
         orderNo += 1
         inputOrderNo = orderNo
         isInputAllowed = false
         strengthSettingValueA = abs(accumulatedStrengthValueA)(取绝对值)
         accumulatedStrengthValueA = 0
     }else{
         orderNo = 0
         strengthParsingMethod = 0b0000
         strengthSettingValueA = 0
     }
}
A通道强度回应消息处理函数
fun strengthDataCallback(returnOrderNo : Int,returnStrengthValueA : Int):Unit{
    //returnOrderNo 返回输入的序列号
    //returnStrengthValueA 返回脉冲主机当前A通道强度
    
    deviceStrengthValueA = returnStrengthValueA
    if(returnOrderNo == inputNo){
         isInputAllowed = true
         strengthParsingMethod = 0b0000
         strengthSettingValueA = 0
         inputOrderNo = 0
     }
}
A通道强度设置0
fun strengthZero():Unit{
    strengthParsingMethod = 0b1100
    strengthSettingValueA = 0
    orderNo = 1
    inputOrderNo = orderNo
}
```
以下顺序为时间顺序，但序号并不代表某个具体时刻:<br/>
```
1 -> 按下A通道强度‘+’按钮
     accumulatedStrengthValueA += 1(值 = 1)
2 -> (100ms周期)B0准备写入
     strengthDataProcessingA()
     BLE WRITE 150A(0xB0 + orderNo(0b0001) + strengthParsingMethod(0b0100) + strengthSettingValueA(1) + ......)
3 -> (100ms周期)B0准备写入
     strengthDataProcessingA()
     BLE WRITE 150A(0xB0 + orderNo(0b0000) + strengthParsingMethod(0b0000) + strengthSettingValueA(1) + ......)
3 -> 150B返回A通道强度值
     BLE NOTIFY 150B(0xB1 + returnOrderNo(1) + returnStrengthValueA(1) + ......)
     返回的序列号 = 1，返回的A通道强度 = 1
     strengthDataCallback(1,1)
4 -> 按下A通道强度‘+’按钮    
     accumulatedStrengthValueA += 1(值 = 1)
5 -> 按下A通道强度‘+’按钮 
     accumulatedStrengthValueA += 1(值 = 2)
6 -> 按下A通道强度‘+’按钮 
     accumulatedStrengthValueA += 1(值 = 3)
7 -> (100ms周期)B0准备写入
     strengthDataProcessingA()
     BLE WRITE 150A(0xB0 + orderNo(0b0001) + strengthParsingMethod(0b0100) + strengthSettingValueA(3) + ......)
8 -> 按下A通道强度‘+’按钮 
     accumulatedStrengthValueA += 1(值 = 1)  
9 -> (100ms周期)B0准备写入
     strengthDataProcessingA()
     BLE WRITE 150A(0xB0 + orderNo(0b0000) + strengthParsingMethod(0b0000) + strengthSettingValueA(0) + ......)     
10-> 150B返回A通道强度值
     BLE NOTIFY 150B(0xB1 + returnOrderNo(1) + returnStrengthValueA(4) + ......)
     返回的序列号 = 1，返回的A通道强度 = 4
     strengthDataCallback(1,4)     
11-> 按下A通道强度‘+’按钮 
     accumulatedStrengthValueA += 1(值 = 2)
12-> (100ms周期)B0准备写入
     strengthDataProcessingA()
     BLE WRITE 150A(0xB0 + orderNo(0b0001) + strengthParsingMethod(0b0100) + strengthSettingValueA(2) + ......)
13-> 按下A通道强度‘-’按钮 
     accumulatedStrengthValueA -= 1(值 = -1)
14-> 150B返回A通道强度值
     BLE NOTIFY 150B(0xB1 + returnOrderNo(1) + returnStrengthValueA(6) + ......)
     返回的序列号 = 1，返回的A通道强度 = 6
     strengthDataCallback(1,6) 
15-> (100ms周期)B0准备写入
     strengthDataProcessingA()
     BLE WRITE 150A(0xB0 + orderNo(0b0010) + strengthParsingMethod(0b1000) + strengthSettingValueA(1) + ......)
16-> 150B返回A通道强度值
     BLE NOTIFY 150B(0xB1 + returnOrderNo(2) + returnStrengthValueA(5) + ......)
     返回的序列号 = 2，返回的A通道强度 = 5
     strengthDataCallback(1,5)
17-> (100ms周期)B0准备写入
     strengthZero()
     BLE WRITE 150A(0xB0 + orderNo(0b0001) + strengthParsingMethod(0b1100) + strengthSettingValueA(0) + ......)
18-> 150B返回A通道强度值
     BLE NOTIFY 150B(0xB1 + returnOrderNo(1) + returnStrengthValueA(0) + ......)
     返回的序列号 = 1，返回的A通道强度 = 0
     strengthDataCallback(1,0) 
......     
```
