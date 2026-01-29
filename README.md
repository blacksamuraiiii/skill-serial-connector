# skill-serial-connector

[![Version](https://img.shields.io/badge/version-v0.1-blue.svg)](https://github.com/blacksamuraiiii/skill-serial-connector)
[![Platform](https://img.shields.io/badge/platform-win10--x64-orange.svg)](https://github.com/blacksamuraiiii/skill-serial-connector)

`skill-serial-connector` 是一个专为 Windows 环境设计的交换机串口自动化工具。它不仅是一个独立的 Python 库，更是一个完全符合 **Claude Code Agent SKILL** 规范的智能插件。通过集成 `plink.exe`，它能够让 AI 助手直接接管串口，实现对中兴、华为、思科等主流厂商设备的协议扫描、配置下发及故障排查。

---

## 🤖 AI Agent 兼容性

本项目严格遵循 **Agent Skills 开源标准**，可无缝集成至 Claude Code、Cursor 等主流 AI 编程助手：

- **自动化指令转换**：AI 助手可阅读 `references/` 下的厂商手册，自动将自然语言（如“把 gei-2/1 换到 VLAN 10”）转换为对应厂商的 CLI 命令。
- **自描述调用界面**：通过 `SKILL.md` 定义的任务协议，AI 助手能自主决定何时调用 `serial_connector.py` 进行物理交互。
- **状态感知执行**：AI 能通过读取 `.log` 文件实时感知设备反馈，并根据错误提示（如 `Error 140303`）自动修正命令逻辑。
- **无感断点续传**：当 AI 任务因 Token 限制或网络波动中断时，新的 Agent 实例能通过日志自动定位进度，实现无缝接力。

---

## ✨ 核心功能

- **🚀 自动化任务管理**：通过 API 快速生成任务文件（`.txt`）并执行。
- **⏱️ 统一命名规范**：任务文件与日志文件共享相同的时间戳（`{厂家}_{时间戳}`），便于回溯。
- **🔄 断点续传机制**：自动分析已执行日志，支持在异常中断后从最后一条成功命令继续执行。
- **🛡️ Windows 深度优化**：
  - 针对 Windows 处理串口输入流的特性，修复了 `OSError [Errno 22] Invalid argument` 错误。
  - 使用 `\n` 替代 `\r` 提高不同厂商设备的兼容性。
- **🧹 目录分离架构**：SKILL 核心文件与运行生成的临时文件完全分离，保持项目目录纯净。
- **📚 多厂商预设**：内置中兴 (ZTE)、华为 (HW)、H3C、锐捷 (Ruijie)、思科 (Cisco) 的常用指令参考。

---

## 💻 系统要求

- **操作系统**：Windows 10 / 11 x64
- **运行环境**：Python 3.8+
- **依赖工具**：`assets/plink.exe` (已内置)

---

## 🛠️ 调用流程

```mermaid
graph LR
    A[用户提出自然语言需求] --> B[AI 加载 SKILL]
    B --> C[AI 结合厂商文档生成 CLI 命令]
    C --> D[AI 调用脚本执行任务]
    D --> E[生成实时日志并返回结果]
```

---

## 🚀 快速开始

### 1. 安装与自动加载 SKILL（推荐方式）

首先，克隆本项目到本地：

```bash
git clone https://github.com/blacksamuraiiii/skill-serial-connector
```

然后，直接在 AI 助手（如 Cursor、Claude Code）的对话框中输入以下指令即可：

> **“加载项目级 SKILL，地址：./skill-serial-connector”**

加载成功后，你只需描述你的需求，AI 将自动接管一切：

> **用户问**：
> “帮我配置这台中兴交换机，COM6口，密码是admin。需要把 gei-2/2 端口加入 VLAN 20。”
>
> **AI 动作**：
>
> 1. 读取 `references/zte-commands.md` 确认语法。
> 2. 自动生成包含 `enable`、`config t` 等模式切换的完整命令序列。
> 3. 调用 `serial_connector.py` 自动执行，并实时通过日志感知执行进度。

### 2. 任务文件格式

你也可以手动创建任务文件执行：

```ini
[METADATA]
vendor=ZTE
com_port=COM6
baud_rate=115200
password=admin
log_file=ZTE_20260129_193000.log

[COMMANDS]
show version
show interface brief

[END]
```

---

## 📁 文件结构

```text
skill-serial-connector/
├── SKILL.md                    # 详细技术规格文档
├── task_template.txt           # 任务文件标准模板
├── scripts/
│   └── serial_connector.py     # 核心 Python 逻辑 (v0.1)
├── assets/
│   └── plink.exe              # 串口通信核心组件
├── references/                 # 厂商指令参考手册
│   ├── zte-commands.md
│   ├── hw-commands.md
│   ├── h3c-commands.md
│   ├── ruijie-commands.md
│   └── cisco-commands.md
└── (生成的临时文件)             # 运行后出现在工作目录，不影响以上结构
    ├── ZTE_20260129_190900.txt
    └── ZTE_20260129_190900.log
```

---

## ❌ 错误说明与排查

| 错误特征                        | 可能原因               | 解决方法                                                                 |
| :------------------------------ | :--------------------- | :----------------------------------------------------------------------- |
| **Error 140303**          | 模式错误或语法错误     | 确认是否已执行 `enable` 进入特权模式或 `config t` 进入配置模式。     |
| **Error 140251**          | 密码输入超时           | 检查密码是否正确，或增加 `wait_time` 延迟。                            |
| **OSError [Errno 22]**    | Windows 进程管道异常   | `v0.1已修复`。确保使用最新脚本，会自动检查进程状态并使用 `\n` 换行。 |
| **Timeout / No Response** | 串口占用或参数配置错误 | 检查 COM 口号是否被其他软件（如 Putty）占用；确认波特率（默认 115200）。 |

---

## ⚠️ 开发注意事项

1. **命令顺序**：交换机通常有严格的模式层级（用户模式 -> 特权模式 -> 全局配置模式）。在 `commands` 列表中必须包含 `enable` 或 `configure terminal` 等切换指令。
2. **连接占用**：本工具运行期间会独占串口，请关闭第三方串口调试助手。
3. **安全提示**：请勿在 `password` 字段中硬编码敏感生产密码，建议使用环境变量或输入提示。

---

## 🧪 测试说明与社区贡献

⚠️ **当前状态**：由于作者手头硬件限制，目前本项目**仅在中兴 (ZTE) 交换机下进行了部分功能测试并确认成功**。华为、思科、锐捷等厂商的逻辑基于手册编写，尚未经过真机验证。

🤝 **欢迎贡献**：

- 如果你在其他厂商设备上测试成功或发现问题，欢迎提交 **Issue** 或直接 **Fork** 本项目进行修改并提交 **Pull Request**。
- 你的每一行代码贡献都能帮助更多工程师解决串口自动化的烦恼！

---

*Last Updated: 2026-01-29*
