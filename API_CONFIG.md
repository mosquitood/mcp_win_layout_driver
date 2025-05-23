# MCP Layout Driver API 配置说明

## 概述

MCP Layout Driver 现在已经配置为通过 HTTP API 调用后端服务来获取真实数据，而不是返回模拟数据。每个工具函数都会向指定的API端点发送请求。

## API 配置

### 环境变量配置

您可以通过以下环境变量来配置API行为：

```bash
# API基础URL
export LAYOUT_DRIVER_API_URL="http://127.0.0.1:23456"

# 请求超时时间（秒）
export LAYOUT_DRIVER_TIMEOUT="30"

# 日志级别
export LAYOUT_DRIVER_LOG_LEVEL="INFO"

# 启用详细日志
export LAYOUT_DRIVER_VERBOSE="true"

# SSL证书验证
export LAYOUT_DRIVER_VERIFY_SSL="true"

# API认证Token
export LAYOUT_DRIVER_AUTH_TOKEN="your_token_here"

# 最大重试次数
export LAYOUT_DRIVER_MAX_RETRIES="3"
```

### API 端点定义

当前定义的API端点包括：

#### 窗口管理
- `GET /windows` - 获取窗口列表
- `POST /windows/close` - 批量关闭窗口
- `POST /windows/minimize` - 批量最小化窗口
- `POST /windows/maximize` - 批量最大化窗口
- `POST /windows/restore` - 批量还原窗口
- `POST /windows/opacity` - 批量设置窗口透明度

## 当前实现的工具函数

### 1. get_window_list()

**功能**: 获取当前桌面已打开窗口列表
**API调用**: `GET /windows`
**返回格式**:
```json
{
  "success": true,
  "status_code": 200,
  "content": [
    {
      "handle": 12345,
      "title": "窗口标题",
      "width": 1200,
      "height": 800,
      "x": 100,
      "y": 100,
      "icon": "data:image/png;base64,...",
      "alias": "窗口别名"
    }
  ],
  "headers": {...},
  "url": "http://127.0.0.1:23456/windows"
}
```

### 2. close_windows_batch()

**功能**: 批量关闭窗口
**API调用**: `POST /windows/close`
**入参**:
```json
{
  "handle": 12345,
  "title": "窗口标题",
  "width": 1200,
  "height": 800,
  "x": 100,
  "y": 100,
  "icon": "data:image/png;base64,...",
  "alias": "窗口别名"
}
```
**返回格式**:
```json
{
  "success": true,
  "status_code": 200,
  "content": {
    "message": "窗口关闭操作完成",
    "closed_count": 1,
    "failed_windows": []
  },
  "headers": {...},
  "url": "http://127.0.0.1:23456/windows/close"
}
```

### 3. minimize_windows_batch()

**功能**: 批量最小化窗口
**API调用**: `POST /windows/minimize`
**入参**:
```json
{
  "handle": 12345,
  "title": "窗口标题",
  "width": 1200,
  "height": 800,
  "x": 100,
  "y": 100,
  "icon": "data:image/png;base64,...",
  "alias": "窗口别名"
}
```
**返回格式**:
```json
{
  "success": true,
  "status_code": 200,
  "content": {
    "message": "窗口最小化操作完成",
    "minimized_count": 1,
    "failed_windows": []
  },
  "headers": {...},
  "url": "http://127.0.0.1:23456/windows/minimize"
}
```

### 4. maximize_windows_batch()

**功能**: 批量最大化窗口
**API调用**: `POST /windows/maximize`
**入参**:
```json
{
  "handle": 12345,
  "title": "窗口标题",
  "width": 1200,
  "height": 800,
  "x": 100,
  "y": 100,
  "icon": "data:image/png;base64,...",
  "alias": "窗口别名"
}
```
**返回格式**:
```json
{
  "success": true,
  "status_code": 200,
  "content": {
    "message": "窗口最大化操作完成",
    "maximized_count": 1,
    "failed_windows": []
  },
  "headers": {...},
  "url": "http://127.0.0.1:23456/windows/maximize"
}
```

### 5. restore_windows_batch()

**功能**: 批量还原窗口
**API调用**: `POST /windows/restore`
**入参**:
```json
{
  "handle": 12345,
  "title": "窗口标题",
  "width": 1200,
  "height": 800,
  "x": 100,
  "y": 100,
  "icon": "data:image/png;base64,...",
  "alias": "窗口别名"
}
```
**返回格式**:
```json
{
  "success": true,
  "status_code": 200,
  "content": {
    "message": "窗口还原操作完成",
    "restored_count": 1,
    "failed_windows": []
  },
  "headers": {...},
  "url": "http://127.0.0.1:23456/windows/restore"
}
```

### 6. set_window_opacity_batch()

**功能**: 批量设置窗口透明度
**API调用**: `POST /windows/opacity`
**入参**:
```json
[
  {
    "window": {
      "handle": 12345,
      "title": "窗口标题",
      "width": 1200,
      "height": 800,
      "x": 100,
      "y": 100,
      "icon": "data:image/png;base64,...",
      "alias": "窗口别名"
    },
    "opacity": 128
  }
]
```
**返回格式**:
```json
{
  "success": true,
  "status_code": 200,
  "content": {
    "message": "窗口透明度设置完成",
    "updated_count": 1,
    "failed_windows": []
  },
  "headers": {...},
  "url": "http://127.0.0.1:23456/windows/opacity"
}
```

**透明度值说明**:
- `0`: 完全透明（窗口不可见）
- `128`: 半透明（50%透明度）
- `255`: 完全不透明（默认状态）

## 后端API要求

您的后端API应该：

1. **响应格式**: 返回JSON格式的数据
2. **状态码**: 使用标准HTTP状态码
   - 200: 成功
   - 400: 客户端错误
   - 404: 资源不存在
   - 500: 服务器错误

3. **CORS**: 如果从浏览器访问，需要配置CORS

4. **认证**: 如果需要认证，支持Bearer Token

### 批量操作API规范

您的后端需要实现以下接口：

#### 批量关闭窗口
**端点**: `POST /windows/close`
**请求体**:
```json
{
  "handle": 0,
  "title": "窗口标题",
  "width": 0,
  "height": 0,
  "x": 0,
  "y": 0,
  "icon": "data:image/png",
  "alias": "别名"
}
```
**响应**: HTTP 200 状态码表示成功

#### 批量最小化窗口
**端点**: `POST /windows/minimize`
**请求体**:
```json
{
  "handle": 0,
  "title": "窗口标题",
  "width": 0,
  "height": 0,
  "x": 0,
  "y": 0,
  "icon": "data:image/png",
  "alias": "别名"
}
```
**响应**: HTTP 200 状态码表示成功

#### 批量最大化窗口
**端点**: `POST /windows/maximize`
**请求体**:
```json
{
  "handle": 0,
  "title": "窗口标题",
  "width": 0,
  "height": 0,
  "x": 0,
  "y": 0,
  "icon": "data:image/png",
  "alias": "别名"
}
```
**响应**: HTTP 200 状态码表示成功

#### 批量还原窗口
**端点**: `POST /windows/restore`
**请求体**:
```json
{
  "handle": 0,
  "title": "窗口标题",
  "width": 0,
  "height": 0,
  "x": 0,
  "y": 0,
  "icon": "data:image/png",
  "alias": "别名"
}
```
**响应**: HTTP 200 状态码表示成功

#### 批量设置窗口透明度
**端点**: `POST /windows/opacity`
**请求体**:
```json
[
  {
    "window": {
      "handle": 0,
      "title": "窗口标题",
      "width": 0,
      "height": 0,
      "x": 0,
      "y": 0,
      "icon": "data:image/png",
      "alias": "别名"
    },
    "opacity": 128
  }
]
```
**响应**: HTTP 200 状态码表示成功
**说明**: 
- 请求体是数组格式，支持同时设置多个窗口的透明度
## 错误处理

系统会自动处理以下错误情况：

- 网络连接失败
- 请求超时
- API返回错误状态码
- JSON解析失败
- SSL证书验证失败（可配置）

所有错误都会返回统一的错误格式：

```json
{
  "success": false,
  "error": "错误描述",
  "status_code": 0,
  "url": "请求的URL"
}
```

## 使用示例

### 基础配置
```bash
# 设置API地址
export LAYOUT_DRIVER_API_URL="http://127.0.0.1:23456"

# 启动MCP服务器
python -m src.layout_driver
```

### 开发环境配置
```bash
# 本地开发，跳过SSL验证，启用详细日志
export LAYOUT_DRIVER_API_URL="http://localhost:3000"
export LAYOUT_DRIVER_VERIFY_SSL="false"
export LAYOUT_DRIVER_VERBOSE="true"
export LAYOUT_DRIVER_LOG_LEVEL="DEBUG"
```

### 生产环境配置
```bash
# 生产环境，使用HTTPS，启用认证
export LAYOUT_DRIVER_API_URL="https://api.production.com/v1"
export LAYOUT_DRIVER_AUTH_TOKEN="your_production_token"
export LAYOUT_DRIVER_VERIFY_SSL="true"
export LAYOUT_DRIVER_TIMEOUT="10"
```

## 测试API连接

您可以通过以下方式测试API连接：

1. **直接测试端点**:
```bash
# 测试获取窗口列表
curl http://127.0.0.1:23456/windows

# 测试批量关闭窗口
curl -X POST http://127.0.0.1:23456/windows/close \
  -H "Content-Type: application/json" \
  -d '{
    "handle": 12345,
    "title": "测试窗口",
    "width": 800,
    "height": 600,
    "x": 100,
    "y": 100,
    "icon": null,
    "alias": "测试"
  }'

# 测试批量最小化窗口
curl -X POST http://127.0.0.1:23456/windows/minimize \
  -H "Content-Type: application/json" \
  -d '{
    "handle": 12345,
    "title": "测试窗口",
    "width": 800,
    "height": 600,
    "x": 100,
    "y": 100,
    "icon": null,
    "alias": "测试"
  }'

# 测试批量最大化窗口
curl -X POST http://127.0.0.1:23456/windows/maximize \
  -H "Content-Type: application/json" \
  -d '{
    "handle": 12345,
    "title": "测试窗口",
    "width": 800,
    "height": 600,
    "x": 100,
    "y": 100,
    "icon": null,
    "alias": "测试"
  }'

# 测试批量还原窗口
curl -X POST http://127.0.0.1:23456/windows/restore \
  -H "Content-Type: application/json" \
  -d '{
    "handle": 12345,
    "title": "测试窗口",
    "width": 800,
    "height": 600,
    "x": 100,
    "y": 100,
    "icon": null,
    "alias": "测试"
  }'

# 测试批量设置窗口透明度
curl -X POST http://127.0.0.1:23456/windows/opacity \
  -H "Content-Type: application/json" \
  -d '[
    {
      "window": {
        "handle": 12345,
        "title": "测试窗口",
        "width": 800,
        "height": 600,
        "x": 100,
        "y": 100,
        "icon": null,
        "alias": "测试"
      },
      "opacity": 128
    }
  ]'
```

2. **使用MCP工具**:
调用相应的工具，检查返回结果中的 `success` 字段。

## 工具函数使用示例

### 获取窗口列表
```python
# 通过MCP调用
result = await get_window_list()
if result["success"]:
    windows = result["content"]
    print(f"找到 {len(windows)} 个窗口")
```

### 批量关闭窗口
```python
# 通过MCP调用
result = await close_windows_batch(
    handle=12345,
    title="Google Chrome - 新标签页",
    width=1200,
    height=800,
    x=100,
    y=100,
    alias="浏览器"
)
if result["success"]:
    print(f"窗口关闭成功: {result['content']['message']}")
```

### 批量最小化窗口
```python
# 通过MCP调用
result = await minimize_windows_batch(
    handle=12345,
    title="Google Chrome - 新标签页",
    width=1200,
    height=800,
    x=100,
    y=100,
    alias="浏览器"
)
if result["success"]:
    print(f"窗口最小化成功: {result['content']['message']}")
```

### 批量最大化窗口
```python
# 通过MCP调用
result = await maximize_windows_batch(
    handle=12345,
    title="Google Chrome - 新标签页",
    width=1200,
    height=800,
    x=100,
    y=100,
    alias="浏览器"
)
if result["success"]:
    print(f"窗口最大化成功: {result['content']['message']}")
```

### 批量还原窗口
```python
# 通过MCP调用
result = await restore_windows_batch(
    handle=12345,
    title="Google Chrome - 新标签页",
    width=1200,
    height=800,
    x=100,
    y=100,
    alias="浏览器"
)
if result["success"]:
    print(f"窗口还原成功: {result['content']['message']}")
```

### 批量设置窗口透明度
```python
# 通过MCP调用
result = await set_window_opacity_batch(
    windows=[
        {
            "handle": 12345,
            "title": "Google Chrome - 新标签页",
            "width": 1200,
            "height": 800,
            "x": 100,
            "y": 100,
            "icon": "data:image/png;base64,...",
            "alias": "浏览器",
            "opacity": 128
        }
    ]
)
if result["success"]:
    print(f"窗口透明度设置成功: {result['content']['message']}")
```

## 扩展功能

要添加新的API端点：

1. 在 `config.py` 的 `APIConfig.ENDPOINTS` 中添加端点
2. 创建对应的工具函数，使用 `make_api_request()` 调用API
3. 在 `DriverTools` 枚举中添加工具名称
4. 在服务器的工具列表和处理函数中注册新工具

这样的设计让您可以轻松扩展新的API功能，而无需修改核心的HTTP请求逻辑。 