from apps.users.crud import check_email_exists
import asyncio

async def test_check_email_exists():
    email = "1297370884@qq.com"
    if not await check_email_exists(email):
        print("邮箱未被注册")
    else:
        print("邮箱已被注册")

if __name__ == "__main__":
    asyncio.run(test_check_email_exists())

