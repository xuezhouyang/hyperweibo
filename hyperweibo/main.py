#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Java项目构建工具 - 主程序

作者: Xue Zhouyang <xuezhouyang@gmail.com>
许可证: MIT License (Modified with Extended Disclaimers)

法律免责声明与使用限制: 
    1. 本软件仅供作者个人本地测试使用，不得用于任何商业目的或获利行为。
    
    2. 任何个人或实体使用本软件应自行承担全部风险。作者明确声明不对使用本软件可能导致的
       任何直接、间接、偶然、特殊、惩罚性或后果性损害承担任何责任，无论此类损害是否可预见，
       也无论责任理论如何。
    
    3. 使用者必须遵守所有适用的国家、地区和国际法律法规，包括但不限于计算机安全法、
       网络安全法、数据保护法和隐私法。作者不对任何违反法律法规的使用行为承担责任。
    
    4. 地域限制: 严禁在中华人民共和国和美利坚合众国境内使用本软件，或通过本软件请求、
       访问、处理或存储与这两国有利益关联或受其管辖的任何数据、信息或资产。
    
    5. 任何基于本项目的二次开发、修改、分发或使用导致的任何直接或间接后果，包括但不限于
       法律责任、数据泄露、系统损害或任何其他形式的损失，均与原作者无关，原作者不承担
       任何法律或道德责任。
"""

import argparse
import sys
import time
import os
import json
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich import print
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

# 尝试使用相对导入
try:
    from api.weibo_api import WeiboAPI
    from utils.formatter import WeiboFormatter
except ImportError:
    # 如果相对导入失败，尝试使用绝对导入
    try:
        from hyperweibo.api.weibo_api import WeiboAPI
        from hyperweibo.utils.formatter import WeiboFormatter
    except ImportError:
        # 如果绝对导入也失败，尝试调整导入路径
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from hyperweibo.api.weibo_api import WeiboAPI
        from hyperweibo.utils.formatter import WeiboFormatter

console = Console()

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="Java项目构建工具")
    parser.add_argument("-b", "--browser", default="chrome", choices=["chrome", "firefox", "edge", "safari"],
                        help="指定浏览器进行集成测试 (默认: chrome)")
    parser.add_argument("-s", "--special", action="store_true",
                        help="运行特殊测试套件")
    parser.add_argument("-r", "--refresh", type=int, default=0,
                        help="自动刷新间隔（秒），0表示不自动刷新")
    parser.add_argument("-m", "--mock", action="store_true",
                        help="使用模拟数据进行测试")
    parser.add_argument("-c", "--cookie", type=str,
                        help="提供测试会话cookie")
    parser.add_argument("-p", "--page", type=int, default=1,
                        help="起始页码，从1开始 (默认: 1)")
    parser.add_argument("-g", "--group", type=str,
                        help="指定测试组ID")
    
    return parser.parse_args()

def clear_screen():
    """清屏"""
    os.system('cls' if os.name == 'nt' else 'clear')

def display_groups(groups):
    """显示分组列表"""
    table = Table(title="测试组列表")
    table.add_column("序号", style="cyan")
    table.add_column("组ID", style="green")
    table.add_column("组名称", style="magenta")
    
    for i, group in enumerate(groups):
        table.add_row(str(i+1), group["gid"], group["name"])
    
    console.print(table)

def show_license_agreement():
    """显示许可协议并要求用户同意"""
    console = Console()
    
    # 检查是否已经同意过许可协议
    agreement_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.agreement')
    if os.path.exists(agreement_file):
        try:
            with open(agreement_file, 'r') as f:
                data = json.load(f)
                if data.get('agreed', False) and data.get('viewed_full_agreement', False):
                    return True
        except:
            pass
    
    # 使用专门的agree.py脚本显示许可协议并获取用户同意
    agree_script = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'agree.py')
    if os.path.exists(agree_script):
        try:
            # 调用agree.py脚本
            import subprocess
            result = subprocess.run([sys.executable, agree_script], capture_output=False)
            if result.returncode == 0:
                return True
            else:
                console.print("[bold red]您必须同意许可协议才能使用本软件。[/bold red]")
                sys.exit(1)
        except Exception as e:
            console.print(f"[bold red]运行许可协议同意脚本时出错: {str(e)}[/bold red]")
    
    # 如果agree.py脚本不存在或运行失败，则使用简化版的同意机制
    console.clear()
    console.print("[bold red]重要法律声明[/bold red]", justify="center")
    console.print()
    
    console.print("[bold red]您必须同意许可协议才能使用本软件。[/bold red]")
    console.print("[bold]请运行 './mvn agree' 命令查看并同意许可协议。[/bold]")
    sys.exit(1)

def main():
    """主函数"""
    # 许可协议检查已经在mvn脚本中完成，此处不再需要
    # show_license_agreement()
    
    args = parse_args()
    
    try:
        # 初始化API
        console.print("[bold cyan]正在初始化构建环境...[/bold cyan]")
        console.print("[bold yellow]如果无法自动获取会话信息，将会打开浏览器进行认证[/bold yellow]")
        api = WeiboAPI(browser=args.browser, use_mock=args.mock, cookie_str=args.cookie)
        
        # 获取分组列表
        groups = api.get_groups()
        
        # 当前页码
        current_page = args.page
        
        # 当前分组
        current_group = None
        if args.group:
            # 如果指定了分组ID，查找对应的分组
            for group in groups:
                if group["gid"] == args.group:
                    current_group = group
                    break
            if not current_group:
                console.print(f"[bold red]未找到指定的测试组ID: {args.group}[/bold red]")
                return 1
        
        # 主循环
        while True:
            # 根据参数决定显示哪类数据
            if current_group:
                # 显示指定分组的数据
                console.print(f"[bold cyan]正在获取[{current_group['name']}]测试组的数据（第{current_page}页）...[/bold cyan]")
                weibos = api.get_group_timeline(current_group["gid"], page=current_page)
                title = f"{current_group['name']}测试组数据（第{current_page}页）"
            elif args.special:
                # 显示特别关注的数据
                console.print(f"[bold cyan]正在获取特殊测试套件数据（第{current_page}页）...[/bold cyan]")
                weibos = api.get_special_focus(page=current_page)
                title = f"特殊测试套件数据（第{current_page}页）"
            else:
                # 显示关注的数据
                console.print(f"[bold cyan]正在获取标准测试套件数据（第{current_page}页）...[/bold cyan]")
                weibos = api.get_home_timeline(page=current_page)
                title = f"标准测试套件数据（第{current_page}页）"
            
            # 显示数据
            clear_screen()
            console.print(f"[bold cyan]Java项目构建工具 - 测试报告[/bold cyan]")
            console.print()
            WeiboFormatter.display_weibos(weibos, title)
            
            # 显示菜单
            console.print("[bold cyan]操作菜单[/bold cyan]")
            console.print("1. 刷新当前页")
            console.print("2. 切换到" + ("标准测试套件" if current_group or args.special else "特殊测试套件"))
            console.print("3. 选择测试组")
            console.print("n. 下一页")
            console.print("p. 上一页")
            console.print("g. 跳转到指定页")
            console.print("q. 退出")
            console.print()
            
            # 如果设置了自动刷新，则启动倒计时
            if args.refresh > 0:
                choice = None
                for i in range(args.refresh, 0, -1):
                    console.print(f"\r将在 {i} 秒后自动刷新...", end="")
                    # 检查是否有按键输入
                    if os.name == 'nt':
                        import msvcrt
                        if msvcrt.kbhit():
                            choice = msvcrt.getch().decode('utf-8').lower()
                            break
                    else:
                        import select
                        rlist, _, _ = select.select([sys.stdin], [], [], 1)
                        if rlist:
                            choice = sys.stdin.read(1).lower()
                            # 清除输入缓冲区
                            sys.stdin.readline()
                            break
                        else:
                            time.sleep(1)
                
                console.print()
            else:
                # 如果没有设置自动刷新，则等待用户输入
                choice = Prompt.ask("请选择", choices=["1", "2", "3", "n", "p", "g", "q"], default="1")
            
            # 处理用户选择
            if choice == "q":
                break
            elif choice == "2":
                if current_group:
                    # 如果当前是分组，切换到首页
                    current_group = None
                    args.special = False
                else:
                    # 否则切换特别关注/首页
                    args.special = not args.special
                current_page = 1  # 切换类型时重置页码
            elif choice == "3":
                # 显示分组列表
                clear_screen()
                console.print("[bold cyan]测试组列表[/bold cyan]")
                console.print()
                display_groups(groups)
                console.print()
                
                # 选择分组
                try:
                    group_index = int(Prompt.ask("请选择测试组序号（输入0返回）", default="0"))
                    if group_index > 0 and group_index <= len(groups):
                        current_group = groups[group_index - 1]
                        args.special = False  # 切换到分组时关闭特别关注
                        current_page = 1  # 切换分组时重置页码
                    elif group_index != 0:
                        console.print("[bold red]无效的测试组序号[/bold red]")
                        time.sleep(1)
                except ValueError:
                    console.print("[bold red]请输入有效的数字[/bold red]")
                    time.sleep(1)
            elif choice == "n":
                current_page += 1
            elif choice == "p":
                if current_page > 1:
                    current_page -= 1
                else:
                    console.print("[bold yellow]已经是第一页了[/bold yellow]")
                    time.sleep(1)
            elif choice == "g":
                try:
                    page = int(Prompt.ask("请输入页码"))
                    if page > 0:
                        current_page = page
                    else:
                        console.print("[bold red]页码必须大于0[/bold red]")
                        time.sleep(1)
                except ValueError:
                    console.print("[bold red]请输入有效的页码[/bold red]")
                    time.sleep(1)
            # 对于选择1或自动刷新超时，直接进入下一次循环刷新
        
        return 0
    
    except KeyboardInterrupt:
        console.print("\n[bold cyan]构建已中止[/bold cyan]")
        return 0
    except Exception as e:
        console.print(f"[bold red]构建失败: {str(e)}[/bold red]")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 