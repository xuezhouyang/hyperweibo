#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
从curl命令中提取cookie

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
import re

def extract_cookie_from_curl(curl_command):
    """从curl命令中提取cookie"""
    # 查找-b或--cookie参数后的cookie字符串
    cookie_match = re.search(r'-b\s+\'([^\']+)\'', curl_command)
    if not cookie_match:
        cookie_match = re.search(r'--cookie\s+\'([^\']+)\'', curl_command)
    
    if cookie_match:
        return cookie_match.group(1)
    else:
        return None

def main():
    """主函数"""
    if len(sys.argv) > 1:
        # 从命令行参数读取curl命令
        curl_command = sys.argv[1]
    else:
        # 从标准输入读取curl命令
        print("请输入curl命令（以Ctrl+D结束）：")
        curl_command = sys.stdin.read()
    
    cookie = extract_cookie_from_curl(curl_command)
    if cookie:
        print("\n提取的cookie：")
        print(cookie)
        print("\n使用方法：")
        print(f"python hyperweibo.py -c '{cookie}'")
    else:
        print("未找到cookie，请确保curl命令包含-b或--cookie参数")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 