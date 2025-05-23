"""
MCP Layout Driver 配置文件

用于管理API端点、超时时间等配置项
"""

import os
from typing import Dict, Any

# API配置
class APIConfig:
    """API配置类"""
    
    # 基础URL，可通过环境变量覆盖
    BASE_URL = os.getenv("LAYOUT_DRIVER_API_URL", "http://127.0.0.1:23456")
    
    # 默认超时时间（秒）
    DEFAULT_TIMEOUT = int(os.getenv("LAYOUT_DRIVER_TIMEOUT", "30"))
    
    # API端点配置
    ENDPOINTS = {
        # 窗口管理相关
        "WINDOWS_LIST": "/windows",              # GET - 获取窗口列表
        "WINDOWS_CLOSE_BATCH": "/windows/close", # POST - 批量关闭窗口
        "WINDOWS_MINIMIZE_BATCH": "/windows/minimize", # POST - 批量最小化窗口
        "WINDOWS_MAXIMIZE_BATCH": "/windows/maximize", # POST - 批量最大化窗口
        "WINDOWS_RESTORE_BATCH": "/windows/restore", # POST - 批量还原窗口
        "WINDOWS_OPACITY_BATCH": "/windows/opacity", # POST - 批量设置窗口透明度
    }
    
    # 默认请求头
    DEFAULT_HEADERS = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "MCP-Layout-Driver/1.0"
    }
    
    @classmethod
    def get_endpoint_url(cls, endpoint_key: str, **kwargs) -> str:
        """获取完整的端点URL
        
        Args:
            endpoint_key: 端点键名
            **kwargs: 用于格式化URL的参数（如handle, pid等）
            
        Returns:
            完整的API URL
            
        Example:
            >>> APIConfig.get_endpoint_url("WINDOW_INFO", handle=12345)
            'http://localhost:8080/api/windows/12345'
        """
        endpoint = cls.ENDPOINTS.get(endpoint_key)
        if not endpoint:
            raise ValueError(f"未知的API端点: {endpoint_key}")
        
        # 格式化端点路径
        if kwargs:
            endpoint = endpoint.format(**kwargs)
            
        return f"{cls.BASE_URL}{endpoint}"
    
    @classmethod
    def get_headers(cls, additional_headers: Dict[str, str] = None) -> Dict[str, str]:
        """获取请求头
        
        Args:
            additional_headers: 额外的请求头
            
        Returns:
            合并后的请求头
        """
        headers = cls.DEFAULT_HEADERS.copy()
        if additional_headers:
            headers.update(additional_headers)
        return headers


# 日志配置
class LogConfig:
    """日志配置类"""
    
    LEVEL = os.getenv("LAYOUT_DRIVER_LOG_LEVEL", "INFO")
    FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # 是否启用详细日志
    VERBOSE = os.getenv("LAYOUT_DRIVER_VERBOSE", "false").lower() == "true"


# 安全配置
class SecurityConfig:
    """安全配置类"""
    
    # 是否验证SSL证书
    VERIFY_SSL = os.getenv("LAYOUT_DRIVER_VERIFY_SSL", "true").lower() == "true"
    
    # API认证Token（如果需要）
    AUTH_TOKEN = os.getenv("LAYOUT_DRIVER_AUTH_TOKEN", "")
    
    # 允许的最大重试次数
    MAX_RETRIES = int(os.getenv("LAYOUT_DRIVER_MAX_RETRIES", "3")) 