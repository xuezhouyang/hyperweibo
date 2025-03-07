#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
微博命令行工具

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

import sys
import os
import locale
import argparse

# 添加当前目录到模块搜索路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="微博命令行工具")
    parser.add_argument("-l", "--language", choices=["en", "zh", "auto"], default="auto",
                        help="设置语言 (en/zh/auto)")
    parser.add_argument("-s", "--style", choices=["weibo", "maven"], default="weibo",
                        help="设置界面风格 (weibo/maven)")
    parser.add_argument("-y", "--style-passthrough", dest="style", 
                        help=argparse.SUPPRESS)  # 用于从mvn脚本传递风格参数
    
    # 添加其他参数
    parser.add_argument("-b", "--browser", default="chrome", choices=["chrome", "firefox", "edge", "safari"],
                        help="指定浏览器 (默认: chrome)")
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
    parser.add_argument("-S", "--special", action="store_true",
                        help="查看特别关注内容")
    
    args, unknown = parser.parse_known_args()
    
    # 如果语言设置为auto，则自动检测系统语言
    if args.language == "auto":
        system_lang, _ = locale.getdefaultlocale()
        args.language = "en" if system_lang and system_lang.startswith("en") else "zh"
    
    return args

if __name__ == "__main__":
    # 解析语言和风格参数
    args = parse_args()
    
    # 设置环境变量，传递给main模块
    os.environ["HYPERWEIBO_LANGUAGE"] = args.language
    os.environ["HYPERWEIBO_STYLE"] = args.style
    
    # 导入主程序
    from hyperweibo.main import main
    
    sys.exit(main()) 