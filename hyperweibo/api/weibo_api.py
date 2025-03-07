#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
微博API客户端

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

import requests
import browser_cookie3
import json
from bs4 import BeautifulSoup
import re
import logging
from typing import List, Dict, Any, Optional
import datetime
import random
import webbrowser
import time
import os
import subprocess
from urllib.parse import urlencode
try:
    from pycookiecheat import chrome_cookies
    HAS_PYCOOKIECHEAT = True
except ImportError:
    HAS_PYCOOKIECHEAT = False

# 配置日志
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'weibo_api.log')

# 配置文件和控制台双重输出
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class WeiboAPI:
    """微博API客户端，使用H5版本的微博"""
    
    BASE_URL = "https://m.weibo.cn"
    USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
    
    def __init__(self, browser="chrome", use_mock=False, cookie_str=None):
        """
        初始化微博API客户端
        
        Args:
            browser: 浏览器类型，支持"chrome"、"firefox"、"edge"等
            use_mock: 是否使用模拟数据
            cookie_str: 直接提供cookie字符串，如果提供则优先使用
        """
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": self.USER_AGENT,
            "Accept": "application/json, text/plain, */*",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": "https://m.weibo.cn/",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty"
        })
        
        self.use_mock = use_mock
        self.browser = browser
        
        # 初始化缓存
        self._cache = {
            'groups': None,  # 分组列表缓存
            'group_timeline': {},  # 分组微博缓存，格式: {gid_page: data}
            'home_timeline': {},  # 首页微博缓存，格式: {page: data}
            'special_focus': {},  # 特别关注缓存，格式: {page: data}
            'html_parse': {},  # HTML解析结果缓存，格式: {url_params: data}
            'user_info': None,  # 用户信息缓存
        }
        self._cache_expiry = {
            'groups': 0,  # 分组列表缓存过期时间
            'group_timeline': {},  # 分组微博缓存过期时间
            'home_timeline': {},  # 首页微博缓存过期时间
            'special_focus': {},  # 特别关注缓存过期时间
            'html_parse': {},  # HTML解析结果缓存过期时间
            'user_info': 0,  # 用户信息缓存过期时间
        }
        # 缓存过期时间（秒）
        self.cache_ttl = {
            'groups': 300,  # 分组列表缓存1小时
            'timeline': 300,  # 微博时间线缓存5分钟
            'user_info': 3600,  # 用户信息缓存1小时
            'html_parse': 300,  # HTML解析结果缓存5分钟
        }
        
        # 如果提供了cookie字符串，直接使用
        if cookie_str:
            self.set_cookie_from_string(cookie_str)
            logger.info("已使用提供的cookie")
        # 否则从浏览器获取cookie
        elif not use_mock:
            self._load_cookies_from_browser(browser)
    
    def _is_cache_valid(self, cache_type, key=None):
        """检查缓存是否有效"""
        current_time = time.time()
        
        if key is None:
            # 检查没有key的缓存类型
            return (self._cache[cache_type] is not None and 
                    self._cache_expiry[cache_type] > current_time)
        else:
            # 检查有key的缓存类型
            return (key in self._cache[cache_type] and 
                    key in self._cache_expiry[cache_type] and 
                    self._cache_expiry[cache_type][key] > current_time)
    
    def _set_cache(self, cache_type, data, key=None, ttl=None):
        """设置缓存"""
        if ttl is None:
            if cache_type == 'groups' or cache_type == 'user_info':
                ttl = self.cache_ttl['groups'] if cache_type == 'groups' else self.cache_ttl['user_info']
            else:
                ttl = self.cache_ttl['timeline']
        
        current_time = time.time()
        
        if key is None:
            # 设置没有key的缓存类型
            self._cache[cache_type] = data
            self._cache_expiry[cache_type] = current_time + ttl
        else:
            # 设置有key的缓存类型
            self._cache[cache_type][key] = data
            self._cache_expiry[cache_type][key] = current_time + ttl
    
    def _get_cache(self, cache_type, key=None):
        """获取缓存"""
        if not self._is_cache_valid(cache_type, key):
            return None
        
        if key is None:
            # 获取没有key的缓存类型
            return self._cache[cache_type]
        else:
            # 获取有key的缓存类型
            return self._cache[cache_type].get(key)
    
    def _clear_cache(self, cache_type=None, key=None):
        """清除缓存"""
        if cache_type is None:
            # 清除所有缓存
            self._cache = {
                'groups': None,
                'group_timeline': {},
                'home_timeline': {},
                'special_focus': {},
                'html_parse': {},
                'user_info': None,
            }
            self._cache_expiry = {
                'groups': 0,
                'group_timeline': {},
                'home_timeline': {},
                'special_focus': {},
                'html_parse': {},
                'user_info': 0,
            }
        elif key is None:
            # 清除指定类型的所有缓存
            self._cache[cache_type] = {} if isinstance(self._cache[cache_type], dict) else None
            self._cache_expiry[cache_type] = {} if isinstance(self._cache_expiry[cache_type], dict) else 0
        else:
            # 清除指定类型和key的缓存
            if key in self._cache[cache_type]:
                del self._cache[cache_type][key]
            if key in self._cache_expiry[cache_type]:
                del self._cache_expiry[cache_type][key]

    def _parse_html_for_weibo(self, html_content):
        """解析HTML内容提取微博数据，并缓存结果"""
        soup = BeautifulSoup(html_content, 'lxml')
        
        # 尝试提取渲染数据
        scripts = soup.find_all('script')
        weibo_data = []
        
        for script in scripts:
            if script.string and "$render_data" in script.string:
                match = re.search(r'\$render_data\s*=\s*(\[.*?\])\[0\]', script.string, re.DOTALL)
                if match:
                    try:
                        data = json.loads(match.group(1))[0]
                        if 'status' in data:
                            weibo_data = data['status']
                            break
                    except json.JSONDecodeError:
                        continue
        
        return weibo_data

    def _open_browser_for_login(self):
        """打开浏览器让用户登录微博"""
        logger.info("正在打开浏览器，请登录微博...")
        
        # 根据不同操作系统和浏览器类型打开浏览器
        url = "https://m.weibo.cn/"
        browser_opened = False
        
        try:
            if self.browser.lower() == "chrome":
                logger.info("尝试打开Chrome浏览器...")
                # 尝试使用不同平台的方式打开Chrome
                if os.name == 'nt':  # Windows
                    logger.info("检测到Windows系统，使用start命令打开Chrome")
                    subprocess.Popen(['start', 'chrome', url], shell=True)
                    browser_opened = True
                elif os.name == 'posix':  # macOS or Linux
                    if os.path.exists('/Applications/Google Chrome.app'):  # macOS
                        logger.info("检测到macOS系统，使用open命令打开Chrome")
                        subprocess.Popen(['open', '-a', 'Google Chrome', url])
                        browser_opened = True
                    else:  # Linux
                        logger.info("检测到Linux系统，使用google-chrome命令打开Chrome")
                        subprocess.Popen(['google-chrome', url])
                        browser_opened = True
            elif self.browser.lower() == "firefox":
                logger.info("尝试打开Firefox浏览器...")
                if os.name == 'nt':  # Windows
                    subprocess.Popen(['start', 'firefox', url], shell=True)
                    browser_opened = True
                elif os.name == 'posix':  # macOS or Linux
                    if os.path.exists('/Applications/Firefox.app'):  # macOS
                        subprocess.Popen(['open', '-a', 'Firefox', url])
                        browser_opened = True
                    else:  # Linux
                        subprocess.Popen(['firefox', url])
                        browser_opened = True
            elif self.browser.lower() == "edge":
                logger.info("尝试打开Edge浏览器...")
                if os.name == 'nt':  # Windows
                    subprocess.Popen(['start', 'msedge', url], shell=True)
                    browser_opened = True
                elif os.name == 'posix':  # macOS
                    if os.path.exists('/Applications/Microsoft Edge.app'):
                        subprocess.Popen(['open', '-a', 'Microsoft Edge', url])
                        browser_opened = True
            elif self.browser.lower() == "safari":
                logger.info("尝试打开Safari浏览器...")
                if os.name == 'posix' and os.path.exists('/Applications/Safari.app'):  # macOS
                    subprocess.Popen(['open', '-a', 'Safari', url])
                    browser_opened = True
        except Exception as e:
            logger.error(f"打开浏览器失败: {str(e)}")
        
        # 如果特定浏览器打开失败，使用默认浏览器
        if not browser_opened:
            logger.info("使用默认浏览器打开微博登录页面")
            webbrowser.open(url)
        
        # 等待用户登录
        logger.info("请在浏览器中登录微博，然后回到终端按回车键继续...")
        input("请在浏览器中登录微博后，按回车键继续...")
        logger.info("用户已确认登录完成")
    
    def _load_cookies_from_browser(self, browser):
        """从浏览器加载微博cookie"""
        try:
            logger.info(f"尝试从{browser}浏览器获取cookie...")
            
            if browser.lower() == "chrome" and HAS_PYCOOKIECHEAT:
                logger.info("使用pycookiecheat.chrome_cookies获取cookie")
                try:
                    cookies_dict = chrome_cookies("https://m.weibo.cn")
                    logger.info(f"成功获取Chrome cookie，cookie数量: {len(cookies_dict)}")
                    
                    # 将字典形式的cookie转换为RequestsCookieJar
                    cookies = requests.cookies.RequestsCookieJar()
                    for name, value in cookies_dict.items():
                        cookies.set(name, value, domain=".weibo.cn")
                except Exception as e:
                    logger.error(f"使用pycookiecheat获取cookie失败: {str(e)}")
                    logger.info("尝试使用browser_cookie3作为备选方案")
                    cookies = browser_cookie3.chrome(domain_name=".weibo.cn")
            elif browser.lower() == "chrome":
                logger.info("使用browser_cookie3.chrome获取cookie")
                cookies = browser_cookie3.chrome(domain_name=".weibo.cn")
                logger.info(f"成功获取Chrome cookie，cookie数量: {len(list(cookies))}")
            elif browser.lower() == "firefox":
                logger.info("使用browser_cookie3.firefox获取cookie")
                cookies = browser_cookie3.firefox(domain_name=".weibo.cn")
                logger.info(f"成功获取Firefox cookie，cookie数量: {len(list(cookies))}")
            elif browser.lower() == "edge":
                logger.info("使用browser_cookie3.edge获取cookie")
                cookies = browser_cookie3.edge(domain_name=".weibo.cn")
                logger.info(f"成功获取Edge cookie，cookie数量: {len(list(cookies))}")
            elif browser.lower() == "safari":
                logger.info("使用browser_cookie3.safari获取cookie")
                cookies = browser_cookie3.safari(domain_name=".weibo.cn")
                logger.info(f"成功获取Safari cookie，cookie数量: {len(list(cookies))}")
            else:
                raise ValueError(f"不支持的浏览器类型: {browser}")
            
            # 检查是否获取到了关键cookie
            if isinstance(cookies, requests.cookies.RequestsCookieJar):
                cookie_names = [cookie.name for cookie in cookies]
            else:
                cookie_names = list(cookies.keys())
            
            logger.info(f"获取到的cookie名称: {cookie_names}")
            
            important_cookies = ['SUB', 'SUBP', 'SSOLoginState', 'XSRF-TOKEN']
            missing_cookies = [name for name in important_cookies if name not in cookie_names]
            
            if missing_cookies:
                logger.warning(f"缺少重要的cookie: {missing_cookies}")
            else:
                logger.info("所有重要的cookie都已获取")
            
            # 将cookie添加到session中
            self.session.cookies.update(cookies)
            logger.info(f"已从{browser}浏览器加载微博cookie")
            
            # 验证cookie是否有效
            if not self._verify_cookie():
                logger.warning("从浏览器加载的cookie无效或已过期")
                # 打开浏览器让用户登录
                self._open_browser_for_login()
                # 重新尝试获取cookie
                return self._load_cookies_from_browser(browser)
            
        except Exception as e:
            logger.error(f"从{browser}浏览器加载cookie失败: {str(e)}")
            logger.info("请确保您已在浏览器中登录微博")
            
            # 打开浏览器让用户登录
            self._open_browser_for_login()
            
            # 重新尝试获取cookie
            try:
                logger.info(f"重新尝试从{browser}浏览器获取cookie...")
                
                if browser.lower() == "chrome" and HAS_PYCOOKIECHEAT:
                    try:
                        cookies_dict = chrome_cookies("https://m.weibo.cn")
                        cookies = requests.cookies.RequestsCookieJar()
                        for name, value in cookies_dict.items():
                            cookies.set(name, value, domain=".weibo.cn")
                    except Exception:
                        cookies = browser_cookie3.chrome(domain_name=".weibo.cn")
                elif browser.lower() == "chrome":
                    cookies = browser_cookie3.chrome(domain_name=".weibo.cn")
                elif browser.lower() == "firefox":
                    cookies = browser_cookie3.firefox(domain_name=".weibo.cn")
                elif browser.lower() == "edge":
                    cookies = browser_cookie3.edge(domain_name=".weibo.cn")
                elif browser.lower() == "safari":
                    cookies = browser_cookie3.safari(domain_name=".weibo.cn")
                else:
                    raise ValueError(f"不支持的浏览器类型: {browser}")
                
                # 检查是否获取到了关键cookie
                if isinstance(cookies, requests.cookies.RequestsCookieJar):
                    cookie_names = [cookie.name for cookie in cookies]
                else:
                    cookie_names = list(cookies.keys())
                
                logger.info(f"重新获取到的cookie名称: {cookie_names}")
                
                # 将cookie添加到session中
                self.session.cookies.update(cookies)
                logger.info(f"已从{browser}浏览器重新加载微博cookie")
                
                # 验证cookie是否有效
                if not self._verify_cookie():
                    logger.warning("重新加载的cookie仍然无效")
                    self.use_mock = True
                    logger.info("已切换到模拟数据模式")
            except Exception as e:
                logger.error(f"重新加载cookie失败: {str(e)}")
                self.use_mock = True
                logger.info("已切换到模拟数据模式")
    
    def _verify_cookie(self):
        """验证cookie是否有效"""
        try:
            # 尝试获取用户信息，如果成功则cookie有效
            url = f"{self.BASE_URL}/api/config/list"
            logger.info(f"正在验证cookie有效性，请求URL: {url}")
            
            response = self.session.get(url, timeout=5)
            logger.info(f"验证cookie响应状态码: {response.status_code}")
            
            if response.status_code != 200:
                logger.warning(f"验证cookie请求失败，状态码: {response.status_code}")
                return False
            
            try:
                data = response.json()
                logger.info(f"验证cookie响应JSON: {data}")
                
                if data.get('ok') == 1:
                    logger.info("cookie验证成功")
                    return True
                else:
                    logger.warning(f"cookie验证失败，响应ok值不为1: {data.get('ok')}")
                    return False
            except json.JSONDecodeError:
                logger.warning(f"cookie验证失败，无法解析JSON响应: {response.text[:100]}...")
                return False
        except Exception as e:
            logger.error(f"cookie验证过程中发生错误: {str(e)}")
            return False
    
    def set_cookie_from_string(self, cookie_str):
        """从字符串设置cookie"""
        try:
            # 解析cookie字符串
            cookies = {}
            for item in cookie_str.split(';'):
                item = item.strip()
                if not item:
                    continue
                if '=' in item:
                    key, value = item.split('=', 1)
                    cookies[key] = value
            
            # 设置cookie
            for key, value in cookies.items():
                self.session.cookies.set(key, value, domain=".weibo.cn")
            
            # 设置XSRF-TOKEN到请求头
            if 'XSRF-TOKEN' in cookies:
                self.session.headers.update({
                    "X-XSRF-TOKEN": cookies['XSRF-TOKEN']
                })
            
            logger.info("成功设置cookie")
            return True
        except Exception as e:
            logger.error(f"设置cookie失败: {str(e)}")
            self.use_mock = True
            logger.info("已切换到模拟数据模式")
            return False
    
    def get_home_timeline(self, page=1) -> List[Dict[str, Any]]:
        """
        获取首页微博（关注的人发布的微博）
        
        Args:
            page: 页码，从1开始
            
        Returns:
            微博列表
        """
        # 如果使用模拟数据，直接返回模拟数据
        if self.use_mock:
            return self._generate_mock_weibo(10)
        
        # 检查缓存
        cache_key = f"page_{page}"
        cached_data = self._get_cache('home_timeline', cache_key)
        if cached_data is not None:
            logger.info(f"使用缓存的首页微博数据，页码: {page}")
            return cached_data
        
        # 添加页码参数
        url = f"{self.BASE_URL}/feed/friends"
        params = {"page": page}
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            # 尝试解析JSON响应
            try:
                data = response.json()
                if 'data' in data and 'statuses' in data['data']:
                    result = data['data']['statuses']
                    # 缓存结果
                    self._set_cache('home_timeline', result, cache_key)
                    return result
            except json.JSONDecodeError:
                pass
            
            # 生成HTML解析缓存键
            html_cache_key = f"{url}_{urlencode(params)}"
            parsed_html = self._get_cache('html_parse', html_cache_key)
            
            if parsed_html is None:
                # 如果JSON解析失败，尝试解析HTML
                parsed_html = self._parse_html_for_weibo(response.text)
                # 缓存HTML解析结果
                self._set_cache('html_parse', parsed_html, html_cache_key, self.cache_ttl['html_parse'])
            
            # 缓存结果
            self._set_cache('home_timeline', parsed_html, cache_key)
            return parsed_html
        except Exception as e:
            logger.error(f"获取首页微博失败: {str(e)}")
            # 如果获取失败，返回模拟数据
            return self._generate_mock_weibo(10)
    
    def get_special_focus(self, page=1) -> List[Dict[str, Any]]:
        """
        获取特别关注的微博
        
        Args:
            page: 页码，从1开始
            
        Returns:
            特别关注的微博列表
        """
        # 如果使用模拟数据，直接返回模拟数据
        if self.use_mock:
            return self._generate_mock_weibo(5)
        
        # 检查缓存
        cache_key = f"page_{page}"
        cached_data = self._get_cache('special_focus', cache_key)
        if cached_data is not None:
            logger.info(f"使用缓存的特别关注微博数据，页码: {page}")
            return cached_data
        
        # 先获取用户的分组列表
        groups = self.get_groups()
        special_focus_group = None
        
        # 查找名为"特别关注"的分组
        for group in groups:
            if group.get("name") == "特别关注":
                special_focus_group = group
                break
        
        # 如果找到了特别关注分组，使用其ID；否则使用默认ID
        if special_focus_group:
            gid = special_focus_group.get("gid")
            logger.info(f"找到特别关注分组，ID: {gid}")
        else:
            logger.warning("未找到特别关注分组，将使用默认分组")
            # 如果没有找到特别关注分组，返回模拟数据
            return self._generate_mock_weibo(5)
        
        # 使用分组ID获取微博
        return self.get_group_timeline(gid, page)
    
    def get_user_info(self) -> Optional[Dict[str, Any]]:
        """
        获取当前登录用户信息
        
        Returns:
            用户信息字典，如果获取失败则返回None
        """
        # 如果使用模拟数据，直接返回模拟数据
        if self.use_mock:
            return self._generate_mock_user()
        
        # 检查缓存
        cached_data = self._get_cache('user_info')
        if cached_data is not None:
            logger.info("使用缓存的用户信息数据")
            return cached_data
        
        # 尝试从首页获取用户信息
        url = f"{self.BASE_URL}/api/config"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            # 解析JSON响应
            data = response.json()
            if 'data' in data and 'login' in data['data'] and data['data']['login']:
                # 如果已登录，获取用户详细信息
                uid = data['data'].get('uid', '')
                if uid:
                    user_url = f"{self.BASE_URL}/api/container/getIndex?containerid=230283{uid}_-_INFO"
                    user_response = self.session.get(user_url)
                    user_response.raise_for_status()
                    user_data = user_response.json()
                    
                    # 提取用户信息
                    if 'data' in user_data and 'cards' in user_data['data']:
                        user_info = {}
                        for card in user_data['data']['cards']:
                            if 'card_group' in card:
                                for item in card['card_group']:
                                    if 'item_name' in item and 'item_content' in item:
                                        user_info[item['item_name']] = item['item_content']
                        
                        # 构建用户信息
                        result = {
                            "screen_name": user_info.get('昵称', '未知用户'),
                            "description": user_info.get('简介', '暂无简介'),
                            "followers_count": self._extract_number(user_info.get('粉丝', '0')),
                            "follow_count": self._extract_number(user_info.get('关注', '0')),
                            "statuses_count": self._extract_number(user_info.get('微博', '0')),
                            "verified": True if '认证' in user_info else False,
                            "verified_type": 0
                        }
                        # 缓存结果
                        self._set_cache('user_info', result)
                        return result
            
            # 如果无法获取详细信息，尝试从配置中获取基本信息
            if 'data' in data and 'login' in data['data'] and data['data']['login']:
                result = {
                    "screen_name": data['data'].get('nick', '未知用户'),
                    "description": "暂无简介",
                    "followers_count": 0,
                    "follow_count": 0,
                    "statuses_count": 0,
                    "verified": False,
                    "verified_type": -1
                }
                # 缓存结果
                self._set_cache('user_info', result)
                return result
            
            # 如果未登录，返回模拟数据
            logger.error("未登录微博")
            return self._generate_mock_user()
        except Exception as e:
            logger.error(f"获取用户信息失败: {str(e)}")
            # 如果获取失败，返回模拟数据
            return self._generate_mock_user()
    
    def _extract_number(self, text):
        """从文本中提取数字"""
        import re
        match = re.search(r'(\d+(\.\d+)?)', text)
        if match:
            num = match.group(1)
            if '万' in text:
                return int(float(num) * 10000)
            elif '亿' in text:
                return int(float(num) * 100000000)
            else:
                return int(float(num))
        return 0
    
    def get_groups(self) -> List[Dict[str, Any]]:
        """
        获取用户的分组列表
        
        Returns:
            分组列表，每个分组包含gid和name
        """
        # 如果使用模拟数据，直接返回模拟数据
        if self.use_mock:
            return [
                {"gid": "xxxxxxxxxxxxxxxxxx", "name": "特别关注"},
                {"gid": "xxxxxxxxxxxxxxxxxx", "name": "名人明星"},
                {"gid": "xxxxxxxxxxxxxxxxxx", "name": "同事"},
                {"gid": "xxxxxxxxxxxxxxxxxx", "name": "同学"}
            ]
        
        # 检查缓存
        cached_data = self._get_cache('groups')
        if cached_data is not None:
            logger.info("使用缓存的分组列表数据")
            return cached_data
        
        url = f"{self.BASE_URL}/api/config/list"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            # 解析JSON响应
            data = response.json()
            if data.get('ok') == 1 and 'data' in data and 'groups' in data['data']:
                result = data['data']['groups']
                # 缓存结果
                self._set_cache('groups', result)
                return result
            
            return []
        except Exception as e:
            logger.error(f"获取分组列表失败: {str(e)}")
            # 如果获取失败，返回模拟数据
            mock_data = [
                {"gid": "xxxxxxxxxxxxxxxxxx", "name": "特别关注"},
                {"gid": "xxxxxxxxxxxxxxxxxx", "name": "名人明星"},
                {"gid": "xxxxxxxxxxxxxxxxxx", "name": "同事"},
                {"gid": "xxxxxxxxxxxxxxxxxx", "name": "同学"}
            ]
            return mock_data
    
    def get_group_timeline(self, gid: str, page=1) -> List[Dict[str, Any]]:
        """
        获取指定分组的微博
        
        Args:
            gid: 分组ID
            page: 页码，从1开始
            
        Returns:
            分组微博列表
        """
        # 如果使用模拟数据，直接返回模拟数据
        if self.use_mock:
            return self._generate_mock_weibo(5)
        
        # 检查缓存
        cache_key = f"{gid}_page_{page}"
        cached_data = self._get_cache('group_timeline', cache_key)
        if cached_data is not None:
            logger.info(f"使用缓存的分组微博数据，分组ID: {gid}, 页码: {page}")
            return cached_data
        
        # 使用分组ID获取微博
        url = f"{self.BASE_URL}/feed/group"
        params = {"gid": gid, "page": page}
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            # 尝试解析JSON响应
            try:
                data = response.json()
                if 'data' in data and 'statuses' in data['data']:
                    result = data['data']['statuses']
                    # 缓存结果
                    self._set_cache('group_timeline', result, cache_key)
                    # 如果是特别关注分组，也缓存到special_focus
                    for group in self.get_groups():
                        if group.get("gid") == gid and group.get("name") == "特别关注":
                            self._set_cache('special_focus', result, f"page_{page}")
                            break
                    return result
            except json.JSONDecodeError:
                pass
            
            # 生成HTML解析缓存键
            html_cache_key = f"{url}_{urlencode(params)}"
            parsed_html = self._get_cache('html_parse', html_cache_key)
            
            if parsed_html is None:
                # 如果JSON解析失败，尝试解析HTML
                parsed_html = self._parse_html_for_weibo(response.text)
                # 缓存HTML解析结果
                self._set_cache('html_parse', parsed_html, html_cache_key, self.cache_ttl['html_parse'])
            
            # 缓存结果
            self._set_cache('group_timeline', parsed_html, cache_key)
            # 如果是特别关注分组，也缓存到special_focus
            for group in self.get_groups():
                if group.get("gid") == gid and group.get("name") == "特别关注":
                    self._set_cache('special_focus', parsed_html, f"page_{page}")
                    break
            return parsed_html
        except Exception as e:
            logger.error(f"获取分组微博失败: {str(e)}")
            # 如果获取失败，返回模拟数据
            return self._generate_mock_weibo(5) 
    
    def _generate_mock_weibo(self, count=10) -> List[Dict[str, Any]]:
        """生成模拟微博数据"""
        mock_weibos = []
        
        # 模拟用户
        users = [
            {"screen_name": "微博用户1", "verified": True, "verified_type": 0},
            {"screen_name": "微博用户2", "verified": False, "verified_type": -1},
            {"screen_name": "微博官方", "verified": True, "verified_type": 1},
            {"screen_name": "科技博主", "verified": True, "verified_type": 0},
            {"screen_name": "娱乐博主", "verified": True, "verified_type": 2}
        ]
        
        # 模拟微博内容
        contents = [
            "今天天气真好，出去走走吧！#日常生活#",
            "分享一篇好文章：《如何提高工作效率》，推荐阅读！",
            "新电影《模拟人生》今天上映了，有没有一起去看的？",
            "刚刚发布了新版本，修复了一些bug，欢迎更新！#技术分享#",
            "美食推荐：今天去了一家新开的餐厅，味道不错，推荐给大家！[美食]",
            "今天是个特别的日子，祝所有人节日快乐！",
            "分享一个小技巧：如何快速学习一门新语言 #学习方法#",
            "刚刚看完一本好书，强烈推荐！#读书分享#",
            "新的一天，新的开始，加油！",
            "谢谢大家的支持，我们会继续努力！"
        ]
        
        # 生成模拟微博
        for i in range(count):
            # 随机选择用户和内容
            user = random.choice(users)
            content = random.choice(contents)
            
            # 生成随机时间（过去7天内）
            days_ago = random.randint(0, 7)
            hours_ago = random.randint(0, 23)
            minutes_ago = random.randint(0, 59)
            created_at = (datetime.datetime.now() - datetime.timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)).strftime("%a %b %d %H:%M:%S +0800 %Y")
            
            # 随机生成评论、点赞和转发数
            comments_count = random.randint(0, 1000)
            attitudes_count = random.randint(0, 5000)
            reposts_count = random.randint(0, 500)
            
            # 随机决定是否有图片
            has_pics = random.choice([True, False])
            pics = []
            if has_pics:
                pic_count = random.randint(1, 9)
                for j in range(pic_count):
                    pics.append({"url": f"https://example.com/pic{j}.jpg"})
            
            # 随机决定是否有视频
            has_video = random.choice([True, False]) if not has_pics else False
            page_info = {}
            if has_video:
                page_info = {
                    "media_info": {
                        "duration": random.randint(10, 300)
                    }
                }
            
            # 随机决定是否是转发微博
            is_retweet = random.choice([True, False])
            retweeted_status = None
            if is_retweet:
                retweeted_user = random.choice(users)
                retweeted_content = random.choice(contents)
                retweeted_status = {
                    "user": retweeted_user,
                    "text": retweeted_content,
                    "created_at": (datetime.datetime.now() - datetime.timedelta(days=days_ago+1)).strftime("%a %b %d %H:%M:%S +0800 %Y")
                }
            
            # 构建微博对象
            weibo = {
                "user": user,
                "text": content,
                "created_at": created_at,
                "comments_count": comments_count,
                "attitudes_count": attitudes_count,
                "reposts_count": reposts_count,
                "pics": pics,
                "page_info": page_info,
                "retweeted_status": retweeted_status
            }
            
            mock_weibos.append(weibo)
        
        return mock_weibos
    
    def _generate_mock_user(self) -> Dict[str, Any]:
        """生成模拟用户数据"""
        return {
            "screen_name": "模拟用户",
            "description": "这是一个模拟用户，用于演示HyperWeibo的功能",
            "followers_count": random.randint(100, 10000),
            "follow_count": random.randint(50, 500),
            "statuses_count": random.randint(100, 1000),
            "verified": True,
            "verified_type": 0
        }