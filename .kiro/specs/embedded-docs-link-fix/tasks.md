# 实施计划：嵌入式文档链接修复与内容创建

## 概述

本实施计划专注于两项核心工作：修复现有文档中的错误链接，以及创建14篇高质量技术文档（每篇1500行以上）。每个文档创建任务都包含更新对应目录的index.md文件。

## 任务列表

- [x] 1. 修复现有文档中的错误链接
  - 修正嵌入式文档中所有错误的内部链接
  - _需求: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8_

- [x] 1.1 修复 01-pwm-advanced.md 中的链接
  - 文件: `knowledge/02-technologies/embedded/01-hardware-layer/05-actuator-control/intermediate/01-pwm-advanced.md`
  - 更新链接: `../../03-power-management/intermediate/02-switching-power-supply.md` → `../../../03-power-management/intermediate/04-switching-power-supply.md`
  - _需求: 1.2, 1.3_

- [x] 1.2 修复 02-bldc-motor-control.md 中的链接
  - 文件: `knowledge/02-technologies/embedded/01-hardware-layer/05-actuator-control/intermediate/02-bldc-motor-control.md`
  - 更新链接: `../../02-driver-bsp-layer/04-interrupt-exception-handling/intermediate/02-encoder-interface.md` → `../../../../02-driver-bsp-layer/04-interrupt-exception-handling/intermediate/04-encoder-interface.md`
  - 更新链接: `../../03-operating-system-layer/02-analog-signal-processing/intermediate/01-current-sensing.md` → `../../../04-sensor-technology/intermediate/01-current-sensing.md`
  - _需求: 1.2, 1.3_

- [x] 1.3 修复 01-uart-hardware.md 中的链接
  - 文件: `knowledge/02-technologies/embedded/01-hardware-layer/06-communication-interface-hardware/beginner/01-uart-hardware.md`
  - 更新链接: `../../04-middleware-layer/03-communication-protocols/intermediate/01-modbus-protocol.md` → `../../../../06-communication-networking/02-network-protocols/intermediate/02-modbus-protocol.md`
  - 更新链接: `../../04-middleware-layer/03-communication-protocols/beginner/02-at-commands.md` → `../../../../06-communication-networking/02-network-protocols/beginner/02-at-commands.md`
  - _需求: 1.2, 1.3_

- [x] 1.4 修复 02-spi-hardware.md 中的链接
  - 文件: `knowledge/02-technologies/embedded/01-hardware-layer/06-communication-interface-hardware/beginner/02-spi-hardware.md`
  - 更新链接: `../../04-middleware-layer/02-storage-management/beginner/01-flash-storage.md` → `../../../../04-middleware-layer/02-storage-technology/beginner/01-flash-technology.md`
  - 更新链接: `../../04-middleware-layer/02-storage-management/intermediate/01-sd-card-filesystem.md` → `../../../../04-middleware-layer/02-storage-technology/intermediate/03-sd-card-filesystem.md`
  - 更新链接: `../../05-application-layer/02-user-interface/intermediate/01-tft-display.md` → `../../../../04-middleware-layer/03-graphics-display/intermediate/01-tft-display.md`
  - _需求: 1.2, 1.3_

- [x] 1.5 修复 03-i2c-hardware.md 中的链接
  - 文件: `knowledge/02-technologies/embedded/01-hardware-layer/06-communication-interface-hardware/beginner/03-i2c-hardware.md`
  - 更新链接: `../../04-middleware-layer/02-storage-management/beginner/02-eeprom-storage.md` → `../../../../04-middleware-layer/02-storage-technology/beginner/02-eeprom-storage.md`
  - 更新链接: `../../04-middleware-layer/03-communication-protocols/beginner/03-rtc-application.md` → `../../../../06-communication-networking/02-network-protocols/beginner/03-rtc-application.md`
  - 更新链接: `../../05-application-layer/01-data-acquisition/beginner/01-sensor-reading.md` → `../../../04-sensor-technology/beginner/01-sensor-reading.md`
  - _需求: 1.2, 1.3_

- [x] 1.6 修复 01-can-bus-hardware.md 中的链接
  - 文件: `knowledge/02-technologies/embedded/01-hardware-layer/06-communication-interface-hardware/intermediate/01-can-bus-hardware.md`
  - 更新链接: `../../04-middleware-layer/03-communication-protocols/intermediate/02-canopen-protocol.md` → `../intermediate/06-canopen-protocol.md`
  - 更新链接: `../../04-middleware-layer/03-communication-protocols/advanced/01-j1939-protocol.md` → `../../../../06-communication-networking/02-network-protocols/advanced/01-j1939-protocol.md`
  - _需求: 1.2, 1.3_

- [x] 1.7 修复 03-ethernet-hardware.md 中的链接
  - 文件: `knowledge/02-technologies/embedded/01-hardware-layer/06-communication-interface-hardware/intermediate/03-ethernet-hardware.md`
  - 更新链接: `../../04-middleware-layer/03-communication-protocols/intermediate/01-lwip-stack.md` → `../../../../06-communication-networking/02-network-protocols/intermediate/04-lwip-stack.md`
  - 更新链接: `../../04-middleware-layer/03-communication-protocols/intermediate/03-modbus-tcp.md` → `../../../../06-communication-networking/02-network-protocols/intermediate/05-modbus-tcp.md`
  - _需求: 1.2, 1.3_

- [x] 2. 创建高优先级文档（网络协议）
  - 创建关键的网络协议文档
  - _需求: 3.1-3.10, 11.1-11.6_

- [x] 2.1 创建《lwIP协议栈移植》文档
  - 文件: `knowledge/02-technologies/embedded/06-communication-networking/02-network-protocols/intermediate/04-lwip-stack.md`
  - 内容: lwIP架构、移植指南、配置、集成示例
  - 包含: TCP/IP协议栈概述、内存管理、线程模型、驱动集成
  - 代码示例: 初始化、套接字编程、回调处理
  - 最少1500行，内容全面深入
  - 完整的frontmatter元数据
  - _需求: 3.1-3.10, 11.1-11.6_

- [x] 2.2 更新 network-protocols/intermediate 的 index.md
  - 文件: `knowledge/02-technologies/embedded/06-communication-networking/02-network-protocols/intermediate/index.md`
  - 添加 04-lwip-stack.md 的条目，包含标题和描述
  - 保持与现有条目一致的格式
  - _需求: 4.1, 4.2_

- [x] 2.3 创建《Modbus TCP实现》文档
  - 文件: `knowledge/02-technologies/embedded/06-communication-networking/02-network-protocols/intermediate/05-modbus-tcp.md`
  - 内容: Modbus TCP协议、实现指南、客户端/服务器示例
  - 包含: 协议规范、帧格式、功能码、错误处理
  - 代码示例: 客户端实现、服务器实现、数据解析
  - 最少1500行，内容全面深入
  - 完整的frontmatter元数据
  - _需求: 3.1-3.10, 11.1-11.6_

- [x] 2.4 更新 network-protocols/intermediate 的 index.md
  - 文件: `knowledge/02-technologies/embedded/06-communication-networking/02-network-protocols/intermediate/index.md`
  - 添加 05-modbus-tcp.md 的条目，包含标题和描述
  - 保持与现有条目一致的格式
  - _需求: 4.1, 4.2_

- [x] 3. 创建高优先级文档（硬件与存储）
  - 创建关键的硬件和存储文档
  - _需求: 3.1-3.10, 11.1-11.6_

- [x] 3.1 创建《开关电源设计》文档
  - 文件: `knowledge/02-technologies/embedded/01-hardware-layer/03-power-management/intermediate/04-switching-power-supply.md`
  - 内容: 开关电源原理、拓扑结构、设计方法
  - 包含: Buck/Boost/Buck-Boost转换器、PWM控制、元件选型
  - 代码示例: PWM生成、反馈控制、保护电路
  - 图表: 电路原理图、波形图、控制环路
  - 最少1500行，内容全面深入
  - 完整的frontmatter元数据
  - _需求: 3.1-3.10, 11.1-11.6_

- [x] 3.2 更新 power-management/intermediate 的 index.md
  - 文件: `knowledge/02-technologies/embedded/01-hardware-layer/03-power-management/intermediate/index.md`
  - 添加 04-switching-power-supply.md 的条目，包含标题和描述
  - 保持与现有条目一致的格式
  - _需求: 4.1, 4.2_

- [x] 3.3 创建《SD卡文件系统》文档
  - 文件: `knowledge/02-technologies/embedded/04-middleware-layer/02-storage-technology/intermediate/03-sd-card-filesystem.md`
  - 内容: SD卡接口、FAT文件系统、FatFs库使用
  - 包含: SPI/SDIO接口、文件系统操作、性能优化
  - 代码示例: 初始化、文件操作、目录管理
  - 最少1500行，内容全面深入
  - 完整的frontmatter元数据
  - _需求: 3.1-3.10, 11.1-11.6_

- [x] 3.4 更新 storage-technology/intermediate 的 index.md
  - 文件: `knowledge/02-technologies/embedded/04-middleware-layer/02-storage-technology/intermediate/index.md`
  - 添加 03-sd-card-filesystem.md 的条目，包含标题和描述
  - 保持与现有条目一致的格式
  - _需求: 4.1, 4.2_

- [x] 4. 创建中优先级文档（基础协议）
  - 创建入门级协议文档
  - _需求: 3.1-3.10, 11.1-11.6_

- [x] 4.1 创建《AT命令集应用》文档
  - 文件: `knowledge/02-technologies/embedded/06-communication-networking/02-network-protocols/beginner/02-at-commands.md`
  - 内容: AT命令基础、常用命令、调制解调器控制
  - 包含: 命令语法、响应解析、错误处理
  - 代码示例: UART通信、命令发送、响应解析
  - 最少1500行，内容全面深入
  - 完整的frontmatter元数据
  - _需求: 3.1-3.10, 11.1-11.6_

- [x] 4.2 更新 network-protocols/beginner 的 index.md
  - 文件: `knowledge/02-technologies/embedded/06-communication-networking/02-network-protocols/beginner/index.md`
  - 添加 02-at-commands.md 的条目，包含标题和描述
  - 保持与现有条目一致的格式
  - _需求: 4.1, 4.2_

- [x] 4.3 创建《RTC实时时钟应用》文档
  - 文件: `knowledge/02-technologies/embedded/06-communication-networking/02-network-protocols/beginner/03-rtc-application.md`
  - 内容: RTC原理、I2C/SPI RTC芯片、时间管理
  - 包含: 时钟配置、闹钟功能、电池备份
  - 代码示例: RTC初始化、时间读写、闹钟设置
  - 最少1500行，内容全面深入
  - 完整的frontmatter元数据
  - _需求: 3.1-3.10, 11.1-11.6_

- [x] 4.4 更新 network-protocols/beginner 的 index.md
  - 文件: `knowledge/02-technologies/embedded/06-communication-networking/02-network-protocols/beginner/index.md`
  - 添加 03-rtc-application.md 的条目，包含标题和描述
  - 保持与现有条目一致的格式
  - _需求: 4.1, 4.2_

- [x] 5. 创建中优先级文档（高级协议）
  - 创建高级协议文档
  - _需求: 3.1-3.10, 11.1-11.6_

- [x] 5.1 创建《CANopen协议实现》文档
  - 文件: `knowledge/02-technologies/embedded/01-hardware-layer/06-communication-interface-hardware/intermediate/06-canopen-protocol.md`
  - 内容: CANopen协议栈、对象字典、通信配置
  - 包含: SDO/PDO通信、网络管理、设备配置
  - 代码示例: 节点初始化、SDO传输、PDO映射
  - 最少1500行，内容全面深入
  - 完整的frontmatter元数据
  - _需求: 3.1-3.10, 11.1-11.6_

- [x] 5.2 更新 communication-interface-hardware/intermediate 的 index.md
  - 文件: `knowledge/02-technologies/embedded/01-hardware-layer/06-communication-interface-hardware/intermediate/index.md`
  - 添加 06-canopen-protocol.md 的条目，包含标题和描述
  - 保持与现有条目一致的格式
  - _需求: 4.1, 4.2_

- [x] 5.3 创建《J1939协议应用》文档
  - 文件: `knowledge/02-technologies/embedded/06-communication-networking/02-network-protocols/advanced/01-j1939-protocol.md`
  - 内容: J1939车载网络协议、PGN、SPN、消息格式
  - 包含: 传输协议、地址声明、诊断消息
  - 代码示例: 消息编解码、地址管理、诊断功能
  - 最少1500行，内容全面深入
  - 完整的frontmatter元数据
  - _需求: 3.1-3.10, 11.1-11.6_

- [x] 5.4 更新 network-protocols/advanced 的 index.md
  - 文件: `knowledge/02-technologies/embedded/06-communication-networking/02-network-protocols/advanced/index.md`
  - 添加 01-j1939-protocol.md 的条目，包含标题和描述
  - 保持与现有条目一致的格式
  - _需求: 4.1, 4.2_

- [x] 6. 创建中优先级文档（硬件传感与显示）
  - 创建硬件相关文档
  - _需求: 3.1-3.10, 11.1-11.6_

- [x] 6.1 创建《电流采样与保护》文档
  - 文件: `knowledge/02-technologies/embedded/01-hardware-layer/04-sensor-technology/intermediate/01-current-sensing.md`
  - 内容: 电流检测方法、分流电阻、霍尔传感器
  - 包含: ADC采样、过流保护、校准方法
  - 代码示例: ADC配置、电流计算、保护逻辑
  - 图表: 检测电路、保护方案
  - 最少1500行，内容全面深入
  - 完整的frontmatter元数据
  - _需求: 3.1-3.10, 11.1-11.6_

- [x] 6.2 更新 sensor-technology/intermediate 的 index.md
  - 文件: `knowledge/02-technologies/embedded/01-hardware-layer/04-sensor-technology/intermediate/index.md`
  - 添加 01-current-sensing.md 的条目，包含标题和描述
  - 保持与现有条目一致的格式
  - _需求: 4.1, 4.2_

- [x] 6.3 创建《TFT显示屏驱动》文档
  - 文件: `knowledge/02-technologies/embedded/04-middleware-layer/03-graphics-display/intermediate/01-tft-display.md`
  - 内容: TFT LCD原理、显示控制器（ILI9341、ST7789）、驱动开发
  - 包含: SPI/并行接口、图形基元、帧缓冲管理
  - 代码示例: 初始化、像素绘制、图形库集成
  - 最少1500行，内容全面深入
  - 完整的frontmatter元数据
  - _需求: 3.1-3.10, 11.1-11.6_

- [x] 6.4 更新 graphics-display/intermediate 的 index.md
  - 文件: `knowledge/02-technologies/embedded/04-middleware-layer/03-graphics-display/intermediate/index.md`
  - 添加 01-tft-display.md 的条目，包含标题和描述
  - 保持与现有条目一致的格式
  - _需求: 4.1, 4.2_

- [x] 7. 创建低优先级文档（I2C协议）
  - 完成I2C相关协议文档
  - _需求: 3.1-3.10, 11.1-11.6_

- [x] 7.1 创建《I2C多路复用器应用》文档
  - 文件: `knowledge/02-technologies/embedded/01-hardware-layer/06-communication-interface-hardware/intermediate/04-i2c-multiplexer.md`
  - 内容: I2C多路复用器芯片（TCA9548A）、地址冲突、总线管理
  - 包含: 通道选择、设备枚举、错误处理
  - 代码示例: 多路复用器控制、设备扫描、多总线管理
  - 最少1500行，内容全面深入
  - 完整的frontmatter元数据
  - _需求: 3.1-3.10, 11.1-11.6_

- [x] 7.2 更新 communication-interface-hardware/intermediate 的 index.md
  - 文件: `knowledge/02-technologies/embedded/01-hardware-layer/06-communication-interface-hardware/intermediate/index.md`
  - 添加 04-i2c-multiplexer.md 的条目，包含标题和描述
  - 保持与现有条目一致的格式
  - _需求: 4.1, 4.2_

- [x] 7.3 创建《SMBus协议详解》文档
  - 文件: `knowledge/02-technologies/embedded/01-hardware-layer/06-communication-interface-hardware/intermediate/05-smbus-protocol.md`
  - 内容: SMBus协议规范、与I2C的区别、包错误检查
  - 包含: 命令协议、PEC计算、超时处理
  - 代码示例: SMBus事务、PEC实现、错误恢复
  - 最少1500行，内容全面深入
  - 完整的frontmatter元数据
  - _需求: 3.1-3.10, 11.1-11.6_

- [x] 7.4 更新 communication-interface-hardware/intermediate 的 index.md
  - 文件: `knowledge/02-technologies/embedded/01-hardware-layer/06-communication-interface-hardware/intermediate/index.md`
  - 添加 05-smbus-protocol.md 的条目，包含标题和描述
  - 保持与现有条目一致的格式
  - _需求: 4.1, 4.2_

- [x] 8. 创建低优先级文档（电源与传感器基础）
  - 完成剩余文档
  - _需求: 3.1-3.10, 11.1-11.6_

- [x] 8.1 创建《PMBus电源管理》文档
  - 文件: `knowledge/02-technologies/embedded/01-hardware-layer/06-communication-interface-hardware/advanced/01-pmbus-power-management.md`
  - 内容: PMBus电源管理协议、命令集、遥测功能
  - 包含: 电源控制、监控、故障管理
  - 代码示例: PMBus通信、遥测读取、配置管理
  - 最少1500行，内容全面深入
  - 完整的frontmatter元数据
  - _需求: 3.1-3.10, 11.1-11.6_

- [x] 8.2 更新 communication-interface-hardware/advanced 的 index.md
  - 文件: `knowledge/02-technologies/embedded/01-hardware-layer/06-communication-interface-hardware/advanced/index.md`
  - 添加 01-pmbus-power-management.md 的条目，包含标题和描述
  - 保持与现有条目一致的格式
  - _需求: 4.1, 4.2_

- [x] 8.3 创建《传感器数据采集基础》文档
  - 文件: `knowledge/02-technologies/embedded/01-hardware-layer/04-sensor-technology/beginner/01-sensor-reading.md`
  - 内容: 传感器基础、模拟/数字传感器、数据采集原理
  - 包含: ADC使用、传感器校准、数据滤波
  - 代码示例: ADC读取、移动平均滤波、传感器接口
  - 最少1500行，内容全面深入
  - 完整的frontmatter元数据
  - _需求: 3.1-3.10, 11.1-11.6_

- [x] 8.4 更新 sensor-technology/beginner 的 index.md
  - 文件: `knowledge/02-technologies/embedded/01-hardware-layer/04-sensor-technology/beginner/index.md`
  - 添加 01-sensor-reading.md 的条目，包含标题和描述
  - 保持与现有条目一致的格式
  - _需求: 4.1, 4.2_

## 说明

### 文档创建要求
- 所有文档必须至少1500行高质量内容
- 每篇文档必须包含全面的技术细节、代码示例和图表
- 所有文档必须使用中文，并使用正确的技术术语
- 每篇文档必须包含完整的frontmatter元数据字段：
  - title（标题）、description（描述）、category（分类）、difficulty（难度）、tags（标签）、prerequisites（前置知识）、related_contents（相关内容）

### index.md 更新要求
- 创建每篇文档后，必须更新对应目录的index.md文件
- 添加包含文档编号、标题和简要描述的条目
- 保持与现有条目一致的格式
- 确保新条目按正确的数字顺序排列

### 链接修复要求
- 更新所有错误链接，使用正确的相对路径
- 验证目标文件在新路径下存在
- 保留原始链接文本，只更新URL部分
- 保持正确的markdown格式

### 执行顺序
- 首先完成所有链接修复（任务1）
- 按优先级顺序创建文档（任务2-8）
- 创建每篇文档后立即更新index.md
- 这样可以确保链接指向已存在的文件，导航始终保持最新
