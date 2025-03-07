#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
许可协议同意脚本

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

import os
import sys
import json
import time
import argparse
import curses
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.text import Text
from rich.style import Style
from rich.markdown import Markdown

def display_agreement_with_paging(agreement_text, title="许可协议"):
    """分页显示许可协议，支持n/p翻页，回车直接同意"""
    console = Console()
    console.clear()
    
    # 计算控制台高度
    height = console.height - 10  # 留出一些空间给提示信息
    
    # 将协议文本分割成行
    lines = agreement_text.split('\n')
    total_lines = len(lines)
    
    # 计算总页数
    pages = (total_lines + height - 1) // height
    current_page = 1
    
    # 用户必须查看到最后一页才能退出
    viewed_last_page = False if pages > 1 else True
    
    # 用户是否直接同意
    direct_agree = False
    
    while True:
        console.clear()
        console.print(f"[bold]{title}[/bold] (第 {current_page}/{pages} 页)", justify="center")
        console.print()
        
        # 显示当前页的内容
        start_line = (current_page - 1) * height
        end_line = min(start_line + height, total_lines)
        
        for i in range(start_line, end_line):
            console.print(lines[i])
        
        # 如果是最后一页，标记为已查看最后一页
        if current_page == pages:
            viewed_last_page = True
        
        # 显示导航提示
        console.print()
        if pages > 1:
            if current_page < pages:
                console.print("[bold]按 [n] 查看下一页，按 [p] 查看上一页，按 [Enter] 直接同意，按 [q] 退出[/bold]")
            else:
                console.print("[bold]已到达最后一页，按 [Enter] 直接同意，按 [p] 查看上一页，按 [q] 退出[/bold]")
        else:
            console.print("[bold]按 [Enter] 直接同意，按 [q] 退出[/bold]")
        
        # 获取用户输入
        key = console.input("")
        
        if key.lower() == 'q':
            if viewed_last_page:
                break
            else:
                console.print("[bold red]您必须查看完整个协议才能继续！[/bold red]")
                time.sleep(2)
        elif key.lower() == 'n' and current_page < pages:  # n键下一页
            current_page += 1
        elif key.lower() == 'p' and current_page > 1:  # p键上一页
            current_page -= 1
        elif key == '':  # Enter键直接同意
            if viewed_last_page:
                direct_agree = True
                break
            else:
                # 如果用户尚未查看最后一页，询问是否确认同意
                console.print("[bold yellow]您尚未查看完整个协议，确定要直接同意吗？[/bold yellow]")
                confirm = Confirm.ask("确认直接同意？", default=False)
                if confirm:
                    direct_agree = True
                    break
                else:
                    # 用户取消，继续浏览
                    continue
    
    return viewed_last_page, direct_agree

def show_license_agreement(force=False):
    """显示许可协议并要求用户同意"""
    console = Console()
    
    # 检查是否已经同意过许可协议
    agreement_file = '.agreement'
    if os.path.exists(agreement_file) and not force:
        try:
            with open(agreement_file, 'r') as f:
                data = json.load(f)
                if data.get('agreed', False) and data.get('viewed_full_agreement', False):
                    console.print("[bold green]您已经同意了许可协议。[/bold green]")
                    return True
        except Exception as e:
            console.print(f"[bold yellow]读取协议同意状态时出错: {str(e)}[/bold yellow]")
            # 如果文件存在但读取失败，尝试删除它
            try:
                os.remove(agreement_file)
                console.print("[bold yellow]已重置协议同意状态。[/bold yellow]")
            except:
                pass
    
    # 重要提示
    console.clear()
    console.print(Panel(
        Text("重要法律提示", style="bold red"), 
        title="请仔细阅读以下内容", 
        border_style="red"
    ))
    
    console.print(Text("本软件的重点限制包括：", style="bold red"))
    console.print("1. [bold red]地域限制[/bold red]: 严禁在中华人民共和国和美利坚合众国境内使用")
    console.print("2. [bold red]专属管辖权[/bold red]: 任何争议由北京市朝阳区人民法院专属管辖")
    console.print("3. [bold red]赔偿标准[/bold red]: 违反协议需承担包括法律费用在内的全部损失")
    console.print("4. [bold red]最终解释权[/bold red]: 本协议的最终解释权归作者所有")
    console.print("5. [bold red]使用限制[/bold red]: 仅供个人测试使用，禁止商业用途")
    console.print()
    console.print("请按 [bold]Enter[/bold] 键继续查看完整协议（或按 [bold]q[/bold] 退出）...", end="")
    key = input()
    if key.lower() == 'q':
        console.print("[bold red]您未同意许可协议，程序将退出。[/bold red]")
        return False
    
    # 准备协议文本
    agreement_text = """法律免责声明与使用限制: 
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

6. 争议解决: 因本协议引起的或与之相关的任何争议，应首先通过友好协商解决。如协商不成，
   任何一方均可将争议提交至北京市朝阳区人民法院专属管辖。

7. 赔偿责任: 如因使用者违反本协议任何条款而导致任何第三方索赔或诉讼，使用者应为作者
   辩护并赔偿作者因此遭受的全部损失，包括但不限于合理的律师费、诉讼费、赔偿金等。

8. 协议修改: 作者保留随时修改本协议的权利，修改后的协议将在发布后立即生效。使用者
   继续使用本软件即视为接受修改后的协议。

9. 完整协议: 本协议构成使用者与作者之间关于本软件使用的完整协议，并取代先前或同时的
   所有口头或书面协议、提议和陈述。

10. 可分割性: 如本协议的任何条款被认定为无效或不可执行，其余条款仍将保持完全效力。

11. 最终解释权: 本协议的最终解释权归作者所有。中文版本为本协议的官方版本。"""

    english_agreement_text = """Legal Disclaimer and Usage Restrictions:
1. This software is for the author's personal local testing only and may not be used for any commercial purposes or profit-making activities.

2. Any individual or entity using this software does so at their own risk. The author expressly disclaims any liability for any direct, indirect, incidental, special, punitive, or consequential damages that may result from the use of this software, whether foreseeable or not, and regardless of the theory of liability.

3. Users must comply with all applicable national, regional, and international laws and regulations, including but not limited to computer security laws, network security laws, data protection laws, and privacy laws. The author is not responsible for any use that violates laws or regulations.

4. Territorial Restrictions: It is strictly prohibited to use this software within the territories of the People's Republic of China and the United States of America, or to request, access, process, or store any data, information, or assets through this software that are associated with or subject to the jurisdiction of these two countries.

5. The original author bears no legal or moral responsibility for any direct or indirect consequences resulting from secondary development, modification, distribution, or use based on this project, including but not limited to legal liability, data leakage, system damage, or any other form of loss.

6. Dispute Resolution: Any dispute arising from or related to this agreement shall first be resolved through friendly negotiation. If negotiation fails, either party may submit the dispute to the exclusive jurisdiction of the People's Court in Chaoyang District, Beijing.

7. Indemnification: If any third-party claims or lawsuits arise due to the user's violation of any terms of this agreement, the user shall defend and indemnify the author for all losses suffered, including but not limited to reasonable attorney fees, litigation costs, and damages.

8. Modification of Agreement: The author reserves the right to modify this agreement at any time, and the modified agreement will take effect immediately upon publication. Continued use of the software by users is deemed acceptance of the modified agreement.

9. Entire Agreement: This agreement constitutes the entire agreement between the user and the author regarding the use of this software and supersedes all prior or contemporaneous oral or written agreements, proposals, and representations.

10. Severability: If any provision of this agreement is deemed invalid or unenforceable, the remaining provisions will remain in full force and effect.

11. Final Right of Interpretation: The final right of interpretation of this agreement belongs to the author. The Chinese version is the official version of this agreement.

Note: This English version is for reference only. In case of any inconsistency between the Chinese and English versions, the Chinese version shall prevail."""

    # 分页显示中文版许可协议
    viewed_chinese, direct_agree_chinese = display_agreement_with_paging(agreement_text, "许可协议（中文版）")
    
    # 如果用户在中文版直接同意，跳过英文版
    if direct_agree_chinese:
        agreed = True
    else:
        # 分页显示英文版许可协议
        viewed_english, direct_agree_english = display_agreement_with_paging(english_agreement_text, "License Agreement (English Version - For Reference Only)")
        
        # 确保用户至少查看了中文版协议
        if not viewed_chinese:
            console.print("[bold red]您必须查看完整个中文版许可协议才能继续！[/bold red]")
            return False
        
        console.clear()
        # 要求用户同意
        console.print("[bold red]重要提示：使用本软件即表示您确认已阅读、理解并同意遵守上述所有条款和条件。[/bold red]")
        console.print("[bold red]如不同意，请立即停止使用本软件并删除所有相关文件。[/bold red]")
        console.print()
        
        agreed = Confirm.ask("您是否同意上述许可协议？", default=False)
    
    if not agreed:
        console.print("[bold red]您未同意许可协议，程序将退出。[/bold red]")
        return False
    
    # 保存用户同意记录
    try:
        agreement_data = {
            'agreed': True, 
            'timestamp': time.time(),
            'viewed_full_agreement': True
        }
        
        # 写入文件
        with open(agreement_file, 'w') as f:
            json.dump(agreement_data, f)
            
        # 验证文件是否正确写入
        if os.path.exists(agreement_file):
            with open(agreement_file, 'r') as f:
                verify_data = json.load(f)
                if not (verify_data.get('agreed', False) and verify_data.get('viewed_full_agreement', False)):
                    console.print("[bold yellow]警告: 协议同意状态可能未正确保存。[/bold yellow]")
        else:
            console.print("[bold yellow]警告: 协议同意文件未创建。[/bold yellow]")
            
    except Exception as e:
        console.print(f"[bold yellow]保存协议同意状态时出错: {str(e)}[/bold yellow]")
    
    console.print("[bold green]感谢您同意许可协议。现在您可以使用本软件了。[/bold green]")
    return True

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='许可协议同意脚本')
    parser.add_argument('-f', '--force', action='store_true', help='强制显示许可协议，即使已经同意过')
    return parser.parse_args()

def main():
    """主函数"""
    args = parse_args()
    result = show_license_agreement(force=args.force)
    # 根据用户是否同意返回状态码
    if result:
        sys.exit(0)  # 成功 - 用户同意或已经同意过
    else:
        sys.exit(1)  # 失败 - 用户未同意

if __name__ == '__main__':
    main() 