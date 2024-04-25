## 郊狼情趣脉冲主机V3

### 蓝牙特性

| 服务UUID | 特性UUID |  属性 |   名称   | 大小(BYTE) |       说明       |
| :----: | :----: | :-: | :----: | :------: | :------------: |
| 0x180C | 0x150A |  写  |  WRITE |  最长20字节  |  所有的指令都在该特性输入  |
| 0x180C | 0x150B |  通知 | NOTIFY |  最长20字节  | 所有的回应消息都在该特性返回 |

> 基础UUID：0000`xxxx`-0000-1000-8000-00805f9b34fb(将xxxx替换为服务/特性UUID)

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