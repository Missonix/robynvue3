from settings import render_template


async def index_page_view(request):
    return render_template("station/index.html",request=request)

async def about_page_view(request):
    return render_template("station/about.html",request=request)

async def service_page_view(request):
    return render_template("station/service.html",request=request)

async def contact_page_view(request):
    return render_template("station/contact.html",request=request)

async def personal_page_view(request):
    username = request.identity.claims["user"]
    context = {
        "username": username
    }
    return render_template("station/personal.html",request=request, **context)

async def product_page_view(request):
    return render_template("station/product.html",request=request)

async def shop_page_view(request):
    return render_template("station/shop.html",request=request)

async def single_page_view(request):
    return render_template("station/single.html",request=request)

async def typography_page_view(request):
    return render_template("station/typography.html",request=request)

