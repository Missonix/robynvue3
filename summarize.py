"""
前后端的请求处理流程：

用户输入 URL 或点击链接：用户在浏览器地址栏输入 URL，或通过点击某个链接发起 HTTP 请求。
浏览器向后端服务器发送该 URL 的请求）。
后端接收请求并处理：后端服务器根据 URL 请求路径确定对应的路由。
如果路由指向一个 HTML 页面：后端从模板或静态文件中生成/加载 HTML 页面并将其发送给浏览器（HTML 响应）--现在HTML响应可以正常完成。

浏览器接收 HTML 文件并解析：浏览器接收到 HTML 响应后开始解析 HTML 内容，构建 DOM 树。--目前浏览器可以正确解析并且我能看到HTML界面
但是现在以下静态资源无法正常请求：
    浏览器请求静态资源：
    后端提供静态资源响应：
    后端接收到静态资源的请求，根据请求路径返回对应的 CSS、JS 文件或图片等资源。
    浏览器渲染页面：
    浏览器解析和应用 CSS 文件更新页面样式。
    浏览器加载并执行 JS 文件，为页面添加交互功能。



Robyn框架语法及内置方法

作用：增加路由映射
app.add_directory(router="/static", directory_path="static", index_file="index.html")

作用：增加路由映射
app.add_route(route_type="POST", endpoint="/users/login", handler=login_user_view)



"""