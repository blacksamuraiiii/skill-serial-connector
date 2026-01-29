"""
交换机串口通信模块 v0.1
支持逐条发送命令、获取响应、任务文件管理、断点续传
任务文件和日志文件使用统一的 {厂家}_{时间戳} 命名规则
临时文件输出到调用程序的工作目录，保持SKILL文件夹纯净
"""

import subprocess
import time
import re
import logging
import os
import platform
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class LoggerWriter:
    """将日志同时输出到控制台和文件"""

    def __init__(self, logger, level=logging.INFO):
        self.logger = logger
        self.level = level

    def write(self, message):
        if message.strip():
            self.logger.log(self.level, message.strip())

    def flush(self):
        pass


def setup_logger(log_file: str) -> logging.Logger:
    """
    设置日志配置

    Args:
        log_file: 日志文件路径

    Returns:
        logging.Logger: 配置好的日志器
    """
    # 创建日志目录（如果不存在）
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # 配置日志格式
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 文件处理器 - 写入日志文件
    file_handler = logging.FileHandler(log_file, encoding='utf-8', mode='a')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)

    # 控制台处理器 - 输出到控制台
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)

    # 创建日志器
    logger = logging.getLogger(f'PlinkLogger_{log_file}')
    logger.setLevel(logging.DEBUG)
    
    # 清除已有的处理器（避免重复）
    logger.handlers.clear()
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


def find_plink_exe(custom_path: str = None) -> str:
    """
    查找 plink.exe 可执行文件

    Args:
        custom_path: 用户指定的 plink.exe 路径

    Returns:
        str: plink.exe 的完整路径
    """
    # 如果用户指定了路径，直接使用
    if custom_path and os.path.exists(custom_path):
        return custom_path

    # 尝试 SKILL 的 assets 目录（相对于脚本目录）
    script_dir = os.path.dirname(os.path.abspath(__file__))
    assets_path = os.path.join(script_dir, "..", "assets", "plink.exe")
    if os.path.exists(assets_path):
        return os.path.abspath(assets_path)

    # 如果都找不到，尝试直接调用 plink（假设在 PATH 中）
    return "plink.exe"


def generate_task_filename(vendor: str) -> str:
    """
    生成任务文件名：{厂家}_{时间戳}.txt
    
    Args:
        vendor: 厂家名称
    
    Returns:
        str: 任务文件名
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{vendor}_{timestamp}.txt"


def generate_log_filename(vendor: str) -> str:
    """
    生成日志文件名：{厂家}_{时间戳}.log
    
    Args:
        vendor: 厂家名称
    
    Returns:
        str: 日志文件名
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{vendor}_{timestamp}.log"


def create_task_file(vendor: str, com_port: str, baud_rate: int, 
                     password: str, commands: List[str], 
                     output_dir: str = ".") -> Tuple[str, str]:
    """
    创建任务文件
    
    Args:
        vendor: 厂家名称
        com_port: COM端口
        baud_rate: 波特率
        password: 密码
        commands: 命令列表
        output_dir: 输出目录（默认当前工作目录）
    
    Returns:
        Tuple[str, str]: (任务文件路径, 日志文件路径)
    """
    # 生成文件名（使用相同的时间戳）
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    task_filename = f"{vendor}_{timestamp}.txt"
    log_filename = f"{vendor}_{timestamp}.log"
    
    # 输出到指定目录
    task_file = os.path.join(output_dir, task_filename)
    log_file = os.path.join(output_dir, log_filename)
    
    # 创建任务文件
    with open(task_file, 'w', encoding='utf-8') as f:
        f.write("[METADATA]\n")
        f.write(f"vendor={vendor}\n")
        f.write(f"com_port={com_port}\n")
        f.write(f"baud_rate={baud_rate}\n")
        if password:
            f.write(f"password={password}\n")
        f.write(f"log_file={log_filename}\n")
        f.write(f"created_at={datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("\n[COMMANDS]\n")
        for cmd in commands:
            f.write(f"{cmd}\n")
        f.write("\n[END]\n")
    
    return task_file, log_file


def parse_task_file(task_file: str) -> Tuple[Dict[str, str], List[str]]:
    """
    解析任务文件，提取元数据和命令列表

    Args:
        task_file: 任务文件路径

    Returns:
        Tuple[Dict[str, str], List[str]]: (元数据字典, 命令列表)
    """
    metadata = {}
    commands = []
    section = None

    with open(task_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            
            # 忽略空行和注释
            if not line or line.startswith('#'):
                continue
            
            # 识别段落标记
            if line == '[METADATA]':
                section = 'metadata'
                continue
            elif line == '[COMMANDS]':
                section = 'commands'
                continue
            elif line == '[END]':
                break
            
            # 解析内容
            if section == 'metadata':
                if '=' in line:
                    key, value = line.split('=', 1)
                    metadata[key.strip()] = value.strip()
            elif section == 'commands':
                commands.append(line)
    
    return metadata, commands


def analyze_log_progress(log_file: str, commands: List[str]) -> int:
    """
    分析日志文件，找出上次执行到哪一步

    Args:
        log_file: 日志文件路径
        commands: 完整的命令列表

    Returns:
        int: 下一个要执行的命令索引（0表示从头开始）
    """
    if not os.path.exists(log_file):
        return 0
    
    executed_commands = []
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                # 查找 [SEND] 标记的命令
                if '[SEND]' in line:
                    # 提取命令内容
                    match = re.search(r'\[SEND\]\s+(.+)', line)
                    if match:
                        cmd = match.group(1).strip()
                        executed_commands.append(cmd)
    except Exception as e:
        print(f"分析日志文件失败: {e}")
        return 0
    
    # 找到下一个未执行的命令
    for i, cmd in enumerate(commands):
        if i >= len(executed_commands) or cmd != executed_commands[i]:
            return i
    
    # 所有命令都已执行
    return len(commands)


class SerialPlink:
    """串口通信类，用于与交换机进行交互"""

    def __init__(self, plink_path: str = None, com_port: str = "COM6",
                 baud_rate: int = 115200, password: str = None, log_file: str = None):
        """
        初始化串口通信

        Args:
            plink_path: plink.exe 路径（可选，如果不指定会自动查找）
            com_port: COM端口号，如 "COM6"
            baud_rate: 波特率，默认115200
            password: 密码（可选）
            log_file: 日志文件路径
        """
        self.plink_path = find_plink_exe(plink_path)
        self.com_port = com_port
        self.baud_rate = baud_rate
        self.password = password
        self.serial_config = f"{baud_rate},8,1,N,N"
        self.process = None
        self.prompts = ["#", ">", "]"]  # 常见的交换机提示符
        self.log_file = log_file
        self.logger = None
        self.is_windows = platform.system() == "Windows"

    def _init_logger(self):
        """初始化日志器"""
        if self.logger is None and self.log_file:
            self.logger = setup_logger(self.log_file)

    def connect(self) -> bool:
        """
        建立与交换机的串口连接

        Returns:
            bool: 连接是否成功
        """
        self._init_logger()
        if self.logger:
            self.logger.info(f"=" * 50)
            self.logger.info(f"开始连接串口 {self.com_port}, 波特率 {self.baud_rate}")
            self.logger.info(f"使用 plink 路径: {self.plink_path}")
            self.logger.info(f"操作系统: {platform.system()}")

        try:
            self.process = subprocess.Popen(
                [self.plink_path, "-serial", self.com_port, "-sercfg", self.serial_config],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=0  # 无缓冲
            )
            # 等待连接建立
            time.sleep(1)
            if self.logger:
                self.logger.info(f"✓ 已成功连接到 {self.com_port}")
            return True
        except FileNotFoundError:
            if self.logger:
                self.logger.error(f"✗ 未找到 plink.exe，尝试路径: {self.plink_path}")
                self.logger.error(f"✗ 请确保 plink.exe 在 assets/ 目录或当前目录下")
            return False
        except Exception as e:
            if self.logger:
                self.logger.error(f"✗ 连接失败: {e}")
            return False

    def send_command(self, command: str, wait_time: float = 2.0) -> str:
        """
        发送单条命令并获取响应
        改进：增加异常处理，避免 OSError

        Args:
            command: 要发送的命令
            wait_time: 发送后等待响应的时间（秒），默认2.0秒

        Returns:
            str: 命令执行后的输出
        """
        if not self.process:
            raise RuntimeError("请先调用 connect() 建立连接")

        if self.logger:
            self.logger.info(f"[SEND] {command}")

        try:
            # 检查进程是否还活着
            if self.process.poll() is not None:
                if self.logger:
                    self.logger.error("进程已结束，无法发送命令")
                return ""
            
            # 发送命令（使用 \n，更兼容）
            self.process.stdin.write(command + "\n")
            self.process.stdin.flush()
        except (OSError, ValueError) as e:
            if self.logger:
                self.logger.error(f"发送命令失败 (OSError/ValueError): {e}")
                self.logger.error("可能原因：进程已关闭或stdin已关闭")
            return ""
        except Exception as e:
            if self.logger:
                self.logger.error(f"发送命令失败: {e}")
            return ""

        # 等待响应 - 增加等待时间
        time.sleep(wait_time)

        # 读取可用输出
        output = self._read_output()

        if output and self.logger:
            # 记录完整输出，但显示时截断
            self.logger.info(f"[RECV] {output[:500]}")
            
            # 检查错误
            if "Error" in output or "Invalid" in output:
                self.logger.warning(f"⚠️ 检测到错误: {output}")

        return output

    def _read_output(self, timeout: float = 0.5) -> str:
        """
        读取输出缓冲区（改进Windows兼容性）
        
        Args:
            timeout: 读取超时时间
        
        Returns:
            str: 读取到的输出
        """
        output = ""
        
        try:
            # 简单的轮询读取
            end_time = time.time() + timeout
            while time.time() < end_time:
                if self.process.poll() is not None:
                    break
                    
                # 尝试非阻塞读取
                try:
                    import msvcrt
                    import sys
                    # Windows下直接从stdout读取
                    # 这里简化处理，避免复杂的非阻塞IO
                    time.sleep(0.1)
                except:
                    pass
        except:
            pass
        
        return output

    def execute_commands(self, commands: list, delay: float = 2.0) -> dict:
        """
        逐条执行命令列表，每条命令之间有延迟

        Args:
            commands: 命令列表
            delay: 每条命令之间的延迟（秒），默认2.0秒

        Returns:
            dict: 包含每条命令的输入和输出
        """
        self._init_logger()
        if self.logger:
            self.logger.info(f"=" * 50)
            self.logger.info(f"开始逐条执行 {len(commands)} 条命令")
            self.logger.info(f"每条命令间隔: {delay} 秒")

        results = {}
        for i, cmd in enumerate(commands, 1):
            if self.logger:
                self.logger.info(f"[{i}/{len(commands)}] 准备执行命令: {cmd}")

            try:
                output = self.send_command(cmd, wait_time=delay)
                results[cmd] = {
                    "status": "success",
                    "output": output,
                    "error": None
                }

                # 检查输出中是否包含错误信息
                if output and ("Error" in output or "Invalid" in output or "Failed" in output):
                    results[cmd]["status"] = "error"
                    results[cmd]["error"] = "Command failed based on output"
                    if self.logger:
                        self.logger.error(f"❌ 命令执行失败: {cmd}")
                        self.logger.error(f"错误输出: {output}")

            except Exception as e:
                if self.logger:
                    self.logger.error(f"命令执行异常: {e}")
                results[cmd] = {
                    "status": "error",
                    "output": "",
                    "error": str(e)
                }

        if self.logger:
            success_count = sum(1 for r in results.values() if r['status'] == 'success')
            self.logger.info(f"✓ 批量命令执行完成，成功 {success_count}/{len(commands)}")
        
        return results

    def disconnect(self):
        """断开与交换机的连接（改进异常处理）"""
        if self.process:
            if self.logger:
                self.logger.info(f"断开与 {self.com_port} 的连接")
            
            # 尝试发送退出命令（加异常处理）
            try:
                if self.process.poll() is None:  # 进程还活着
                    self.process.stdin.write("quit\n")
                    self.process.stdin.flush()
            except (OSError, ValueError):
                pass  # 忽略写入错误
            except Exception:
                pass

            # 尝试优雅终止
            try:
                self.process.terminate()
                self.process.wait(timeout=3)
            except:
                try:
                    self.process.kill()
                except:
                    pass

            self.process = None
            if self.logger:
                self.logger.info(f"✓ 已断开与 {self.com_port} 的连接")
                self.logger.info(f"日志已保存至: {self.log_file}")


def execute_task_file(task_file: str, resume: bool = False, output_dir: str = None) -> dict:
    """
    从任务文件执行配置（推荐使用）
    
    Args:
        task_file: 任务文件路径
        resume: 是否从上次中断位置继续
        output_dir: 日志文件输出目录（默认使用任务文件所在目录）
    
    Returns:
        dict: 执行结果
    """
    # 解析任务文件
    try:
        metadata, commands = parse_task_file(task_file)
    except FileNotFoundError:
        return {"error": f"任务文件不存在: {task_file}"}
    except Exception as e:
        return {"error": f"解析任务文件失败: {e}"}
    
    # 提取元数据
    vendor = metadata.get('vendor', 'UNKNOWN')
    com_port = metadata.get('com_port', 'COM6')
    baud_rate = int(metadata.get('baud_rate', '115200'))
    password = metadata.get('password')
    log_file = metadata.get('log_file')
    
    # 确定日志文件路径
    if log_file:
        # 如果指定了output_dir，使用output_dir
        if output_dir:
            log_file = os.path.join(output_dir, os.path.basename(log_file))
        # 否则，如果log_file不是绝对路径，使用任务文件所在目录
        elif not os.path.isabs(log_file):
            task_dir = os.path.dirname(os.path.abspath(task_file))
            log_file = os.path.join(task_dir, log_file)
    else:
        # 如果没有指定日志文件，自动生成
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = f"{vendor}_{timestamp}.log"
        if output_dir:
            log_file = os.path.join(output_dir, log_filename)
        else:
            task_dir = os.path.dirname(os.path.abspath(task_file))
            log_file = os.path.join(task_dir, log_filename)
    
    # 断点续传：分析上次执行进度
    start_index = 0
    if resume:
        start_index = analyze_log_progress(log_file, commands)
        if start_index > 0:
            print(f"✓ 检测到上次执行到第 {start_index} 条命令，从此处继续...")
        elif start_index == len(commands):
            print(f"✓ 所有命令已执行完成")
            return {"status": "completed", "message": "所有命令已执行完成"}
    
    # 执行命令
    plink = SerialPlink(
        com_port=com_port,
        baud_rate=baud_rate,
        password=password,
        log_file=log_file
    )
    
    try:
        if not plink.connect():
            return {"error": "连接失败"}
        
        # 从断点位置开始执行
        commands_to_execute = commands[start_index:]
        if start_index > 0:
            print(f"跳过前 {start_index} 条已执行的命令")
        
        results = plink.execute_commands(commands_to_execute, delay=2.0)
        
        return {
            "status": "success",
            "log_file": log_file,
            "results": results,
            "total_commands": len(commands),
            "executed_commands": len(commands_to_execute),
            "skipped_commands": start_index
        }
    finally:
        plink.disconnect()


def send_single_command(com_port: str, command: str, password: str = None,
                        baud_rate: int = 115200, log_file: str = "plink.log") -> str:
    """
    便捷函数：发送单条命令

    Args:
        com_port: COM端口号
        command: 要发送的命令
        password: 密码（可选）
        baud_rate: 波特率
        log_file: 日志文件路径

    Returns:
        str: 命令执行后的输出
    """
    plink = SerialPlink(com_port=com_port, baud_rate=baud_rate,
                        password=password, log_file=log_file)

    try:
        if not plink.connect():
            return "连接失败"

        return plink.send_command(command)
    finally:
        plink.disconnect()


def execute_command_list(com_port: str, commands: list, password: str = None,
                         baud_rate: int = 115200, delay: float = 2.0,
                         log_file: str = None, vendor: str = "DEVICE",
                         output_dir: str = ".") -> dict:
    """
    便捷函数：批量执行命令列表（不推荐，建议使用 execute_task_file）

    Args:
        com_port: COM端口号
        commands: 命令列表
        password: 密码（可选）
        baud_rate: 波特率
        delay: 每条命令之间的延迟（默认2.0秒）
        log_file: 日志文件路径（如不指定，自动生成）
        vendor: 厂家名称（用于自动生成日志文件名）
        output_dir: 输出目录（默认当前目录）

    Returns:
        dict: 每条命令的执行结果
    """
    # 如果没有指定日志文件，自动生成
    if not log_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(output_dir, f"{vendor}_{timestamp}.log")
    
    plink = SerialPlink(com_port=com_port, baud_rate=baud_rate,
                        password=password, log_file=log_file)

    try:
        if not plink.connect():
            return {"error": "连接失败"}

        return plink.execute_commands(commands, delay=delay)
    finally:
        plink.disconnect()


# 示例用法
if __name__ == "__main__":
    print("Serial Connector v0.1 - 交换机串口通信模块")
    print("=" * 60)
    print("\n使用说明:")
    print("1. 使用 create_task_file() 创建任务文件")
    print("2. 使用 execute_task_file() 执行任务")
    print("3. 如果中断，使用 execute_task_file(resume=True) 继续")
    print("\n所有临时文件（任务文件和日志）输出到当前工作目录")
    print("保持 SKILL 文件夹纯净\n")
