import logging
import json
from mcp.server.stdio import stdio_server
from mcp.server import Server
from mcp.types import (
    TextContent,
    Tool,
)
from enum import Enum
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import httpx
import asyncio

# 导入配置
from .config import APIConfig, SecurityConfig, LogConfig

class GetWindowList(BaseModel):
    """获取当前桌面已打开窗口列表
    
    入参：无需参数
    出参：窗口信息列表，每个窗口包含以下字段：
    - handle: 窗口句柄
    - title: 窗口标题
    - width: 窗口宽度
    - height: 窗口高度
    - x: 窗口X坐标
    - y: 窗口Y坐标
    - icon: 窗口图标数据（可空）
    - alias: 窗口别名（可空）
    """
    pass

class WindowInfo(BaseModel):
    """窗口信息模型"""
    handle: int
    title: str
    width: int
    height: int
    x: int
    y: int
    icon: Optional[str] = None
    alias: Optional[str] = None

class CloseWindowRequest(BaseModel):
    """批量关闭窗口请求模型
    
    入参：
    - handle: 窗口句柄（必填）
    - title: 窗口标题（必填）
    - width: 窗口宽度（必填）
    - height: 窗口高度（必填）
    - x: 窗口X坐标（必填）
    - y: 窗口Y坐标（必填）
    - icon: 窗口图标数据，base64编码（可空）
    - alias: 窗口别名（可空）
    
    出参：
    - success: 操作是否成功
    - message: 操作结果消息
    - closed_count: 成功关闭的窗口数量
    """
    handle: int
    title: str
    width: int
    height: int
    x: int
    y: int
    icon: Optional[str] = None
    alias: Optional[str] = None

class MinimizeWindowRequest(BaseModel):
    """批量最小化窗口请求模型
    
    入参：
    - handle: 窗口句柄（必填）
    - title: 窗口标题（必填）
    - width: 窗口宽度（必填）
    - height: 窗口高度（必填）
    - x: 窗口X坐标（必填）
    - y: 窗口Y坐标（必填）
    - icon: 窗口图标数据，base64编码（可空）
    - alias: 窗口别名（可空）
    
    出参：
    - success: 操作是否成功
    - message: 操作结果消息
    - minimized_count: 成功最小化的窗口数量
    """
    handle: int
    title: str
    width: int
    height: int
    x: int
    y: int
    icon: Optional[str] = None
    alias: Optional[str] = None

class MaximizeWindowRequest(BaseModel):
    """批量最大化窗口请求模型
    
    入参：
    - handle: 窗口句柄（必填）
    - title: 窗口标题（必填）
    - width: 窗口宽度（必填）
    - height: 窗口高度（必填）
    - x: 窗口X坐标（必填）
    - y: 窗口Y坐标（必填）
    - icon: 窗口图标数据，base64编码（可空）
    - alias: 窗口别名（可空）
    
    出参：
    - success: 操作是否成功
    - message: 操作结果消息
    - maximized_count: 成功最大化的窗口数量
    """
    handle: int
    title: str
    width: int
    height: int
    x: int
    y: int
    icon: Optional[str] = None
    alias: Optional[str] = None

class RestoreWindowRequest(BaseModel):
    """批量还原窗口请求模型
    
    入参：
    - handle: 窗口句柄（必填）
    - title: 窗口标题（必填）
    - width: 窗口宽度（必填）
    - height: 窗口高度（必填）
    - x: 窗口X坐标（必填）
    - y: 窗口Y坐标（必填）
    - icon: 窗口图标数据，base64编码（可空）
    - alias: 窗口别名（可空）
    
    出参：
    - success: 操作是否成功
    - message: 操作结果消息
    - restored_count: 成功还原的窗口数量
    """
    handle: int
    title: str
    width: int
    height: int
    x: int
    y: int
    icon: Optional[str] = None
    alias: Optional[str] = None

class WindowOpacityItem(BaseModel):
    """窗口透明度设置项模型"""
    window: WindowInfo
    opacity: int

class SetWindowOpacityRequest(BaseModel):
    """批量设置窗口透明度请求模型
    
    入参：
    - windows: 窗口透明度设置列表，每个项目包含：
      - window: 窗口信息对象
        - handle: 窗口句柄（必填）
        - title: 窗口标题（必填）
        - width: 窗口宽度（必填）
        - height: 窗口高度（必填）
        - x: 窗口X坐标（必填）
        - y: 窗口Y坐标（必填）
        - icon: 窗口图标数据，base64编码（可空）
        - alias: 窗口别名（可空）
      - opacity: 透明度值（0-255，0为完全透明，255为完全不透明）
        
    出参：
    - success: 操作是否成功
    - message: 操作结果消息
    - updated_count: 成功设置透明度的窗口数量
    """
    windows: List[WindowOpacityItem]


class DriverTools(str, Enum):
    GET_WINDOW_LIST = "get_window_list"
    CLOSE_WINDOWS_BATCH = "close_windows_batch"
    MINIMIZE_WINDOWS_BATCH = "minimize_windows_batch"
    MAXIMIZE_WINDOWS_BATCH = "maximize_windows_batch"
    RESTORE_WINDOWS_BATCH = "restore_windows_batch"
    SET_WINDOW_OPACITY_BATCH = "set_window_opacity_batch"


async def make_api_request(endpoint_key: str, method: str = "GET", 
                          data: Optional[Dict] = None,
                          params: Optional[Dict] = None,
                          additional_headers: Optional[Dict] = None,
                          timeout: Optional[int] = None,
                          **url_kwargs) -> Dict[str, Any]:
    """通用API请求函数
    
    这是整个MCP Layout Driver系统的核心HTTP请求函数，负责与后端API进行通信。
    该函数封装了所有的网络请求逻辑，包括认证、错误处理、日志记录等功能。
    
    ## 业务逻辑说明：
    1. 根据endpoint_key从配置中获取完整的API URL
    2. 设置请求头，包括Content-Type、认证Token等
    3. 根据HTTP方法发送相应的请求
    4. 处理各种错误情况（超时、网络错误、HTTP状态码错误等）
    5. 记录详细的请求和响应日志（如果启用verbose模式）
    6. 返回统一格式的响应结果
    
    ## 入参详细说明：
        endpoint_key (str): API端点键名，必须是APIConfig.ENDPOINTS中定义的键
            有效值包括：
            - "WINDOWS_LIST": 获取窗口列表
            - "WINDOWS_CLOSE_BATCH": 批量关闭窗口
            - "WINDOWS_MINIMIZE_BATCH": 批量最小化窗口
            - "WINDOWS_MAXIMIZE_BATCH": 批量最大化窗口
            - "WINDOWS_RESTORE_BATCH": 批量还原窗口
            - "WINDOWS_OPACITY_BATCH": 批量设置窗口透明度
            
        method (str, optional): HTTP请求方法，默认为"GET"
            支持的方法：
            - "GET": 用于获取数据（如获取窗口列表）
            - "POST": 用于创建或操作数据（如批量操作窗口）
            - "PUT": 用于更新数据
            - "DELETE": 用于删除数据
            
        data (Optional[Dict], optional): 请求体数据，默认为None
            - 对于GET请求通常为None
            - 对于POST/PUT请求包含要发送的JSON数据
            - 数据会自动序列化为JSON格式
            
        params (Optional[Dict], optional): URL查询参数，默认为None
            - 会被添加到URL后面作为?key=value&key2=value2格式
            - 常用于分页、过滤等功能
            
        additional_headers (Optional[Dict], optional): 额外的HTTP请求头，默认为None
            - 会与默认请求头合并
            - 可用于添加自定义认证头、内容类型等
            
        timeout (Optional[int], optional): 请求超时时间（秒），默认为None
            - 如果为None，使用APIConfig.DEFAULT_TIMEOUT
            - 超时会触发httpx.TimeoutException异常
            
        **url_kwargs: 用于格式化URL的关键字参数
            - 用于替换URL模板中的占位符，如{handle}、{pid}等
            - 例如：handle=12345会将/windows/{handle}格式化为/windows/12345
    
    ## 出参详细说明：
        返回 Dict[str, Any] 包含以下字段：
        
        ### 成功响应格式：
        {
            "success": True,                    # 请求是否成功的布尔标志
            "status_code": 200,                 # HTTP状态码（200表示成功）
            "content": {...},                   # API返回的实际数据内容
            "headers": {...},                   # HTTP响应头字典
            "url": "http://..."                 # 实际请求的完整URL
        }
        
        ### 失败响应格式：
        {
            "success": False,                   # 请求失败的布尔标志
            "error": "错误描述信息",              # 详细的错误描述
            "status_code": 400,                 # HTTP状态码（4xx或5xx表示错误）
            "content": "原始错误响应",            # 服务器返回的原始错误内容
            "url": "http://..."                 # 实际请求的完整URL
        }
        
        ### 网络错误响应格式：
        {
            "success": False,                   # 请求失败的布尔标志
            "error": "网络连接失败",              # 网络层面的错误描述
            "status_code": 0,                   # 状态码为0表示网络层错误
            "url": "http://..."                 # 尝试请求的URL
        }
    
    ## 错误处理机制：
    1. **超时错误 (TimeoutException)**：
       - 当请求超过指定时间未响应时触发
       - 返回status_code=0和详细的超时错误信息
       
    2. **网络连接错误 (RequestError)**：
       - 当无法建立网络连接时触发（如DNS解析失败、连接拒绝等）
       - 返回status_code=0和网络错误信息
       
    3. **HTTP状态码错误 (4xx/5xx)**：
       - 当服务器返回错误状态码时触发
       - 保留原始状态码和响应内容，便于调试
       
    4. **JSON解析错误**：
       - 当服务器返回的不是有效JSON时，回退到原始文本
       - 不会导致函数失败，确保兼容性
    
    ## 安全特性：
    1. **SSL证书验证**：根据SecurityConfig.VERIFY_SSL配置决定是否验证SSL证书
    2. **认证Token**：自动添加Bearer Token（如果配置了AUTH_TOKEN）
    3. **请求头安全**：设置标准的安全请求头
    
    ## 使用示例：
        >>> # 基础GET请求
        >>> result = await make_api_request("WINDOWS_LIST")
        
        >>> # 带参数的GET请求
        >>> result = await make_api_request(
        ...     "WINDOWS_LIST",
        ...     params={"filter": "visible", "limit": 10}
        ... )
        
        >>> # POST请求发送数据
        >>> result = await make_api_request(
        ...     "WINDOWS_CLOSE_BATCH",
        ...     method="POST",
        ...     data={
        ...         "handle": 12345,
        ...         "title": "测试窗口"
        ...     }
        ... )
        
        >>> # 带URL参数的请求
        >>> result = await make_api_request(
        ...     "WINDOW_INFO",
        ...     handle=12345
        ... )
        
        >>> # 自定义超时和请求头
        >>> result = await make_api_request(
        ...     "WINDOWS_LIST",
        ...     additional_headers={"Custom-Header": "value"},
        ...     timeout=60
        ... )
    
    ## 注意事项：
    1. 此函数是异步函数，必须在异步上下文中调用
    2. 所有网络错误都会被捕获并转换为统一的错误格式
    3. 启用verbose日志时会记录详细的请求和响应信息
    4. 函数会自动处理JSON序列化和反序列化
    5. 认证Token会自动添加，无需手动设置
    """
    try:
        # 步骤1: 构建完整的API URL
        # 从配置中获取端点模板，并使用url_kwargs进行格式化
        url = APIConfig.get_endpoint_url(endpoint_key, **url_kwargs)
        
        # 步骤2: 设置HTTP请求头
        # 获取默认请求头并合并额外的请求头
        headers = APIConfig.get_headers(additional_headers)
        
        # 步骤3: 添加认证Token（如果配置了）
        # 使用Bearer Token格式进行API认证
        if SecurityConfig.AUTH_TOKEN:
            headers["Authorization"] = f"Bearer {SecurityConfig.AUTH_TOKEN}"
        
        # 步骤4: 设置请求超时时间
        # 如果未指定，使用配置文件中的默认值
        if timeout is None:
            timeout = APIConfig.DEFAULT_TIMEOUT
        
        # 步骤5: 记录请求日志（调试用）
        # 在verbose模式下记录详细的请求信息
        if LogConfig.VERBOSE:
            logging.info(f"API请求: {method} {url}")
            if data:
                logging.debug(f"请求数据: {json.dumps(data, ensure_ascii=False)}")
        
        # 步骤6: 创建HTTP客户端并发送请求
        # 使用httpx异步客户端，支持SSL验证配置
        async with httpx.AsyncClient(verify=SecurityConfig.VERIFY_SSL) as client:
            # 根据HTTP方法分别处理不同类型的请求
            if method.upper() == "GET":
                # GET请求：主要用于获取数据，参数通过URL查询参数传递
                response = await client.get(
                    url=url,
                    params=params,
                    headers=headers,
                    timeout=timeout
                )
            elif method.upper() == "POST":
                # POST请求：主要用于创建或操作数据，数据通过请求体传递
                response = await client.post(
                    url=url,
                    json=data,  # 自动序列化为JSON
                    params=params,
                    headers=headers,
                    timeout=timeout
                )
            elif method.upper() == "PUT":
                # PUT请求：主要用于更新数据
                response = await client.put(
                    url=url,
                    json=data,
                    params=params,
                    headers=headers,
                    timeout=timeout
                )
            elif method.upper() == "DELETE":
                # DELETE请求：主要用于删除数据
                response = await client.delete(
                    url=url,
                    params=params,
                    headers=headers,
                    timeout=timeout
                )
            else:
                # 不支持的HTTP方法，抛出异常
                raise ValueError(f"不支持的HTTP方法: {method}")
            
            # 步骤7: 记录响应日志
            if LogConfig.VERBOSE:
                logging.info(f"API响应: {response.status_code}")
            
            # 步骤8: 检查HTTP状态码
            # 4xx和5xx状态码表示请求失败
            if response.status_code >= 400:
                error_msg = f"API请求失败，状态码: {response.status_code}"
                if LogConfig.VERBOSE:
                    logging.error(f"{error_msg}, 响应内容: {response.text}")
                return {
                    "success": False,
                    "error": error_msg,
                    "status_code": response.status_code,
                    "content": response.text,
                    "url": url
                }
            
            # 步骤9: 解析响应内容
            # 尝试解析JSON，如果失败则使用原始文本
            try:
                content = response.json()
            except:
                # JSON解析失败，可能是非JSON响应
                content = response.text
                
            # 步骤10: 返回成功响应
            return {
                "success": True,
                "status_code": response.status_code,
                "content": content,
                "headers": dict(response.headers),
                "url": url
            }
            
    except httpx.TimeoutException:
        # 处理请求超时异常
        error_msg = f"API请求超时，超过 {timeout} 秒"
        logging.error(error_msg)
        return {
            "success": False,
            "error": error_msg,
            "status_code": 0,
            "url": APIConfig.get_endpoint_url(endpoint_key, **url_kwargs)
        }
    except httpx.RequestError as e:
        # 处理网络连接异常（DNS解析失败、连接拒绝等）
        error_msg = f"API请求错误: {str(e)}"
        logging.error(error_msg)
        return {
            "success": False,
            "error": error_msg,
            "status_code": 0,
            "url": APIConfig.get_endpoint_url(endpoint_key, **url_kwargs)
        }
    except Exception as e:
        # 处理其他未预期的异常
        error_msg = f"未知错误: {str(e)}"
        logging.error(error_msg)
        return {
            "success": False,
            "error": error_msg,
            "status_code": 0,
            "url": APIConfig.get_endpoint_url(endpoint_key, **url_kwargs) if endpoint_key in APIConfig.ENDPOINTS else "unknown"
        }


async def get_window_list() -> Dict[str, Any]:
    """获取当前桌面已打开窗口列表
    
    通过调用后端API接口获取窗口信息。
    
    入参：
        无需参数
        
    出参：
        Dict[str, Any]: API响应结果，包含：
        - success (bool): 请求是否成功
        - content (list): 窗口信息列表，每个窗口包含：
          - handle (int): 窗口句柄，唯一标识符
          - title (str): 窗口标题
          - width (int): 窗口宽度（像素）
          - height (int): 窗口高度（像素）
          - x (int): 窗口左上角X坐标
          - y (int): 窗口左上角Y坐标
          - icon (str, optional): 窗口图标，base64编码的PNG数据，可为空
          - alias (str, optional): 窗口别名，可为空
        - error (str, optional): 错误信息（如果有）
        
    API端点: GET /windows
        
    Example:
        >>> result = await get_window_list()
        >>> if result["success"]:
        ...     windows = result["content"]
        ...     print(f"找到 {len(windows)} 个窗口")
        ...     for window in windows:
        ...         print(f"  - {window['title']} ({window['width']}x{window['height']})")
        >>> else:
        ...     print(f"获取窗口列表失败: {result['error']}")
    """
    return await make_api_request("WINDOWS_LIST", method="GET")

async def close_windows_batch(handle: int, title: str, width: int, height: int, 
                             x: int, y: int, icon: Optional[str] = None, 
                             alias: Optional[str] = None) -> Dict[str, Any]:
    """批量关闭窗口
    
    通过调用后端API接口批量关闭指定的窗口。
    
    入参：
        handle (int): 窗口句柄，用于唯一标识窗口
        title (str): 窗口标题
        width (int): 窗口宽度（像素）
        height (int): 窗口高度（像素）
        x (int): 窗口左上角X坐标
        y (int): 窗口左上角Y坐标
        icon (str, optional): 窗口图标，base64编码的PNG数据，默认None
        alias (str, optional): 窗口别名，默认None
        
    出参：
        Dict[str, Any]: API响应结果，包含：
        - success (bool): 请求是否成功
        - content (dict): 关闭操作结果，包含：
          - message (str): 操作结果消息
          - closed_count (int): 成功关闭的窗口数量
          - failed_windows (list, optional): 关闭失败的窗口列表
        - status_code (int): HTTP状态码
        - error (str, optional): 错误信息（如果有）
        
    API端点: POST /windows/close
        
    Example:
        >>> # 关闭特定窗口
        >>> result = await close_windows_batch(
        ...     handle=12345,
        ...     title="Google Chrome - 新标签页",
        ...     width=1200,
        ...     height=800,
        ...     x=100,
        ...     y=100,
        ...     alias="浏览器"
        ... )
        >>> if result["success"]:
        ...     content = result["content"]
        ...     print(f"关闭操作完成: {content['message']}")
        ...     print(f"成功关闭 {content['closed_count']} 个窗口")
        >>> else:
        ...     print(f"关闭窗口失败: {result['error']}")
    """
    # 构建请求数据
    window_data = {
        "handle": handle,
        "title": title,
        "width": width,
        "height": height,
        "x": x,
        "y": y,
        "icon": icon,
        "alias": alias
    }
    
    # 记录操作日志
    if LogConfig.VERBOSE:
        logging.info(f"准备关闭窗口: {title} (句柄: {handle})")
    
    return await make_api_request("WINDOWS_CLOSE_BATCH", method="POST", data=window_data)

async def minimize_windows_batch(handle: int, title: str, width: int, height: int, 
                                x: int, y: int, icon: Optional[str] = None, 
                                alias: Optional[str] = None) -> Dict[str, Any]:
    """批量最小化窗口
    
    通过调用后端API接口批量最小化指定的窗口。
    
    入参：
        handle (int): 窗口句柄，用于唯一标识窗口
        title (str): 窗口标题
        width (int): 窗口宽度（像素）
        height (int): 窗口高度（像素）
        x (int): 窗口左上角X坐标
        y (int): 窗口左上角Y坐标
        icon (str, optional): 窗口图标，base64编码的PNG数据，默认None
        alias (str, optional): 窗口别名，默认None
        
    出参：
        Dict[str, Any]: API响应结果，包含：
        - success (bool): 请求是否成功
        - content (dict): 最小化操作结果，包含：
          - message (str): 操作结果消息
          - minimized_count (int): 成功最小化的窗口数量
          - failed_windows (list, optional): 最小化失败的窗口列表
        - status_code (int): HTTP状态码
        - error (str, optional): 错误信息（如果有）
        
    API端点: POST /windows/minimize
        
    Example:
        >>> # 最小化特定窗口
        >>> result = await minimize_windows_batch(
        ...     handle=12345,
        ...     title="Google Chrome - 新标签页",
        ...     width=1200,
        ...     height=800,
        ...     x=100,
        ...     y=100,
        ...     alias="浏览器"
        ... )
        >>> if result["success"]:
        ...     content = result["content"]
        ...     print(f"最小化操作完成: {content['message']}")
        ...     print(f"成功最小化 {content['minimized_count']} 个窗口")
        >>> else:
        ...     print(f"最小化窗口失败: {result['error']}")
    """
    # 构建请求数据
    window_data = {
        "handle": handle,
        "title": title,
        "width": width,
        "height": height,
        "x": x,
        "y": y,
        "icon": icon,
        "alias": alias
    }
    
    # 记录操作日志
    if LogConfig.VERBOSE:
        logging.info(f"准备最小化窗口: {title} (句柄: {handle})")
    
    return await make_api_request("WINDOWS_MINIMIZE_BATCH", method="POST", data=window_data)

async def maximize_windows_batch(handle: int, title: str, width: int, height: int, 
                                x: int, y: int, icon: Optional[str] = None, 
                                alias: Optional[str] = None) -> Dict[str, Any]:
    """批量最大化窗口
    
    通过调用后端API接口批量最大化指定的窗口。
    
    入参：
        handle (int): 窗口句柄，用于唯一标识窗口
        title (str): 窗口标题
        width (int): 窗口宽度（像素）
        height (int): 窗口高度（像素）
        x (int): 窗口左上角X坐标
        y (int): 窗口左上角Y坐标
        icon (str, optional): 窗口图标，base64编码的PNG数据，默认None
        alias (str, optional): 窗口别名，默认None
        
    出参：
        Dict[str, Any]: API响应结果，包含：
        - success (bool): 请求是否成功
        - content (dict): 最大化操作结果，包含：
          - message (str): 操作结果消息
          - maximized_count (int): 成功最大化的窗口数量
          - failed_windows (list, optional): 最大化失败的窗口列表
        - status_code (int): HTTP状态码
        - error (str, optional): 错误信息（如果有）
        
    API端点: POST /windows/maximize
        
    Example:
        >>> # 最大化特定窗口
        >>> result = await maximize_windows_batch(
        ...     handle=12345,
        ...     title="Google Chrome - 新标签页",
        ...     width=1200,
        ...     height=800,
        ...     x=100,
        ...     y=100,
        ...     alias="浏览器"
        ... )
        >>> if result["success"]:
        ...     content = result["content"]
        ...     print(f"最大化操作完成: {content['message']}")
        ...     print(f"成功最大化 {content['maximized_count']} 个窗口")
        >>> else:
        ...     print(f"最大化窗口失败: {result['error']}")
    """
    # 构建请求数据
    window_data = {
        "handle": handle,
        "title": title,
        "width": width,
        "height": height,
        "x": x,
        "y": y,
        "icon": icon,
        "alias": alias
    }
    
    # 记录操作日志
    if LogConfig.VERBOSE:
        logging.info(f"准备最大化窗口: {title} (句柄: {handle})")
    
    return await make_api_request("WINDOWS_MAXIMIZE_BATCH", method="POST", data=window_data)

async def restore_windows_batch(handle: int, title: str, width: int, height: int, 
                               x: int, y: int, icon: Optional[str] = None, 
                               alias: Optional[str] = None) -> Dict[str, Any]:
    """批量还原窗口
    
    通过调用后端API接口批量还原指定的窗口到正常状态。
    还原操作会将最小化或最大化的窗口恢复到其原始大小和位置。
    
    入参：
        handle (int): 窗口句柄，用于唯一标识窗口
        title (str): 窗口标题
        width (int): 窗口宽度（像素）
        height (int): 窗口高度（像素）
        x (int): 窗口左上角X坐标
        y (int): 窗口左上角Y坐标
        icon (str, optional): 窗口图标，base64编码的PNG数据，默认None
        alias (str, optional): 窗口别名，默认None
        
    出参：
        Dict[str, Any]: API响应结果，包含：
        - success (bool): 请求是否成功
        - content (dict): 还原操作结果，包含：
          - message (str): 操作结果消息
          - restored_count (int): 成功还原的窗口数量
          - failed_windows (list, optional): 还原失败的窗口列表
        - status_code (int): HTTP状态码
        - error (str, optional): 错误信息（如果有）
        
    API端点: POST /windows/restore
        
    Example:
        >>> # 还原特定窗口
        >>> result = await restore_windows_batch(
        ...     handle=12345,
        ...     title="Google Chrome - 新标签页",
        ...     width=1200,
        ...     height=800,
        ...     x=100,
        ...     y=100,
        ...     alias="浏览器"
        ... )
        >>> if result["success"]:
        ...     content = result["content"]
        ...     print(f"还原操作完成: {content['message']}")
        ...     print(f"成功还原 {content['restored_count']} 个窗口")
        >>> else:
        ...     print(f"还原窗口失败: {result['error']}")
    """
    # 构建请求数据
    window_data = {
        "handle": handle,
        "title": title,
        "width": width,
        "height": height,
        "x": x,
        "y": y,
        "icon": icon,
        "alias": alias
    }
    
    # 记录操作日志
    if LogConfig.VERBOSE:
        logging.info(f"准备还原窗口: {title} (句柄: {handle})")
    
    return await make_api_request("WINDOWS_RESTORE_BATCH", method="POST", data=window_data)

async def set_window_opacity_batch(windows: List[WindowOpacityItem]) -> Dict[str, Any]:
    """批量设置窗口透明度
    
    通过调用后端API接口批量设置指定窗口的透明度。
    支持同时为多个窗口设置不同的透明度值。
    
    入参：
        windows (List[WindowOpacityItem]): 窗口透明度设置列表，每个项目包含：
            - window (WindowInfo): 窗口信息对象
              - handle (int): 窗口句柄，用于唯一标识窗口
              - title (str): 窗口标题
              - width (int): 窗口宽度（像素）
              - height (int): 窗口高度（像素）
              - x (int): 窗口左上角X坐标
              - y (int): 窗口左上角Y坐标
              - icon (str, optional): 窗口图标，base64编码的PNG数据
              - alias (str, optional): 窗口别名
            - opacity (int): 透明度值（0-255）
              - 0: 完全透明（不可见）
              - 128: 半透明
              - 255: 完全不透明（默认状态）
        
    出参：
        Dict[str, Any]: API响应结果，包含：
        - success (bool): 请求是否成功
        - content (dict): 透明度设置操作结果，包含：
          - message (str): 操作结果消息
          - updated_count (int): 成功设置透明度的窗口数量
          - failed_windows (list, optional): 设置失败的窗口列表
        - status_code (int): HTTP状态码
        - error (str, optional): 错误信息（如果有）
        
    API端点: POST /windows/opacity
        
    Example:
        >>> # 设置多个窗口的透明度
        >>> windows_to_update = [
        ...     WindowOpacityItem(
        ...         window=WindowInfo(
        ...             handle=12345,
        ...             title="Google Chrome - 新标签页",
        ...             width=1200,
        ...             height=800,
        ...             x=100,
        ...             y=100,
        ...             alias="浏览器"
        ...         ),
        ...         opacity=128  # 半透明
        ...     ),
        ...     WindowOpacityItem(
        ...         window=WindowInfo(
        ...             handle=67890,
        ...             title="记事本",
        ...             width=600,
        ...             height=400,
        ...             x=200,
        ...             y=200
        ...         ),
        ...         opacity=200  # 轻微透明
        ...     )
        ... ]
        >>> result = await set_window_opacity_batch(windows_to_update)
        >>> if result["success"]:
        ...     content = result["content"]
        ...     print(f"透明度设置完成: {content['message']}")
        ...     print(f"成功设置 {content['updated_count']} 个窗口的透明度")
        >>> else:
        ...     print(f"设置窗口透明度失败: {result['error']}")
    """
    # 构建请求数据 - 转换为API期望的格式
    request_data = []
    for item in windows:
        window_data = {
            "window": {
                "handle": item.window.handle,
                "title": item.window.title,
                "width": item.window.width,
                "height": item.window.height,
                "x": item.window.x,
                "y": item.window.y,
                "icon": item.window.icon,
                "alias": item.window.alias
            },
            "opacity": item.opacity
        }
        request_data.append(window_data)
    
    # 记录操作日志
    if LogConfig.VERBOSE:
        window_titles = [item.window.title for item in windows]
        opacity_values = [item.opacity for item in windows]
        logging.info(f"准备设置 {len(windows)} 个窗口的透明度")
        logging.info(f"窗口标题: {window_titles}")
        logging.info(f"透明度值: {opacity_values}")
    
    return await make_api_request("WINDOWS_OPACITY_BATCH", method="POST", data=request_data)

async def serve() -> None:
    """MCP Layout Driver服务器主函数
    
    这是整个MCP Layout Driver系统的入口函数，负责启动和运行MCP服务器。
    该函数创建了一个完整的MCP服务器实例，注册所有可用的工具，并处理客户端的请求。
    
    ## 功能概述：
    该函数实现了一个基于MCP（Model Context Protocol）的窗口管理服务器，提供以下核心功能：
    1. 窗口发现：获取当前桌面所有打开的窗口列表
    2. 窗口操作：批量关闭、最小化、最大化、还原窗口
    3. 视觉效果：批量设置窗口透明度
    4. API集成：所有操作都通过后端API实现真实的窗口管理
    
    ## 业务逻辑流程：
    1. **服务器初始化**：
       - 创建名为"layout_driver"的MCP服务器实例
       - 配置日志系统
       - 设置服务器基础参数
    
    2. **工具注册阶段**：
       - 通过@server.list_tools()装饰器注册工具发现端点
       - 为每个窗口管理功能创建Tool对象
       - 定义工具的名称、描述和输入模式
    
    3. **请求处理阶段**：
       - 通过@server.call_tool()装饰器注册工具调用端点
       - 根据工具名称路由到相应的处理函数
       - 参数验证和类型转换
       - 调用后端API执行实际操作
    
    4. **通信管理**：
       - 建立stdio通信通道（标准输入/输出）
       - 处理MCP协议消息
       - 管理客户端连接生命周期
    
    ## 服务器架构：
    ```
    MCP客户端 <---> MCP协议 <---> Layout Driver Server <---> 后端API <---> 系统窗口管理
         ^                           ^                       ^                    ^
         |                           |                       |                    |
      AI模型                    本函数serve()            HTTP请求             实际窗口操作
    ```
    
    ## 注册的工具列表：
    1. **get_window_list**: 获取桌面窗口列表
       - 端点：GET /windows
       - 返回：所有打开窗口的详细信息
    
    2. **close_windows_batch**: 批量关闭窗口
       - 端点：POST /windows/close
       - 功能：永久关闭指定窗口
    
    3. **minimize_windows_batch**: 批量最小化窗口
       - 端点：POST /windows/minimize
       - 功能：隐藏窗口但保持进程运行
    
    4. **maximize_windows_batch**: 批量最大化窗口
       - 端点：POST /windows/maximize
       - 功能：全屏显示窗口
    
    5. **restore_windows_batch**: 批量还原窗口
       - 端点：POST /windows/restore
       - 功能：恢复窗口到正常状态
    
    6. **set_window_opacity_batch**: 批量设置窗口透明度
       - 端点：POST /windows/opacity
       - 功能：调整窗口的透明度效果
    
    ## 错误处理机制：
    - 所有工具调用都有完整的异常处理
    - 网络错误和API错误会被优雅处理
    - 错误信息会以JSON格式返回给客户端
    - 支持详细的调试日志（如果启用verbose模式）
    
    ## 入参：
        无参数 - 该函数不接受任何参数
    
    ## 出参：
        无返回值 (None) - 该函数运行直到服务器关闭
        
    ## 异常处理：
        - 如果服务器启动失败，会抛出相应异常
        - 如果通信通道建立失败，会抛出异常
        - 运行时异常会被记录但不会导致服务器崩溃
    
    ## 使用示例：
        >>> # 启动MCP服务器
        >>> await serve()
        
        # 服务器将持续运行，直到收到停止信号
        # 客户端可以通过MCP协议调用注册的工具
    
    ## 配置依赖：
    - APIConfig: API端点和超时配置
    - SecurityConfig: SSL和认证配置  
    - LogConfig: 日志级别和格式配置
    
    ## 注意事项：
    1. 该函数是异步函数，需要在异步上下文中运行
    2. 服务器会持续运行直到进程终止
    3. 所有的窗口操作都需要后端API服务正常运行
    4. 建议在生产环境中配置适当的错误监控
    5. 服务器使用stdio通信，适合与MCP客户端集成
    """
    # 步骤1: 初始化日志记录器
    # 为当前模块创建专用的日志记录器，用于记录服务器运行状态
    logger = logging.getLogger(__name__)
    
    # 步骤2: 创建MCP服务器实例
    # 使用"layout_driver"作为服务器标识符，这个名称会在MCP协议中使用
    server = Server("layout_driver")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """工具发现端点 - 向MCP客户端提供可用工具列表
        
        这是MCP协议的核心端点之一，负责向客户端宣告服务器提供的所有可用工具。
        当MCP客户端连接到服务器时，会首先调用此端点来获取工具清单。
        
        ## 业务逻辑说明：
        1. **工具注册**：为每个窗口管理功能创建Tool对象
        2. **模式定义**：使用Pydantic模型自动生成JSON Schema
        3. **元数据设置**：为每个工具设置名称、描述和输入验证规则
        4. **国际化支持**：提供中英文双语描述
        
        ## 工具分类：
        
        ### 🔍 窗口发现类工具：
        - **get_window_list**: 获取当前桌面已打开窗口列表
          - 用途：让AI模型了解当前桌面状态
          - 无需输入参数
          - 返回完整的窗口信息列表
        
        ### 🎯 窗口状态控制类工具：
        - **close_windows_batch**: 批量关闭窗口
          - 用途：永久关闭不需要的窗口，释放系统资源
          - 危险级别：高（不可逆操作）
          
        - **minimize_windows_batch**: 批量最小化窗口
          - 用途：隐藏窗口到任务栏，保持进程运行
          - 危险级别：低（可恢复操作）
          
        - **maximize_windows_batch**: 批量最大化窗口
          - 用途：全屏显示窗口，提高工作效率
          - 危险级别：低（可恢复操作）
          
        - **restore_windows_batch**: 批量还原窗口
          - 用途：恢复窗口到正常状态
          - 危险级别：低（恢复性操作）
        
        ### 🎨 视觉效果类工具：
        - **set_window_opacity_batch**: 批量设置窗口透明度
          - 用途：调整窗口透明度，创建视觉效果
          - 支持：0-255透明度值范围
          - 危险级别：低（可恢复操作）
        
        ## 输入模式验证：
        每个工具都使用对应的Pydantic模型进行输入验证：
        - GetWindowList: 无参数模型
        - CloseWindowRequest: 单窗口操作模型
        - MinimizeWindowRequest: 单窗口操作模型
        - MaximizeWindowRequest: 单窗口操作模型
        - RestoreWindowRequest: 单窗口操作模型
        - SetWindowOpacityRequest: 多窗口操作模型（支持批量不同透明度）
        
        ## 入参：
            无参数 - 该函数不接受任何参数（由MCP框架自动调用）
        
        ## 出参：
            返回 list[Tool] - 包含所有可用工具的列表，每个Tool对象包含：
            - name (str): 工具的唯一标识符（对应DriverTools枚举值）
            - description (str): 工具的功能描述（中英文双语）
            - inputSchema (dict): JSON Schema格式的输入参数验证规则
        
        ## 工具调用流程：
        ```
        1. 客户端调用 list_tools() 获取工具列表
        2. 客户端选择需要的工具
        3. 客户端根据 inputSchema 构造参数
        4. 客户端调用 call_tool(name, arguments)
        5. 服务器执行相应的窗口操作
        ```
        
        ## 注意事项：
        1. 工具列表是静态的，服务器启动后不会改变
        2. 每个工具的inputSchema都是自动生成的JSON Schema
        3. 工具描述支持中英文，便于不同语言的AI模型理解
        4. 工具名称必须与DriverTools枚举保持一致
        5. 危险操作（如关闭窗口）应该在描述中明确标注
        
        ## 示例返回值：
        ```json
        [
          {
            "name": "get_window_list",
            "description": "获取当前桌面已打开窗口列表 - Get list of currently open windows",
            "inputSchema": {...}
          },
          ...
        ]
        ```
        """
        return [
            # 窗口发现工具：获取桌面窗口列表
            Tool(
                name=DriverTools.GET_WINDOW_LIST,
                description="获取当前桌面已打开窗口列表 - Get list of currently open windows on desktop via API",
                inputSchema=GetWindowList.model_json_schema(),
            ),
            # 窗口关闭工具：永久关闭指定窗口（危险操作）
            Tool(
                name=DriverTools.CLOSE_WINDOWS_BATCH,
                description="批量关闭窗口 - Batch close windows by providing window details",
                inputSchema=CloseWindowRequest.model_json_schema(),
            ),
            # 窗口最小化工具：隐藏窗口但保持进程运行
            Tool(
                name=DriverTools.MINIMIZE_WINDOWS_BATCH,
                description="批量最小化窗口 - Batch minimize windows by providing window details",
                inputSchema=MinimizeWindowRequest.model_json_schema(),
            ),
            # 窗口最大化工具：全屏显示窗口
            Tool(
                name=DriverTools.MAXIMIZE_WINDOWS_BATCH,
                description="批量最大化窗口 - Batch maximize windows by providing window details",
                inputSchema=MaximizeWindowRequest.model_json_schema(),
            ),
            # 窗口还原工具：恢复窗口到正常状态
            Tool(
                name=DriverTools.RESTORE_WINDOWS_BATCH,
                description="批量还原窗口 - Batch restore windows to normal state by providing window details",
                inputSchema=RestoreWindowRequest.model_json_schema(),
            ),
            # 透明度设置工具：调整窗口视觉效果
            Tool(
                name=DriverTools.SET_WINDOW_OPACITY_BATCH,
                description="批量设置窗口透明度 - Batch set window opacity/transparency for multiple windows",
                inputSchema=SetWindowOpacityRequest.model_json_schema(),
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        """工具执行端点 - 处理MCP客户端的工具调用请求
        
        这是MCP协议的核心执行端点，负责根据工具名称和参数执行相应的窗口管理操作。
        该函数接收客户端的工具调用请求，进行参数验证，调用后端API，并返回操作结果。
        
        ## 业务逻辑流程：
        1. **路由分发**：根据工具名称（name）路由到相应的处理分支
        2. **参数提取**：从arguments字典中提取和验证输入参数
        3. **类型转换**：将字典参数转换为相应的数据模型（如WindowInfo）
        4. **API调用**：调用相应的后端函数执行实际的窗口操作
        5. **结果封装**：将API返回结果封装为MCP标准的TextContent格式
        6. **错误处理**：捕获和处理未知工具名称的异常
        
        ## 参数处理策略：
        
        ### 🔍 简单参数工具（get_window_list）：
        - 无需参数处理
        - 直接调用get_window_list()函数
        
        ### 🎯 单窗口操作工具（close/minimize/maximize/restore）：
        - 从arguments中提取窗口基础信息：
          - handle (int): 窗口句柄 [必需]
          - title (str): 窗口标题 [必需]
          - width (int): 窗口宽度 [必需]
          - height (int): 窗口高度 [必需]
          - x (int): 窗口X坐标 [必需]
          - y (int): 窗口Y坐标 [必需]
          - icon (str): 窗口图标 [可选，使用.get()]
          - alias (str): 窗口别名 [可选，使用.get()]
        
        ### 🎨 多窗口操作工具（set_window_opacity_batch）：
        - 处理复杂的嵌套数据结构
        - 将arguments["windows"]中的每个项目转换为WindowOpacityItem对象
        - 每个项目包含window对象和opacity值
        - 使用列表推导式进行批量转换
        
        ## 错误处理机制：
        1. **参数缺失**：如果必需参数缺失，会引发KeyError
        2. **类型错误**：如果参数类型不匹配，会引发TypeError或ValueError
        3. **未知工具**：如果工具名称不在支持列表中，抛出ValueError
        4. **API错误**：后端API调用失败的错误会通过JSON响应返回
        
        ## 返回值格式：
        所有工具调用都返回统一的JSON格式响应，包装在TextContent中：
        ```json
        {
          "success": true/false,
          "status_code": 200,
          "content": {...},
          "headers": {...},
          "url": "http://...",
          "error": "错误信息"  // 仅在失败时存在
        }
        ```
        
        ## 入参详细说明：
            name (str): 要执行的工具名称，必须是以下之一：
                - "get_window_list": 获取窗口列表
                - "close_windows_batch": 批量关闭窗口
                - "minimize_windows_batch": 批量最小化窗口
                - "maximize_windows_batch": 批量最大化窗口
                - "restore_windows_batch": 批量还原窗口
                - "set_window_opacity_batch": 批量设置窗口透明度
                
            arguments (dict): 工具调用参数，格式根据工具类型而异：
                
                ## get_window_list参数：
                {} (空字典，无需参数)
                
                ## 单窗口操作参数（close/minimize/maximize/restore）：
                {
                    "handle": 12345,              # 窗口句柄（整数）
                    "title": "窗口标题",           # 窗口标题（字符串）
                    "width": 1200,               # 窗口宽度（整数）
                    "height": 800,               # 窗口高度（整数）
                    "x": 100,                    # 窗口X坐标（整数）
                    "y": 100,                    # 窗口Y坐标（整数）
                    "icon": "base64...",         # 窗口图标（可选字符串）
                    "alias": "别名"              # 窗口别名（可选字符串）
                }
                
                ## 多窗口透明度设置参数：
                {
                    "windows": [                 # 窗口列表
                        {
                            "handle": 12345,
                            "title": "窗口1",
                            "width": 1200,
                            "height": 800,
                            "x": 100,
                            "y": 100,
                            "icon": null,
                            "alias": null,
                            "opacity": 128       # 透明度值（0-255）
                        }
                    ]
                }
        
        ## 出参详细说明：
            返回 list[TextContent] - 包含单个TextContent元素的列表：
            - type: "text" (固定值)
            - text: JSON格式的操作结果字符串
            
            JSON内容结构：
            - success (bool): 操作是否成功
            - status_code (int): HTTP状态码
            - content (any): API返回的具体内容
            - headers (dict): HTTP响应头（成功时）
            - url (str): 请求的API地址
            - error (str): 错误信息（失败时）
        
        ## 工具执行示例：
        
        ### 获取窗口列表：
        ```python
        name = "get_window_list"
        arguments = {}
        result = await call_tool(name, arguments)
        # 返回所有打开窗口的信息
        ```
        
        ### 关闭窗口：
        ```python
        name = "close_windows_batch"
        arguments = {
            "handle": 12345,
            "title": "Chrome",
            "width": 1200,
            "height": 800,
            "x": 100,
            "y": 100
        }
        result = await call_tool(name, arguments)
        # 关闭指定窗口
        ```
        
        ### 设置透明度：
        ```python
        name = "set_window_opacity_batch"
        arguments = {
            "windows": [
                {
                    "handle": 12345,
                    "title": "Chrome",
                    "width": 1200,
                    "height": 800,
                    "x": 100,
                    "y": 100,
                    "icon": null,
                    "alias": null,
                    "opacity": 128
                }
            ]
        }
        result = await call_tool(name, arguments)
        # 设置窗口为半透明
        ```
        
        ## 注意事项：
        1. 该函数是异步函数，所有操作都是非阻塞的
        2. 参数验证依赖于Pydantic模型的隐式验证
        3. 所有API调用错误都会被捕获并返回给客户端
        4. 返回的JSON字符串使用ensure_ascii=False支持中文
        5. 透明度设置工具的参数结构比其他工具更复杂
        6. 未知工具名称会抛出ValueError异常
        """
        # 工具路由：根据工具名称分发到相应的处理逻辑
        if name == DriverTools.GET_WINDOW_LIST:
            # 🔍 窗口发现工具：获取所有打开窗口的列表
            # 业务逻辑：调用后端API获取当前桌面所有窗口信息
            # 参数：无需参数
            # 返回：窗口信息列表，包含句柄、标题、尺寸、位置等
            result = await get_window_list()
            return [TextContent(
                type="text",
                text=json.dumps(result, ensure_ascii=False, indent=2)
            )]
            
        elif name == DriverTools.CLOSE_WINDOWS_BATCH:
            # 🎯 窗口关闭工具：永久关闭指定窗口（危险操作）
            # 业务逻辑：向后端API发送关闭请求，窗口将被永久关闭
            # 参数：完整的窗口信息（用于精确匹配）
            # 风险：不可逆操作，窗口关闭后无法恢复
            result = await close_windows_batch(
                handle=arguments["handle"],          # 窗口唯一标识符
                title=arguments["title"],            # 窗口标题（用于验证）
                width=arguments["width"],            # 窗口宽度（用于验证）
                height=arguments["height"],          # 窗口高度（用于验证）
                x=arguments["x"],                    # 窗口X坐标（用于验证）
                y=arguments["y"],                    # 窗口Y坐标（用于验证）
                icon=arguments.get("icon"),          # 窗口图标（可选）
                alias=arguments.get("alias")         # 窗口别名（可选）
            )
            return [TextContent(
                type="text",
                text=json.dumps(result, ensure_ascii=False, indent=2)
            )]
            
        elif name == DriverTools.MINIMIZE_WINDOWS_BATCH:
            # 🎯 窗口最小化工具：隐藏窗口但保持进程运行（安全操作）
            # 业务逻辑：将窗口最小化到任务栏，进程继续运行
            # 参数：完整的窗口信息
            # 特点：可恢复操作，窗口可以重新显示
            result = await minimize_windows_batch(
                handle=arguments["handle"],
                title=arguments["title"],
                width=arguments["width"],
                height=arguments["height"],
                x=arguments["x"],
                y=arguments["y"],
                icon=arguments.get("icon"),
                alias=arguments.get("alias")
            )
            return [TextContent(
                type="text",
                text=json.dumps(result, ensure_ascii=False, indent=2)
            )]
            
        elif name == DriverTools.MAXIMIZE_WINDOWS_BATCH:
            # 🎯 窗口最大化工具：全屏显示窗口（安全操作）
            # 业务逻辑：将窗口扩展到最大尺寸，通常占满整个屏幕
            # 参数：完整的窗口信息
            # 用途：提高工作效率，适合需要大屏幕空间的应用
            result = await maximize_windows_batch(
                handle=arguments["handle"],
                title=arguments["title"],
                width=arguments["width"],
                height=arguments["height"],
                x=arguments["x"],
                y=arguments["y"],
                icon=arguments.get("icon"),
                alias=arguments.get("alias")
            )
            return [TextContent(
                type="text",
                text=json.dumps(result, ensure_ascii=False, indent=2)
            )]
            
        elif name == DriverTools.RESTORE_WINDOWS_BATCH:
            # 🎯 窗口还原工具：恢复窗口到正常状态（恢复操作）
            # 业务逻辑：将最小化或最大化的窗口恢复到原始状态
            # 参数：完整的窗口信息
            # 用途：撤销之前的最小化或最大化操作
            result = await restore_windows_batch(
                handle=arguments["handle"],
                title=arguments["title"],
                width=arguments["width"],
                height=arguments["height"],
                x=arguments["x"],
                y=arguments["y"],
                icon=arguments.get("icon"),
                alias=arguments.get("alias")
            )
            return [TextContent(
                type="text",
                text=json.dumps(result, ensure_ascii=False, indent=2)
            )]
            
        elif name == DriverTools.SET_WINDOW_OPACITY_BATCH:
            # 🎨 窗口透明度工具：批量设置窗口视觉效果（视觉操作）
            # 业务逻辑：调整一个或多个窗口的透明度，创建视觉效果
            # 参数：包含窗口信息和透明度值的复杂数据结构
            # 特点：支持为不同窗口设置不同的透明度值
            # 透明度范围：0（完全透明）到255（完全不透明）
            result = await set_window_opacity_batch(
                windows=[
                    # 使用列表推导式将字典参数转换为WindowOpacityItem对象
                    WindowOpacityItem(
                        window=WindowInfo(
                            handle=item["handle"],       # 窗口句柄
                            title=item["title"],         # 窗口标题
                            width=item["width"],         # 窗口宽度
                            height=item["height"],       # 窗口高度
                            x=item["x"],                 # 窗口X坐标
                            y=item["y"],                 # 窗口Y坐标
                            icon=item["icon"],           # 窗口图标
                            alias=item["alias"]          # 窗口别名
                        ),
                        opacity=item["opacity"]          # 透明度值（0-255）
                    )
                    for item in arguments["windows"]     # 遍历所有窗口参数
                ]
            )
            return [TextContent(
                type="text",
                text=json.dumps(result, ensure_ascii=False, indent=2)
            )]
            
        else:
            # ❌ 错误处理：未知的工具名称
            # 如果客户端请求了不存在的工具，抛出异常
            # 这通常表示客户端和服务器版本不匹配或存在编程错误
            raise ValueError(f"Unknown tool: {name}")

    # 步骤3: 创建服务器初始化选项
    # 生成MCP服务器的配置选项，包括协议版本、功能支持等
    options = server.create_initialization_options()
    
    # 步骤4: 启动MCP服务器并建立通信通道
    # 使用stdio（标准输入/输出）作为通信方式，这是MCP协议的标准方式
    # 这种方式允许服务器与任何支持MCP协议的客户端通信
    async with stdio_server() as (read_stream, write_stream):
        # 步骤5: 运行服务器主循环
        # 服务器将持续监听客户端请求，直到连接关闭或收到停止信号
        # raise_exceptions=True 确保异常会被抛出而不是被静默忽略
        await server.run(read_stream, write_stream, options, raise_exceptions=True)