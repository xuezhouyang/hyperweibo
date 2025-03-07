#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
微博命令行工具 - 主程序

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
import datetime

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

# 获取语言和风格设置
LANGUAGE = os.environ.get("HYPERWEIBO_LANGUAGE", "zh")
STYLE = os.environ.get("HYPERWEIBO_STYLE", "weibo")

# 文案定义
TEXT = {
    "en": {
        "weibo": {
            "title": "Weibo Command Line Tool",
            "initializing": "Initializing...",
            "browser_auth": "If unable to automatically get session info, a browser will open for authentication",
            "group_not_found": "Group ID not found: {}",
            "timeline": "Timeline (Page {})",
            "special_timeline": "Special Focus Timeline (Page {})",
            "group_timeline": "{} Timeline (Page {})",
            "total_records": "Total {} records",
            "no_records": "No records found",
            "operation_menu": "Operation Menu",
            "refresh": "Refresh current page",
            "switch_special": "Switch to special focus",
            "switch_normal": "Switch to normal timeline",
            "select_group": "Select group",
            "next_page": "Next page",
            "prev_page": "Previous page",
            "goto_page": "Go to specific page",
            "exit": "Exit",
            "select_prompt": "Please select [1/2/3/n/p/g/q] (1): ",
            "group_list": "Group List",
            "group_number": "No.",
            "group_id": "Group ID",
            "group_name": "Group Name",
            "select_group_prompt": "Please select group number (0 to return): ",
            "page_prompt": "Enter page number: ",
            "invalid_input": "Invalid input, please try again",
            "loading": "Loading data...",
            "quotes": "Reposts",
            "comments": "Comments",
            "likes": "Likes",
            "attachments": "Attachments",
            "media": "Media",
            "stats_error": "Error processing statistics",
            "attachment_error": "Error processing attachments",
            "quote_error": "Error processing quoted content",
            "quote_prefix": "Quote from @{}:",
            "retweet_prefix": "Retweet from @{}:",
            "item_count": "{} items"
        },
        "maven": {
            "title": "Java Project Build Tool",
            "initializing": "Initializing build environment...",
            "browser_auth": "If unable to automatically get session info, a browser will open for authentication",
            "group_not_found": "Test group ID not found: {}",
            "timeline": "Standard Test Suite Data (Page {})",
            "special_timeline": "Special Test Suite Data (Page {})",
            "group_timeline": "{} Test Data (Page {})",
            "total_records": "Total {} records",
            "no_records": "No records found",
            "operation_menu": "Operation Menu",
            "refresh": "Refresh current page",
            "switch_special": "Switch to special test suite",
            "switch_normal": "Switch to standard test suite",
            "select_group": "Select test group",
            "next_page": "Next page",
            "prev_page": "Previous page",
            "goto_page": "Go to specific page",
            "exit": "Exit",
            "select_prompt": "Please select [1/2/3/n/p/g/q] (1): ",
            "group_list": "Test Group List",
            "group_number": "No.",
            "group_id": "Group ID",
            "group_name": "Group Name",
            "select_group_prompt": "Please select test group number (0 to return): ",
            "page_prompt": "Enter page number: ",
            "invalid_input": "Invalid input, please try again",
            "loading": "Loading data...",
            "quotes": "References",
            "comments": "Comments",
            "likes": "Approvals",
            "attachments": "Attachments",
            "media": "Multimedia",
            "stats_error": "Error processing statistics",
            "attachment_error": "Error processing attachments",
            "quote_error": "Error processing referenced content",
            "quote_prefix": "Reference from @{}:",
            "retweet_prefix": "Reference from @{}:",
            "item_count": "{} items"
        }
    },
    "zh": {
        "weibo": {
            "title": "微博命令行工具",
            "initializing": "正在初始化...",
            "browser_auth": "如果无法自动获取会话信息，将会打开浏览器进行认证",
            "group_not_found": "未找到指定的分组ID: {}",
            "timeline": "微博关注内容（第{}页）",
            "special_timeline": "特别关注内容（第{}页）",
            "group_timeline": "{}分组内容（第{}页）",
            "total_records": "共 {} 条记录",
            "no_records": "没有找到记录",
            "operation_menu": "操作菜单",
            "refresh": "刷新当前页",
            "switch_special": "切换到特别关注",
            "switch_normal": "切换到普通关注",
            "select_group": "选择分组",
            "next_page": "下一页",
            "prev_page": "上一页",
            "goto_page": "跳转到指定页",
            "exit": "退出",
            "select_prompt": "请选择 [1/2/3/n/p/g/q] (1): ",
            "group_list": "分组列表",
            "group_number": "序号",
            "group_id": "分组ID",
            "group_name": "分组名称",
            "select_group_prompt": "请选择分组序号（输入0返回）: ",
            "page_prompt": "请输入页码: ",
            "invalid_input": "输入无效，请重试",
            "loading": "正在加载数据...",
            "quotes": "转发",
            "comments": "评论",
            "likes": "点赞",
            "attachments": "附件",
            "media": "多媒体",
            "stats_error": "处理统计信息时出错",
            "attachment_error": "处理附件时出错",
            "quote_error": "处理引用内容时出错",
            "quote_prefix": "引用@{}:",
            "retweet_prefix": "转发@{}:",
            "item_count": "{}个"
        },
        "maven": {
            "title": "Java项目构建工具",
            "initializing": "正在初始化构建环境...",
            "browser_auth": "如果无法自动获取会话信息，将会打开浏览器进行认证",
            "group_not_found": "未找到指定的测试组ID: {}",
            "timeline": "标准测试套件数据（第{}页）",
            "special_timeline": "特殊测试套件数据（第{}页）",
            "group_timeline": "{}测试数据（第{}页）",
            "total_records": "共 {} 条记录",
            "no_records": "没有找到记录",
            "operation_menu": "操作菜单",
            "refresh": "刷新当前页",
            "switch_special": "切换到特殊测试套件",
            "switch_normal": "切换到标准测试套件",
            "select_group": "选择测试组",
            "next_page": "下一页",
            "prev_page": "上一页",
            "goto_page": "跳转到指定页",
            "exit": "退出",
            "select_prompt": "请选择 [1/2/3/n/p/g/q] (1): ",
            "group_list": "测试组列表",
            "group_number": "序号",
            "group_id": "组ID",
            "group_name": "组名称",
            "select_group_prompt": "请选择测试组序号（输入0返回）: ",
            "page_prompt": "请输入页码: ",
            "invalid_input": "输入无效，请重试",
            "loading": "正在加载数据...",
            "quotes": "引用",
            "comments": "评论",
            "likes": "赞同",
            "attachments": "附件",
            "media": "多媒体",
            "stats_error": "处理统计信息时出错",
            "attachment_error": "处理附件时出错",
            "quote_error": "处理引用内容时出错",
            "quote_prefix": "引用@{}:",
            "retweet_prefix": "引用@{}:",
            "item_count": "{}个"
        }
    }
}

# 获取当前语言和风格的文案
def get_text(key):
    return TEXT[LANGUAGE][STYLE].get(key, key)

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description=get_text("title"))
    parser.add_argument("-b", "--browser", default="chrome", choices=["chrome", "firefox", "edge", "safari"],
                        help="指定浏览器 (默认: chrome)")
    parser.add_argument("-s", "--special", action="store_true",
                        help="查看特别关注内容")
    parser.add_argument("-r", "--refresh", type=int, default=0,
                        help="自动刷新间隔（秒），0表示不自动刷新")
    parser.add_argument("-m", "--mock", action="store_true",
                        help="使用模拟数据")
    parser.add_argument("-c", "--cookie", type=str,
                        help="提供会话cookie")
    parser.add_argument("-p", "--page", type=int, default=1,
                        help="起始页码，从1开始 (默认: 1)")
    parser.add_argument("-g", "--group", type=str,
                        help="指定分组ID")
    parser.add_argument("-l", "--language", choices=["en", "zh", "auto"], default="auto",
                        help="设置语言 (en/zh/auto)")
    parser.add_argument("-y", "--style", choices=["weibo", "maven"], default="weibo",
                        help="设置界面风格 (weibo/maven)")
    
    args = parser.parse_args()
    
    # 如果命令行参数中指定了语言和风格，则覆盖环境变量中的设置
    global LANGUAGE, STYLE
    if args.language != "auto":
        LANGUAGE = args.language
    if args.style:
        STYLE = args.style
    
    return args

def clear_screen():
    """清屏"""
    os.system('cls' if os.name == 'nt' else 'clear')

def display_groups(groups):
    """显示分组列表"""
    table = Table(title=get_text("group_list"))
    table.add_column(get_text("group_number"), style="cyan")
    table.add_column(get_text("group_id"), style="green")
    table.add_column(get_text("group_name"), style="magenta")
    
    for i, group in enumerate(groups):
        table.add_row(str(i+1), group["gid"], group["name"])
    
    console.print(table)
    
    while True:
        try:
            choice = input(get_text("select_group_prompt"))
            if choice == "0":
                return None
            choice = int(choice)
            if 1 <= choice <= len(groups):
                return groups[choice-1]
            else:
                console.print(f"[bold red]{get_text('invalid_input')}[/bold red]")
        except ValueError:
            console.print(f"[bold red]{get_text('invalid_input')}[/bold red]")

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
    console.print("[bold]请运行 './weibo agree' 命令查看并同意许可协议。[/bold]")
    sys.exit(1)

def main():
    """主函数"""
    # 许可协议检查已经在weibo脚本中完成，此处不再需要
    # show_license_agreement()
    
    args = parse_args()
    
    try:
        # 初始化API
        console.print(f"[bold cyan]{get_text('initializing')}[/bold cyan]")
        console.print(f"[bold yellow]{get_text('browser_auth')}[/bold yellow]")
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
                console.print(f"[bold red]{get_text('group_not_found').format(args.group)}[/bold red]")
                return 1
        
        # 是否显示特别关注
        is_special = args.special
        
        while True:
            clear_screen()
            
            # 显示标题
            if current_group:
                title = get_text("group_timeline").format(current_group["name"], current_page)
            elif is_special:
                title = get_text("special_timeline").format(current_page)
            else:
                title = get_text("timeline").format(current_page)
            
            console.print(f"[bold]{get_text('title')}[/bold]")
            console.print()
            console.print(f"[bold]{title}[/bold]")
            
            # 获取数据
            console.print(f"[italic]{get_text('loading')}[/italic]")
            if is_special:
                console.print(f"[bold]{get_text('special_timeline').format(current_page)}[/bold]")
                console.print(f"[dim]{get_text('loading')}[/dim]")
                data = api.get_special_focus(page=current_page)
                title = get_text('special_timeline').format(current_page)
            elif current_group:
                group_name = current_group["name"]
                console.print(f"[bold]{get_text('group_timeline').format(group_name, current_page)}[/bold]")
                console.print(f"[dim]{get_text('loading')}[/dim]")
                data = api.get_group_timeline(current_group["gid"], page=current_page)
                title = get_text('group_timeline').format(group_name, current_page)
            else:
                console.print(f"[bold]{get_text('timeline').format(current_page)}[/bold]")
                console.print(f"[dim]{get_text('loading')}[/dim]")
                data = api.get_home_timeline(page=current_page)
                title = get_text('timeline').format(current_page)
            
            # 显示数据
            if data and len(data) > 0:
                console.print(f"{get_text('total_records').format(len(data))}")
                console.print()
                
                for item in data:
                    try:
                        # 显示用户名和发布时间
                        user_info = item.get('user', {})
                        if isinstance(user_info, dict):
                            user = user_info.get('screen_name', '未知用户')
                        else:
                            user = str(user_info)
                        
                        # 处理时间
                        time_str = item.get('time', '')
                        if not time_str:
                            time_str = item.get('created_at', '未知时间')
                            # 尝试解析标准微博时间格式
                            if time_str and not time_str == '未知时间':
                                try:
                                    dt = datetime.datetime.strptime(time_str, "%a %b %d %H:%M:%S +0800 %Y")
                                    time_str = dt.strftime("%Y-%m-%d %H:%M:%S")
                                except:
                                    pass
                        
                        console.print(f"✓ [bold]{user}[/bold] {time_str}:")
                        
                        # 显示微博内容
                        try:
                            console.print()
                            # 使用clean_text处理微博内容
                            from hyperweibo.utils.formatter import WeiboFormatter
                            text = WeiboFormatter.clean_text(item.get('text', ''))
                            console.print(text)
                            
                            # 处理引用内容
                            try:
                                quote = item.get('quote', None)
                                retweeted = item.get('retweeted_status', None)
                                
                                if quote:
                                    quote_user = quote.get('user', '未知用户')
                                    quote_content = WeiboFormatter.clean_text(quote.get('content', '无内容'))
                                    console.print(f"{get_text('quote_prefix').format(quote_user)}")
                                    console.print(quote_content)
                                elif retweeted:
                                    retweeted_user_info = retweeted.get('user', {})
                                    if isinstance(retweeted_user_info, dict):
                                        retweeted_user = retweeted_user_info.get('screen_name', '未知用户')
                                    else:
                                        retweeted_user = str(retweeted_user_info)
                                    retweeted_content = WeiboFormatter.clean_text(retweeted.get('text', '无内容'))
                                    console.print(f"{get_text('retweet_prefix').format(retweeted_user)}")
                                    console.print(retweeted_content)
                            except Exception as e:
                                console.print(f"[bold yellow]{get_text('quote_error')}: {str(e)}[/bold yellow]")
                        except Exception as e:
                            console.print(f"[bold yellow]{get_text('attachment_error') if 'attachment_error' in TEXT[LANGUAGE][STYLE] else '处理附件时出错'}: {str(e)}[/bold yellow]")
                        
                        # 显示附件
                        try:
                            attachments = item.get("attachments", {})
                            pics = item.get("pics", [])
                            page_info = item.get("page_info", {})
                            
                            if attachments or pics or page_info:
                                console.print()
                                if attachments:
                                    if attachments.get("type") == "image":
                                        count = attachments.get('count', 0)
                                        console.print(f"[{get_text('attachments')}: {get_text('item_count').format(count)}]")
                                    elif attachments.get("type") == "video":
                                        console.print(f"[{get_text('media')}]")
                                elif pics and len(pics) > 0:
                                    console.print(f"[{get_text('attachments')}: {get_text('item_count').format(len(pics))}]")
                                elif page_info and page_info.get("media_info"):
                                    console.print(f"[{get_text('media')}]")
                        except Exception as e:
                            console.print(f"[bold yellow]{get_text('attachment_error') if 'attachment_error' in TEXT[LANGUAGE][STYLE] else '处理附件时出错'}: {str(e)}[/bold yellow]")
                        
                        # 显示统计信息
                        try:
                            console.print()
                            quotes = item.get('quotes', 0) or item.get('reposts_count', 0)
                            comments = item.get('comments', 0) or item.get('comments_count', 0)
                            likes = item.get('likes', 0) or item.get('attitudes_count', 0)
                            # 使用一致的格式显示统计信息
                            stats_text = f"{get_text('quotes')}: {quotes} | {get_text('comments')}: {comments} | {get_text('likes')}: {likes}"
                            console.print(stats_text)
                        except Exception as e:
                            console.print(f"[bold yellow]{get_text('stats_error') if 'stats_error' in TEXT[LANGUAGE][STYLE] else '处理统计信息时出错'}: {str(e)}[/bold yellow]")
                        
                        # 分隔线
                        console.print("─" * 80)
                        console.print()
                    except Exception as e:
                        console.print(f"[bold red]显示微博时出错: {str(e)}[/bold red]")
                        console.print(f"[bold yellow]微博数据: {item}[/bold yellow]")
                        console.print("─" * 80)
                        console.print()
            else:
                console.print(f"[bold yellow]{get_text('no_records')}[/bold yellow]")
                console.print()
            
            # 显示操作菜单
            console.print(f"[bold]{get_text('operation_menu')}[/bold]")
            console.print(f"1. {get_text('refresh')}")
            if is_special:
                console.print(f"2. {get_text('switch_normal')}")
            else:
                console.print(f"2. {get_text('switch_special')}")
            console.print(f"3. {get_text('select_group')}")
            console.print(f"n. {get_text('next_page')}")
            console.print(f"p. {get_text('prev_page')}")
            console.print(f"g. {get_text('goto_page')}")
            console.print(f"q. {get_text('exit')}")
            console.print()
            
            # 获取用户输入
            choice = input(get_text("select_prompt"))
            
            if choice == "1":
                # 刷新当前页
                continue
            elif choice == "2":
                # 切换特别关注/普通关注
                is_special = not is_special
                current_page = 1
                current_group = None
            elif choice == "3":
                # 选择分组
                selected_group = display_groups(groups)
                if selected_group:
                    current_group = selected_group
                    current_page = 1
                    is_special = False
            elif choice.lower() == "n":
                # 下一页
                current_page += 1
            elif choice.lower() == "p":
                # 上一页
                if current_page > 1:
                    current_page -= 1
            elif choice.lower() == "g":
                # 跳转到指定页
                try:
                    page = int(input(get_text("page_prompt")))
                    if page > 0:
                        current_page = page
                except ValueError:
                    console.print(f"[bold red]{get_text('invalid_input')}[/bold red]")
                    time.sleep(1)
            elif choice.lower() == "q":
                # 退出
                break
            else:
                console.print(f"[bold red]{get_text('invalid_input')}[/bold red]")
                time.sleep(1)
            
            # 自动刷新
            if args.refresh > 0:
                time.sleep(args.refresh)
        
        return 0
    except KeyboardInterrupt:
        console.print("\n[bold yellow]程序已中断[/bold yellow]")
        return 0
    except Exception as e:
        console.print(f"[bold red]发生错误: {str(e)}[/bold red]")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 