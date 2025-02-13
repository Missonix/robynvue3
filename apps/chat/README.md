# AI 聊天应用接口文档

## 目录
- [模型结构](#模型结构)
- [crud基础数据库查询](#crud基础数据库查询)
- [会话管理](#会话管理)
  - [创建会话](#创建会话)
  - [获取会话](#获取会话)
  - [删除会话](#删除会话)
  - [更新会话标题](#更新会话标题)
- [消息管理](#消息管理)
  - [发送消息](#发送消息)
  - [获取消息](#获取消息)
  - [删除消息](#删除消息)
  - [修改消息](#修改消息)
- [视图路由接口](#视图路由接口)
  - [会话管理api](#会话管理api)
    - [获取会话列表api](#获取会话列表api)
    - [获取会话列表(用于消息首屏加载)](#获取会话列表用于消息首屏加载)
    - [获取单个会话api](#获取单个会话api)
    - [创建会话api](#创建会话api)
    - [更新会话标题api](#更新会话标题api)
    - [删除会话api](#删除会话api)
    - [获取会话消息api](#获取会话消息api)
- [Websocket通信](#Websocket通信)

---

## 模型结构

### 会话对象 (ChatSession)
```json
{
  "session_id": "123e4567-e89b-12d3-a456-426614174000",
  "user_id": "542738228948500480",
  "title": "新会话",
  "message_count": 0,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "is_deleted": false
}
```

### 消息对象 (ChatMessage)
```json
{
  "message_id": 1,
  "session_id": "123e4567-e89b-12d3-a456-426614174000",
  "role": "user",
  "content": "你好，世界！",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "is_deleted": false
}
```

---

## crud基础数据库查询
### 新建会话
```python
create_session(db, session_id, user_id, title="新会话")
```
- 接收: `session_id 和 user_id 和 title(可选)` 
- 返回: `创建的session对象`

### 查询单个会话
```python
get_session(db, session_id)
```
- 接收: `session_id`
- 返回: `查询的session对象列表`

### 批量查询会话(分页，一页20条)    
```python
list_sessions(
        db, 
        user_id,
        page,
        page_size
    )
```
- 接收: `user_id`
- 返回: `查询的session对象`

### 软删除单个会话
```python
soft_delete_session(db, session_id)
```
- 接收: `session_id`
- 返回: `bool`

### 更新会话标题
```python
update_session_title(db, session_id, new_title)
```
- 接收: `session_id`和`new_title(可选)`
- 返回: `bool`

### 新建消息
```python
create_message(
        db,
        session_id,
        content,
        role
    )
```
- 接收: `session_id`和`role`和`content`
- 返回: `创建的message对象`

### 查询单个消息(可拓展复杂查询)
```python
get_message(db, message_id)
```
- 接收: `message_id`
- 返回: `查询的message对象`

### 批量获取会话内消息(分页，一页50条)
```python
list_messages(
        db,
        session_id,
        page,
        page_size
    )
```
- 接收: `session_id`
- 返回: `查询的message对象列表`

### 软删除单个消息
```python
soft_delete_message(db, message_id)
```
- 接收: `message_id`
- 返回: `bool`

### 修改单个消息(仅限role:user的消息)
```python
update_message_content(db, message_id, new_content)
```
- 接收: `message_id`和`new_content`
- 返回: `bool`

---

## 会话管理

### 创建会话
**POST** `/api/chat/session`

请求体：
```json
{
  "user_id": "用户ID",
  "title": "技术讨论" //可有可无
}
```

成功响应：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "session_id": "123e4567-e89b-12d3-a456-426614174000",
    "user_id": "542738228948500480",
    "title": "技术讨论",
    "message_count": 0,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
    "is_deleted": false
  }
}
```

---

### 获取单个会话
**GET** `/api/chat/sessions/:session_id`


路径参数：
- `session_id`: 会话ID

成功响应：
```json
{
  "code": 200,
  "message": "success",
  "data": 
    {
      "session_id": "123e4567-e89b-12d3-a456-426614174000",
      "title": "技术讨论",
      "message_count": 5,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z",
      "is_deleted": false
    }
}
```

---

### 批量获取会话
**POST** `/api/chat/sessions`

请求体：
```json
{
  "user_id": "用户ID",
  "page": 1,
  "page_size": 50
}
```

成功响应：
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "session_id": "123e4567-e89b-12d3-a456-426614174000",
      "title": "技术讨论",
      "message_count": 5,
      "created_at": "2024-01-01T00:00:00Z"
    },
    ...
  ]
}
```

---

### 删除会话
**DELETE** `/api/chat/sessions/:session_id`

路径参数：
- `session_id`: 会话ID

成功响应：
```json
{
  "code": 200,
  "message": "success",
  "data": "会话删除成功"
}
```

---

### 更新会话标题
**PATCH** `/api/chat/sessions/:session_id`

请求体：
```json
{
  "new_title": "更新后的标题"
}
```

成功响应：
```json
{
  "code": 200,
  "message": "success",
  "data": "标题更新成功"
}
```

---

## 消息管理

### 发送消息
**POST** `/api/chat/message`

请求体：
```json
{
  "session_id": "123e4567-e89b-12d3-a456-426614174000",
  "content": "如何学习Python？",
  "role": "user"
}
```

成功响应：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "message_id": 1,
    "content": "如何学习Python？",
    "role": "user",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

---

### 获取单个消息
**GET** `/api/chat/sessions/:session_id/messages/:message_id`

路径参数：
- `session_id`: 会话ID
- `message_id`: 消息ID

成功响应：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "message_id": 1,
    "content": "你好！",
    "role": "user",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

---

### 获取批量消息
**GET** `/api/chat/sessions/:session_id/messages`

路径参数：
- `session_id`: 会话ID

#### 分页查询
**GET** `/api/chat/sessions/:session_id/messages?page=1&pageSize=50`

查询参数：
- `page`: 页码
- `page_size`: 每页数量

成功响应：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [
      {
        "message_id": 1,
        "content": "你好！",
        "role": "user",
        "created_at": "2024-01-01T00:00:00Z"
      }
    ],
    "total": 100,
    "page": 1,
    "page_size": 50
  }
}
```

---

### 删除消息
**DELETE** `/api/chat/messages/:message_id`

路径参数：
- `message_id`: 消息ID

成功响应：
```json
{
  "code": 200,
  "message": "success",
  "data": "消息删除成功"
}
```

---

### 修改消息
**PATCH** `/api/chat/messages/:message_id`

请求体：
```json
{
  "new_content": "更新后的消息内容"
}
```

成功响应：
```json
{
  "code": 200,
  "message": "success",
  "data": "消息编辑成功"
}
```


## 视图路由接口

### 会话管理api

#### 获取会话列表api
- **路径**: `/aichat/getsessionlist/:user_id`
- **方法**: GET
- **描述**: 获取指定用户的会话列表
- **参数**:
  - user_id: 用户ID (路径参数)
  - page: 页码 (查询参数，默认1)
  - page_size: 每页数量 (查询参数，默认20)
- **返回**: 会话列表及分页信息

#### 获取会话列表用于消息首屏加载
- **路径**: `/aichat/getsessionlistshow/:user_id`
- **方法**: GET
- **描述**: 获取会话列表，并包含最近一次更新会话的50条消息
- **参数**:
  - user_id: 用户ID (路径参数)
- **返回**: 会话列表(包含最新会话的消息)及分页信息

#### 获取单个会话api
- **路径**: `/aichat/sessions/:session_id`
- **方法**: GET
- **描述**: 获取单个会话详情
- **参数**:
  - session_id: 会话ID (路径参数)
- **返回**: 会话详情及最近50条消息

#### 创建会话api
- **路径**: `/aichat/createsession`
- **方法**: POST
- **描述**: 创建新的会话
- **请求体**:
  ```json
  {
    "user_id": "用户ID",
    "title": "会话标题(可选)"
  }
  ```
- **返回**: 新创建的会话信息

#### 更新会话标题api
- **路径**: `/aichat/sessions/:session_id`
- **方法**: PATCH
- **描述**: 更新指定会话的标题
- **参数**:
  - session_id: 会话ID (路径参数)
- **请求体**:
  ```json
  {
    "new_title": "新标题"
  }
  ```
- **返回**: 更新成功确认

#### 删除会话api
- **路径**: `/aichat/deletesession/:session_id`
- **方法**: DELETE
- **描述**: 删除指定会话
- **参数**:
  - session_id: 会话ID (路径参数)
- **返回**: 删除成功确认

#### 获取会话消息api
- **路径**: `/aichat/sessions/:session_id/messages`
- **方法**: GET
- **描述**: 获取指定会话的历史消息
- **参数**:
  - session_id: 会话ID (路径参数)
  - page: 页码 (查询参数，默认1)
  - pageSize: 每页数量 (查询参数，默认50)
- **返回**: 消息列表



## 响应格式

所有API返回的数据格式统一为：
```json
{
"code": 200, // 状态码
"message": "", // 消息
"data": {} // 数据
}
```

## Websocket通信
- **路径**: `/ws/:session_id`



---

> 注意：所有接口均需在请求头中携带有效的访问令牌：
> `Authorization: Bearer <access_token>`

