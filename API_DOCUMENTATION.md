# RobynVue API 文档

## 目录

1. [用户认证模块](#1-用户认证模块-authentication)
2. [用户管理模块](#2-用户管理模块-users)
3. [产品管理模块](#3-产品管理模块-products)
4. [全局说明](#4-全局说明)

## 1. 用户认证模块 (Authentication)

### 1.1 用户注册预检

- **接口**: `/users/register/precheck`
- **方法**: `POST`
- **功能**: 注册前检查用户信息并发送验证码
- **请求体**:

```json
{
  "email": "user@example.com"
}
```

- **成功响应**:

```json
{
  "code": 200,
  "message": "验证码已发送",
  "data": {
    "expire_in": 300  // 验证码有效期（秒）
  }
}
```

- **错误场景**:
  - 429 请求频繁（5次/分钟）
  - 422 邮箱已被注册

### 1.2 注册验证

- **接口**: `/users/register/verify`
- **方法**: `POST`
- **功能**: 验证邮箱验证码并完成注册，注册成功后自动登录
- **请求体**:

```json
{
  "email": "user@example.com",
  "code": "123456",
  "password": "P@ssw0rd123!"
}
```

- **响应特征**:
  - 自动设置HttpOnly Cookie: `access_token`
  - 返回refresh_token用于令牌刷新

### 1.3 账号密码登录

- **Cookie**: `access_token=Bearer <token>; HttpOnly; Secure; Path=/; SameSite=Strict; Max-Age=1800`
- **速率限制**: 20 次/分钟

### 1.3 用户登录

- **接口**: `/users/login`
- **方法**: `POST`
- **功能**: 用户登录并获取访问令牌
- **请求体**:

```json
{
  "account": "user@example.com",
  "password": "P@ssw0rd123!"
}
```

- **响应头**:

```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "username": "string",
    "email": "string",
    "refresh_token": "string",
    "ip_address": "string"
  }
}
```

- **Cookie**: `access_token=Bearer <token>; HttpOnly; Secure; Path=/; SameSite=Strict; Max-Age=1800`
- **速率限制**: 10 次/分钟

### 1.4 邮箱登录发送验证码

- **接口**: `/users/send_verification_code_by_email`
- **方法**: `POST`
- **功能**: 发送邮箱验证码
- **请求体**:

```json
{
  "refresh_token": "xxxxxx.xxxxx.xxxxx"
}
```

### 1.5 邮箱验证码登录

- **接口**: `/users/login_by_email`
- **方法**: `POST`
- **功能**: 发送邮箱验证码
- **请求体**:

```json
{
  "email": "user@example.com",
  "code": "123456"
}
```

- **安全限制**:
  - 验证码有效期5分钟
  - 每个邮箱每天最多发送10次

### 1.6 忘记密码发送验证码

- **接口**: `/users/send_verification_code_by_email`
- **方法**: `POST`
- **功能**: 发送忘记密码验证码
- **请求体**:

```json
{
  "email": "user@example.com"
}
```

### 1.7 忘记密码验证码

- **接口**: `/users/forgot_password_by_email`
- **方法**: `POST`
- **功能**: 发送忘记密码验证码
- **请求体**:

```json
{
  "email": "user@example.com",
  "code": "123456",
  "password": "P@ssw0rd123!"
}
```

### 1.8 刷新令牌
```json
{
  "code": 200,
  "message": "令牌刷新成功",
  "data": {
    "username": "string"
  }
}
```

- **Cookie**: 更新访问令牌（同登录）
- **速率限制**: 20 次/分钟

### 1.9 用户登出

- **接口**: `/users/logout`
- **方法**: `GET`
- **功能**: 用户登出并使当前令牌失效
- **请求头**: `Authorization: Bearer <token>`
- **响应**:

```json
{
  "code": 200,
  "message": "退出登录成功",
  "data": null
}
```

- **Cookie**: 清除访问令牌

## 2. 用户管理模块 (Users)

### 2.1 获取当前用户信息

- **接口**: `/api/users/current`
- **方法**: `GET`
- **功能**: 获取当前登录用户的信息
- **请求头**: `Authorization: Bearer <token>`
- **响应**:

```json
{
    "code": 200,
    "message": "success",
    "data": {
        "id": number,
        "username": "string",
        "email": "string",
        "phone": "string",
        "is_admin": boolean,
        "is_active": boolean,
        "ip_address": "string",
        "last_login": "string",
        "created_at": "string",
        "updated_at": "string"
    }
}
```

### 2.2 获取用户 IP 历史

- **接口**: `/api/users/ip_history/{user_id}`
- **方法**: `GET`
- **功能**: 获取指定用户的 IP 地址历史记录
- **请求头**: `Authorization: Bearer <token>`
- **响应**:

```json
{
  "code": 200,
  "message": "获取用户IP历史成功",
  "data": {
    "current_ip": "string",
    "last_login": "string",
    "user_info": {
      "username": "string",
      "email": "string"
    }
  }
}
```

### 2.3 创建用户（管理员）

- **接口**: `/api/users`
- **方法**: `POST`
- **功能**: 管理员创建新用户
- **权限**: 需要管理员权限
- **请求头**: `Authorization: Bearer <token>`
- **请求体**:

```json
{
    "username": "string",
    "email": "string",
    "phone": "string",
    "password": "string",
    "is_admin": boolean,
    "is_active": boolean
}
```

- **响应**:

```json
{
    "code": 200,
    "message": "用户创建成功",
    "data": {
        "id": number,
        "username": "string",
        "email": "string",
        "phone": "string",
        "is_admin": boolean,
        "is_active": boolean,
        "created_at": "string",
        "updated_at": "string"
    }
}
```

- **速率限制**: 20 次/分钟

### 2.4 更新用户（管理员）

- **接口**: `/api/users/{user_id}`
- **方法**: `PUT`
- **功能**: 更新用户全部信息
- **权限**: 需要管理员权限
- **请求头**: `Authorization: Bearer <token>`
- **请求体**: 同创建用户
- **响应**: 同创建用户，message 为 "用户更新成功"

### 2.5 更新用户字段（管理员）

- **接口**: `/api/users/{user_id}`
- **方法**: `PATCH`
- **功能**: 更新用户部分字段
- **权限**: 需要管理员权限
- **请求头**: `Authorization: Bearer <token>`
- **请求体**: 需要更新的字段
- **响应**: 同更新用户，message 为 "用户字段更新成功"

### 2.6 删除用户（管理员）

- **接口**: `/api/users/{user_id}`
- **方法**: `DELETE`
- **功能**: 删除指定用户
- **权限**: 需要管理员权限
- **请求头**: `Authorization: Bearer <token>`
- **响应**:

```json
{
  "code": 200,
  "message": "用户删除成功",
  "data": null
}
```

## 3. 产品管理模块 (Products)

### 3.1 获取产品列表

- **接口**: `/api/products`
- **方法**: `GET`
- **功能**: 获取所有产品列表
- **查询参数**:
  - `page`: 页码 (可选)
  - `limit`: 每页数量 (可选)
  - `category`: 产品类别 (可选)
- **响应**:

```json
{
    "code": 200,
    "message": "success",
    "data": {
        "items": [
            {
                "id": number,
                "name": "string",
                "description": "string",
                "price": number,
                "category": "string",
                "stock": number,
                "created_at": "string",
                "updated_at": "string"
            }
        ],
        "total": number,
        "page": number,
        "limit": number
    }
}
```

- **速率限制**: 100 次/分钟

### 3.2 创建产品

- **接口**: `/api/products`
- **方法**: `POST`
- **功能**: 创建新产品
- **权限**: 需要管理员权限
- **请求体**:

```json
{
    "name": "string",
    "description": "string",
    "price": number,
    "category": "string",
    "stock": number
}
```

- **响应**:

```json
{
  "code": 200,
  "message": "产品创建成功",
  "data": {
    // 产品完整信息
  }
}
```

- **速率限制**: 20 次/分钟

### 3.3 获取产品详情

- **接口**: `/api/products/{product_id}`
- **方法**: `GET`
- **功能**: 获取指定产品的详细信息
- **响应**:

```json
{
    "code": 200,
    "message": "success",
    "data": {
        "id": number,
        "name": "string",
        "description": "string",
        "price": number,
        "category": "string",
        "stock": number,
        "created_at": "string",
        "updated_at": "string"
    }
}
```

### 3.4 更新产品

- **接口**: `/api/products/{product_id}`
- **方法**: `PUT`
- **功能**: 更新产品信息
- **权限**: 需要管理员权限
- **请求体**: 同创建产品
- **响应**:

```json
{
  "code": 200,
  "message": "产品更新成功",
  "data": {
    // 产品完整信息
  }
}
```

### 3.5 删除产品

- **接口**: `/api/products/{product_id}`
- **方法**: `DELETE`
- **功能**: 删除指定产品
- **权限**: 需要管理员权限
- **响应**:

```json
{
  "code": 200,
  "message": "产品删除成功",
  "data": null
}
```

### 3.6 按名称搜索产品

- **接口**: `/api/products/name/{product_name}`
- **方法**: `GET`
- **功能**: 根据产品名称搜索产品
- **响应**:

```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      // 产品信息
    }
  ]
}
```

## 通用说明

### 状态码

- 200: 成功
- 400: 请求错误
- 401: 未授权
- 403: 禁止访问
- 404: 资源不存在
- 422: 请求数据验证失败
- 429: 请求过于频繁
- 500: 服务器错误

### 认证方式

- 访问令牌: 通过 HttpOnly Cookie 传递，有效期 30 分钟
- 刷新令牌: 通过响应体返回，有效期 7 天

### 用户状态

- `is_active`: 账户激活状态（true: 已激活，false: 未激活或被禁用）
- `is_admin`: 管理员权限（true: 管理员，false: 普通用户）
- `is_deleted`: 删除状态（true: 已删除，false: 正常）

### 速率限制

- 登录接口: 10 次/分钟
- 注册预检: 5 次/分钟
- 注册验证: 20 次/分钟
- 管理员接口: 20 次/分钟
- 普通查询接口: 100 次/分钟
