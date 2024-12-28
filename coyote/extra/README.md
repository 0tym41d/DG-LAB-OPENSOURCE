## Coyote Pulse Waveform (auto-translated)

In this article, we will partially explain the waveform protocol of the Coyote Pulse Host to help the majority of Coyote enthusiasts better understand the data principle of the pulse waveform.

### Concept Explanation

#### Waveform frequency

The coyote program divides each second into 1000 milliseconds, and can generate a pulse in each millisecond. We encode the pattern of pulse generation by controlling the pulse and the interval.

The waveform frequency represents the duration of one output unit (an output unit consists of X pulses and Y intervals) and is measured in milliseconds.

So if you want to output a 1Hz waveform, the actual waveform frequency = 1000ms; if you want to output a 50Hz waveform, the waveform frequency = 20ms.

| Pulse frequency | Waveform frequency |
|:------:|:------:|
| 1Hz | 1000ms |
| 5Hz | 200ms |
| 10Hz | 100ms |
| 50Hz | 20ms |
| 100Hz | 10ms |
| 500Hz | 2ms |
| 1000Hz | 1ms |

In the Coyote V2 protocol, the waveform frequency is determined by [X and Y](/coyote/v2/README_V2.md), where X means X pulses are emitted continuously for X milliseconds, and Y means that after X pulses, X pulses will be emitted again for Y milliseconds and the cycle will continue.

> eg

Parameter [1,9] means that one pulse is sent every 9ms, and the total duration is 10ms, that is, the pulse frequency is 100hz and the waveform frequency is 10ms. Parameter [5,95] means that 5 pulses are sent every 95ms, and the total duration is 100ms. Since these five pulses are connected together and the duration is only 5ms, the user will only feel one (five-in-one) pulse, so the pulse frequency in the user's body is 10hz and the waveform frequency is 100ms.

In the Coyote V3 protocol, we only provide the input of the waveform frequency value, and the distribution of pulses (X) and intervals (Y) in the waveform frequency is determined by the [frequency balance parameter 1](/coyote/v3/README_V3.md) in the V3 protocol.

In the V3 protocol, the input of the waveform frequency needs to undergo a compression conversion. If the user wants the waveform frequency to change linearly, please refer to the following example.

>eg 1 
1. Determine the pulse frequency to be linearly changed, for example: 1Hz, 2Hz, 3Hz, 4Hz, 5Hz, 6Hz, 7Hz, 8Hz, 9Hz, 10Hz 2. Convert to waveform frequency value: 1000ms, 500ms, 333ms, 250ms, 200ms, 166ms, 142ms, 125ms, 111ms, 100ms 3. According to the conversion formula of V3 protocol, convert the waveform frequency into actual input value: 240 
, 180, 146, 130, 120, 113, 108, 105, 102, 100 4. According to the protocol, 4 groups are used, and the missing ones are supplemented by 0, and input to the device every 100ms



>eg 2 
1. Determine the waveform frequency value to be linearly changed, for example: 100ms, 200ms, 300ms, 400ms, 500ms, 600ms, 700ms, 800ms, 900ms, 1000ms 
2. According to the conversion consensus of the V3 protocol, convert the waveform frequency into the actual input value: 100, 120, 140, 160, 180, 200, 210, 220, 230, 240 
3. According to the protocol, 4 groups are added, and the missing ones are supplemented with 0, and input to the device every 100ms

#### Conversion between waveform frequency and actual input value

Since the human body is not sensitive to subtle changes in frequency, the larger the waveform frequency (output unit), the more subtle the pulse frequency change corresponding to the waveform frequency (output unit duration) change. In addition, this conversion can compress the data length, allowing interaction with shorter data.

| Waveform frequency | Output value | Pulse frequency |
|:-----:|:---:|:------:|
| 10ms | 10 | 100Hz |
| 20ms | 20 | 50Hz |
| 50ms | 50 | 20Hz |
| 100ms | 100 | 10Hz |
| 110ms | 102 | 9Hz |
| 150ms | 110 | 6.6Hz |
| 650ms | 204 | 1.53Hz |
| 680ms | 208 | 1.47Hz |
| 750ms | 215 | 1.33Hz |

#### Waveform Intensity

A pulse consists of two symmetrical positive and negative unipolar pulses. The height (voltage) of the two unipolar pulses is determined by the strength of this channel. We control the intensity of the feeling brought by the pulse by controlling the pulse width. The wider the pulse, the stronger the feeling, and vice versa, the narrower the pulse, the weaker the feeling. The rhythmic change of pulse width can create different pulse feelings.

In the Coyote V2 protocol, the waveform strength is determined by [Z](/coyote/v2/README_V2.md), and the value range of the official APP is (0 ~ 20). The waveform strength is a relative value, so there is no actual unit to represent it.

In the Coyote V3 protocol, the value range of waveform intensity is (0 ~ 100). Waveform intensity is a relative value, so there is no actual unit to represent it.

The mapping relationship between the waveform intensity of V2 and the waveform intensity of V3 is: (waveform intensity 20 in V2 protocol) ≈ (waveform intensity 100 in V3 protocol)

### Output Window

The output window of the V2 protocol is 100ms, and the output window of the V3 protocol is 25ms, but the data is set in 4 groups each time, so it can still be considered as 100ms.

Many people are confused about the conflict between the waveform frequency value and the output window value. The waveform frequency duration is greater than the output window, so how will the device handle the data input in the next cycle?

Our device has a relatively complex way of dealing with this situation. We will not describe the details for now, but here are a few suggestions:

1. If you want to output a certain waveform frequency stably, it is recommended to input the waveform frequency value stably.
2. If the waveform frequency value is greater than the output window, and the waveform frequency input in the next cycle changes, then the actual output pulse may not be the effect corresponding to the input value, but the effect after complex processing.

### Convert V2 protocol waveform to V3 protocol waveform

V3 waveform frequency = V2 (X + Y), then perform the conversion from (10 ~ 1000) -> (10 ~ 240)

V3 waveform intensity = V2 (Z * 5)



## 郊狼脉冲波形

本文我们将关于郊狼脉冲主机的波形协议进行部分解释，帮助广大郊狼爱好者更好理解脉冲波形的数据原理。

### 概念解释

#### 波形频率

郊狼的程序把每一秒分割成1000毫秒，在每个毫秒内都可以产生一次脉冲。我们通过控制脉冲和间隔来编码脉冲产生的规律。

波形频率表示一个输出单元的时长(输出单元由X个脉冲和Y个间隔组成)，单位是ms。

所以如果您希望输出一个1Hz的波形，实际上波形频率=1000ms；若输出50Hz的波形，波形频率=20ms。

|  脉冲频率  |  波形频率  |
|:------:|:------:|
|  1Hz   | 1000ms |
|  5Hz   | 200ms  |
|  10Hz  | 100ms  |
|  50Hz  |  20ms  |
| 100Hz  |  10ms  |
| 500Hz  |  2ms   |
| 1000Hz |  1ms   |

在郊狼V2 协议中，波形频率由[X 和 Y](/coyote/v2/README_V2.md)共同决定，其中X代表连续X毫秒发出X个脉冲，Y表示X个脉冲过后会间隔Y毫秒再发出X个脉冲并循环。

> e.g<br/>
参数【1,9】代表每隔9ms发出1个脉冲，总共耗时10ms，也就是脉冲频率为100hz，波形频率为10ms。参数【5,95】代表每隔95ms发出5个脉冲，总共耗时100ms，由于这五个脉冲连在一起并且持续时间仅为5ms，因此使用者只会感受到一次（五合一）脉冲，因此在使用者的体感中脉冲频率为10hz，波形频率为100ms

在郊狼V3 协议中，我们只提供了波形频率值的输入，而波形频率中脉冲(X)和间隔(Y)的分配由V3协议中的 [频率平衡参数1](/coyote/v3/README_V3.md) 来决定。

V3 协议中，波形频率的输入还需经过一次压缩转化，若用户想要波形频率线性变化，请参考以下例子。

>e.g 1<br/>1. 确定要线性变化的脉冲频率，举例：1Hz，2Hz，3Hz，4Hz，5Hz，6Hz，7Hz，8Hz，9Hz，10Hz<br/>2. 转换为波形频率值: 1000ms,500ms,333ms,250ms,200ms,166ms,142ms,125ms,111ms,100ms<br/>3. 根据V3 协议的转化公式，将波形频率转化为实际输入值：240，180，146，130,120,113,108,105,102,100<br/>4. 根据协议4个一组，不足的0补，每100ms向设备输入

>e.g 2<br/>1. 确定要线性变化的波形频率值，举例：100ms，200ms，300ms，400ms，500ms，600ms，700ms，800ms，900ms，1000ms<br/>2. 根据V3 协议的转化共识，将波形频率转化为实际输入值：100，120，140，160，180，200，210，220，230，240<br/>3. 根据协议4个一组，不足的0补，每100ms向设备输入

#### 波形频率与实际输入值的转化

由于人体对于频率的细微变化感知并不敏感，波形频率(输出单元)越大，则波形频率(输出单元时长)变化相对应的脉冲频率变化越细微。另外这个转化可以压缩数据长度，可以以更短的数据进行交互

| 波形频率  | 输出值 |  脉冲频率  |
|:-----:|:---:|:------:|
| 10ms  | 10  | 100Hz  |
| 20ms  | 20  |  50Hz  |
| 50ms  | 50  |  20Hz  |
| 100ms | 100 |  10Hz  |
| 110ms | 102 |  9Hz   |
| 150ms | 110 | 6.6Hz  |
| 650ms | 204 | 1.53Hz |
| 680ms | 208 | 1.47Hz |
| 750ms | 215 | 1.33Hz |

#### 波形强度

一次脉冲由两个对称的正负单极性脉冲组成，两个单极性脉冲的高度(电压)由这个通道的强度决定。我们通过控制脉冲宽度的方式控制脉冲带来的感受的强弱。脉冲越宽，感受就越强，反之脉冲越窄感受约越弱。脉冲宽度的节奏性变化可以创造出不同的脉冲感受。

在郊狼V2 协议中，波形强度由[Z](/coyote/v2/README_V2.md)决定,官方APP的值范围是(0 ~ 20)，波形强度是一个相对值，所以并没有实际的单位来表示

在郊狼V3 协议中，波形强度的值范围是(0 ~ 100)，波形强度是一个相对值，所以并没有实际的单位来表示

V2的波形强度与V3的波形强度的映射关系: (V2 协议中 波形强度 20) ≈ (V3 协议中 波形强度 100)

### 输出窗口

V2 协议的输出窗口为100ms，V3 协议的输出窗口为25ms，但每次设置的数据为4组，所以依然可以认为是100ms。

很多人对于波形频率值和输出窗口值的冲突表示困惑，波形频率时长是大于输出窗口的，那么对于下一个周期输入的数据设备将如何处理？

我们的设备内部对于这一情况有一套相对复杂的处理方式，处理细节暂不描述，但给出几个建议：

1. 若希望稳定输出某个波形频率，建议稳定输入该波形频率值
2. 若波形频率值大于输出窗口，下一周期输入的波形频率有所变化，那么真正的输出脉冲可能并非输入值所对应的效果，而是经过复杂方式处理后的效果

### V2协议波形 转化为 V3协议波形

V3波形频率 = V2 (X + Y) 后，执行(10 ~ 1000) -> (10 ~ 240)的转化

V3波形强度 = V2 (Z * 5)
