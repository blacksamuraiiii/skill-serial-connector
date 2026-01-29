---
name: skill-serial-connector
description: 通过Windows串口（COM口）控制多品牌交换机；支持ZTE/华为/H3C/锐捷/思科设备；自然语言指令转换为CLI命令
dependency: {}
---

# Switch Controller

## 任务目标

通过 Windows 串口（COM口）配置和管理多品牌交换机。

**核心能力**：
- 支持多厂商设备：中兴（ZTE）、华为、华三（H3C）、锐捷、思科（Cisco）
- 自然语言理解并转换为对应厂商的 CLI 命令
- 通过串口逐条执行命令，等待设备响应
- 支持断点续传，任务中断后可继续执行

**触发条件**：
- 用户描述交换机配置需求（如"配置VLAN"、"配置链路聚合"）
- 需要通过 COM 口执行交换机命令

## 前置准备

### 设备连接信息（必需）

1. **交换机厂商**：中兴、华为、H3C、锐捷、思科
2. **串口端口**：COM 端口号，如 COM6
3. **波特率**：根据厂商确定（中兴常用 115200，其他常用 9600）
4. **enable密码**（如需要）：如 zxr10、admin、cisco

### Windows 环境要求

- 操作系统：Windows 7/8/10/11
- 串口驱动：确保 COM 端口驱动已正确安装
- COM 口状态：确保未被其他程序占用（如 SecureCRT、PuTTY）

## 操作步骤

### 步骤 1：收集设备信息

向用户确认：
- 交换机厂商
- COM 端口号
- 波特率
- enable/特权密码（如需要）
- 用户指令描述（自然语言或具体命令列表）

### 步骤 2：选择厂商参考文档

根据用户指定的厂商，选择对应的参考文档：

| 厂商 | 参考文档 | 进入配置模式 | 接口命名示例 | 查看命令 |
|------|---------|-------------|-------------|---------|
| 中兴（ZTE） | `references/zte-commands.md` | `configure terminal` | `gei-2/1` | `show` |
| 华为 | `references/hw-commands.md` | `system-view` | `GigabitEthernet 0/0/1` | `display` |
| 华三（H3C） | `references/h3c-commands.md` | `system-view` | `GigabitEthernet1/0/1` | `display` |
| 锐捷 | `references/ruijie-commands.md` | `configure terminal` | `GigabitEthernet 0/1` | `show` |
| 思科（Cisco） | `references/cisco-commands.md` | `configure terminal` | `GigabitEthernet 0/1` | `show` |

### 步骤 3：理解用户需求

分析用户的自然语言描述，提取：
- 配置类型（VLAN/路由/LACP/状态查询等）
- 具体参数（VLAN ID、接口名称、IP 地址等）
- 操作范围（单个端口、多个端口、全局配置）

### 步骤 4：参考厂商命令文档

根据选择的厂商，在对应的参考文档中查找：
- 正确的命令语法
- 命令执行顺序（先进入配置模式，再执行具体配置）
- 模式切换方式
- 接口命名格式

### 步骤 5：生成任务文件

使用 `create_task_file()` 自动生成任务文件（统一命名：`{厂家}_{时间戳}.txt`）：

```python
from scripts.serial_connector import create_task_file

task_file, log_file = create_task_file(
    vendor="ZTE",
    com_port="COM6",
    baud_rate=115200,
    password="MSR_adm10",
    commands=[
        "enable",                    # 进入特权模式
        "configure terminal",        # 进入配置模式
        "interface gei-2/1",         # 配置接口
        "switchport",               # 切换到二层模式
        "switchport mode access",    # 设置为access模式
        "switchport access vlan 10", # 加入VLAN 10
        "exit"                       # 退出配置
    ],
    output_dir="."  # 输出到当前工作目录（保持SKILL文件夹纯净）
)
```

**命令序列原则**：
1. 从用户模式开始，按顺序进入各个配置模式
2. 执行具体配置命令
3. 添加验证命令（如 show/display）
4. 每条命令一行，不要合并
5. 确保符合厂商语法

### 步骤 6：执行任务

```python
from scripts.serial_connector import execute_task_file

# 执行任务（首次执行）
result = execute_task_file(
    task_file=task_file,
    resume=False,
    output_dir="."
)

# 如果中断，继续执行（断点续传）
result = execute_task_file(
    task_file=task_file,
    resume=True,  # 从上次中断位置继续
    output_dir="."
)
```

**执行机制**：
- 逐条发送命令，每条命令间隔 2.0 秒
- 等待设备响应后再发送下一条
- 实时记录日志到 `{厂家}_{时间戳}.log` 文件
- 临时文件输出到工作目录，保持 SKILL 文件夹纯净

### 步骤 7：分析结果

```python
print(result['status'])         # success/error/completed
print(result['log_file'])       # 日志文件路径
print(result['total_commands']) # 总命令数
```

查看日志文件了解详细执行情况，识别错误信息。

### 步骤 8：生成反馈

向用户提供：
- 配置成功/失败的明确反馈
- 执行的命令摘要
- 如果失败，提供故障排查建议
- 日志文件路径

## 资源索引

### 核心脚本

**`scripts/serial_connector.py`** - 串口连接与命令执行

主要函数：
1. **`create_task_file(vendor, com_port, baud_rate, password, commands, output_dir)`**
   - 自动生成任务文件（统一命名：`{厂家}_{时间戳}.txt`）
   - 返回任务文件路径和日志文件路径

2. **`execute_task_file(task_file, resume=False, output_dir=".")`**
   - 执行任务文件
   - 支持断点续传（`resume=True`）

### 厂商参考文档

根据厂商选择对应的参考文档（按需读取）：
- `references/zte-commands.md` - 中兴交换机命令参考
- `references/hw-commands.md` - 华为交换机命令参考
- `references/h3c-commands.md` - 华三交换机命令参考
- `references/ruijie-commands.md` - 锐捷交换机命令参考
- `references/cisco-commands.md` - 思科交换机命令参考

### 输出资产

**`assets/plink.exe`** - 串口通信工具

Windows 可执行文件，由 `serial_connector.py` 自动调用。

## 注意事项

### 厂商差异化

- ⚠️ 不同厂商的命令语法差异较大，必须严格参考对应厂商文档
- ⚠️ 注意模式切换方式：华为/H3C 使用 `system-view`，中兴/锐捷/思科使用 `configure terminal`
- ⚠️ 注意查看命令：华为/H3C 使用 `display`，中兴/锐捷/思科使用 `show`

### 连接相关

- ✅ 确保 COM 端口驱动已正确安装
- ✅ 确保 COM 端口未被其他程序占用
- ✅ 如果连接失败，检查串口线连接和波特率设置

### 命令执行

- ✅ 命令序列必须遵循对应厂商的正确执行顺序
- ✅ **逐条发送命令，每条命令间隔 2.0 秒**，等待设备响应
- ✅ 不要批量发送，不要连续发送，避免触发设备保护

### 文件管理

- ✅ 任务文件和日志文件使用统一命名：`{厂家}_{时间戳}.txt/log`
- ✅ 临时文件输出到工作目录（使用 `output_dir` 参数）
- ✅ SKILL 文件夹保持纯净，仅包含核心资源

### 断点续传

- ✅ 使用 `resume=True` 从上次中断位置继续
- ✅ 避免产生多个重复的日志文件
- ✅ 任务文件和日志使用相同时间戳，便于对应

### 故障排查

- ✅ 所有操作自动记录到日志文件
- ✅ 日志包含时间戳、发送命令、接收响应
- ✅ 如果配置失败，查看日志中的错误信息
- ✅ 常见错误：
  - **Error 140303**：命令语法错误或模式错误（确保先 `enable` 再 `configure terminal`）
  - **OSError**：已在 v0.1 修复
  - 连接超时：检查 COM 口和串口线连接

### 安全注意

- ⚠️ 配置前建议先备份当前配置
- ⚠️ 关键配置修改前，建议先在测试环境验证
- ⚠️ 避免在生产环境执行未经验证的命令序列
