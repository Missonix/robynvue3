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
- [views接口](#views接口)
  - [新建会话接口](#新建会话接口)
  - [获取会话列表接口](#获取会话列表接口)
  - [删除单个会话](#删除单个会话)
  - [获取单个会话](#获取单个会话)


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

## views接口

### 新建会话接口
**POST** `/aichat/createsession`

请求体：
```json
{
    "user_id": "544112870296649728",
    "title": "全世界面积最大的岛是哪个岛？",
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNTQ0MTEyODcwMjk2NjQ5NzI4IiwiZXhwIjoxNzM5MjAxMTUwLCJpYXQiOjE3MzkxOTkzNTAsInR5cGUiOiJhY2Nlc3MifQ.wqIpOn0NbJSgHA9JXN-8iwFS2Lpksmf_qBh-ya9uXTM"
}
```

成功响应：
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "session_id": "54c1e4b6-8763-47c5-8ac4-ca7da479b3ce",
        "user_id": "544112870296649728",
        "title": "全世界面积最大的岛是哪个岛？",
        "message_count": 0,
        "created_at": "2025-02-10T15:02:54.393249",
        "updated_at": "2025-02-10T15:02:54.393249",
        "is_deleted": false
    }
}
```

### 获取会话列表接口
**GET** `/aichat/getsessionlist/:user_id`

成功响应：
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "list": [
            {
                "session_id": "ec2f73f1-5210-495b-90c1-80f69ac36f19",
                "user_id": "544112870296649728",
                "title": "机器学习介绍",
                "message_count": 0,
                "created_at": "2025-02-10T14:37:49.495447",
                "updated_at": "2025-02-10T14:37:49.495447",
                "is_deleted": false
            },
            {
                "session_id": "89662873-e48a-4a9b-902d-48d3932de006",
                "user_id": "544112870296649728",
                "title": "数学技巧",
                "message_count": 0,
                "created_at": "2025-02-10T14:37:43.339597",
                "updated_at": "2025-02-10T14:37:43.339597",
                "is_deleted": false
            },
            ...
        ],
        "pagination": {
            "total": 21,
            "pageSize": 20,
            "pageNum": 1,
            "totalPages": 2
        }
    }
}
```

### 删除会话接口
**DELETE** `/aichat/deletesession/:session_id`

成功响应：
```json
{
    "code": 200,
    "message": "success",
    "data": "会话删除成功"
}
```





---

> 注意：所有接口均需在请求头中携带有效的访问令牌：
> `Authorization: Bearer <access_token>`

