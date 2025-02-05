# from apps.users.middlewares import BasicAuthHandler
# from robyn.authentication import BearerGetter
# from core.views import (
#     index_page_view,
#     about_page_view,
#     service_page_view,
#     contact_page_view,
#     personal_page_view,
#     product_page_view,
#     shop_page_view,
#     single_page_view,
#     typography_page_view,
# )



# def view_routes(app):
#     """
#     注册所有路由
#     """
#     app.configure_authentication(BasicAuthHandler(token_getter=BearerGetter())) # 配置认证

#     app.add_route(route_type="GET", endpoint="/", handler=index_page_view)
#     app.add_route(route_type="GET", endpoint="/index", handler=index_page_view)
#     app.add_route(route_type="GET", endpoint="/about", handler=about_page_view)
#     app.add_route(route_type="GET", endpoint="/service", handler=service_page_view)
#     app.add_route(route_type="GET", endpoint="/contact", handler=contact_page_view)
#     app.add_route(route_type="GET", endpoint="/personal", handler=personal_page_view, auth_required=True)
#     app.add_route(route_type="GET", endpoint="/product", handler=product_page_view)
#     app.add_route(route_type="GET", endpoint="/shop", handler=shop_page_view)
#     app.add_route(route_type="GET", endpoint="/single", handler=single_page_view)
#     app.add_route(route_type="GET", endpoint="/typography", handler=typography_page_view)



    



