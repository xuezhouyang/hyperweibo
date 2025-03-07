#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数据格式化工具

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

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich import box
from datetime import datetime
import re
from typing import Dict, Any, List

console = Console()

class WeiboFormatter:
    """数据格式化工具，用于在终端中美观地显示测试数据"""
    
    @staticmethod
    def format_time(created_at: str) -> str:
        """格式化时间戳"""
        try:
            # 微博时间格式可能有多种，这里尝试处理常见的格式
            dt = datetime.strptime(created_at, "%a %b %d %H:%M:%S %z %Y")
            now = datetime.now()
            delta = now - dt.replace(tzinfo=None)
            
            if delta.days > 365:
                return f"{delta.days // 365}年前"
            elif delta.days > 30:
                return f"{delta.days // 30}个月前"
            elif delta.days > 0:
                return f"{delta.days}天前"
            elif delta.seconds > 3600:
                return f"{delta.seconds // 3600}小时前"
            elif delta.seconds > 60:
                return f"{delta.seconds // 60}分钟前"
            else:
                return "刚刚"
        except Exception:
            # 如果解析失败，直接返回原始时间
            return created_at
    
    @staticmethod
    def clean_text(text: str) -> str:
        """清理文本内容，去除HTML标签等"""
        # 去除HTML标签
        text = re.sub(r'<[^>]+>', '', text)
        # 替换表情符号的占位符
        text = re.sub(r'\[([^\]]+)\]', r'[\1]', text)
        return text
    
    @staticmethod
    def format_weibo(weibo: Dict[str, Any]) -> Text:
        """格式化单条数据为Rich Text"""
        try:
            # 提取数据
            user = weibo.get('user', {})
            user_name = user.get('screen_name', '未知用户')
            user_verified = user.get('verified', False)
            verified_type = user.get('verified_type', -1)
            
            # 根据认证类型设置不同的标识
            verified_mark = ""
            if user_verified:
                if verified_type == 0:  # 个人认证
                    verified_mark = "✓ "
                elif verified_type in (1, 2, 3, 5):  # 企业认证
                    verified_mark = "✓ "
                else:
                    verified_mark = "✓ "
            
            created_at = WeiboFormatter.format_time(weibo.get('created_at', ''))
            text = WeiboFormatter.clean_text(weibo.get('text', ''))
            
            # 处理转发内容
            retweeted = weibo.get('retweeted_status', None)
            retweeted_text = ""
            if retweeted:
                retweeted_user = retweeted.get('user', {}).get('screen_name', '未知用户')
                retweeted_text = WeiboFormatter.clean_text(retweeted.get('text', ''))
                retweeted_text = f"\n\n[bold cyan]引用@{retweeted_user}:[/bold cyan]\n{retweeted_text}"
            
            # 处理图片
            pics = weibo.get('pics', [])
            pics_text = ""
            if pics:
                pics_text = f"\n\n[italic][附件: {len(pics)}个][/italic]"
            
            # 处理视频
            video_info = weibo.get('page_info', {}).get('media_info', {})
            video_text = ""
            if video_info:
                video_text = "\n\n[italic][多媒体][/italic]"
            
            # 处理统计数据
            comments_count = weibo.get('comments_count', 0)
            attitudes_count = weibo.get('attitudes_count', 0)
            reposts_count = weibo.get('reposts_count', 0)
            stats_text = f"\n\n[dim]引用: {reposts_count} | 评论: {comments_count} | 赞同: {attitudes_count}[/dim]"
            
            # 组合完整内容，不使用Panel，直接返回格式化的文本
            header = f"[bold]{verified_mark}{user_name}[/bold] [dim]{created_at}:[/dim]"
            content = f"{header}\n{text}{retweeted_text}{pics_text}{video_text}{stats_text}\n"
            
            # 使用一个简单的分隔线分隔不同的数据
            content += "\n" + "─" * 80 + "\n"
            
            return Text.from_markup(content)
        except Exception as e:
            # 如果解析失败，返回错误信息
            error_text = f"[red]解析数据失败: {str(e)}[/red]"
            return Text.from_markup(error_text)
    
    @staticmethod
    def display_weibos(weibos: List[Dict[str, Any]], title: str = "测试数据"):
        """显示数据列表"""
        console.print(f"[bold cyan]{title}[/bold cyan]", style="bold")
        console.print(f"共 {len(weibos)} 条记录", style="dim")
        console.print()
        
        for weibo in weibos:
            text = WeiboFormatter.format_weibo(weibo)
            console.print(text)
    
    @staticmethod
    def display_user_info(user_info: Dict[str, Any]):
        """显示用户信息"""
        if not user_info:
            console.print("[bold red]获取用户信息失败[/bold red]")
            return
        
        screen_name = user_info.get('screen_name', '未知用户')
        description = user_info.get('description', '暂无简介')
        followers_count = user_info.get('followers_count', 0)
        follow_count = user_info.get('follow_count', 0)
        statuses_count = user_info.get('statuses_count', 0)
        
        table = Table(box=box.ROUNDED)
        table.add_column("项目", style="cyan")
        table.add_column("内容", style="white")
        
        table.add_row("用户名", screen_name)
        table.add_row("简介", description)
        table.add_row("粉丝数", str(followers_count))
        table.add_row("关注数", str(follow_count))
        table.add_row("微博数", str(statuses_count))
        
        console.print(Panel(table, title="[bold]用户信息[/bold]", border_style="green")) 