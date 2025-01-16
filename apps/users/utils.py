import hashlib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from robyn import Response, Robyn, status_codes
from dotenv import load_dotenv
from pathlib import Path

"""
    工具类 
"""

# 获取项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# 加载环境变量，指定.env文件路径
load_dotenv(os.path.join(BASE_DIR, "robyn.env"))


SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = int(os.getenv('SMTP_PORT'))
SMTP_USERNAME = os.getenv('SMTP_USERNAME')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
SMTP_USE_TLS = os.getenv('SMTP_USE_TLS').lower() == 'true'
SMTP_FROM_EMAIL = os.getenv('SMTP_FROM_EMAIL')
SMTP_FROM_NAME = os.getenv('SMTP_FROM_NAME')



# 邮箱发送
async def send_email(email, verification_code):
    """
    发送邮箱验证码
    :param email: 收件人邮箱
    :param verification_code: 验证码
    """
    try:
        # 创建邮件内容
        message = MIMEMultipart()
        message['From'] = f"{SMTP_FROM_NAME} <{SMTP_FROM_EMAIL}>"
        message['To'] = email
        message['Subject'] = "验证码"

        # 邮件正文
        body = f"""
        您好！
        
        您的验证码是：{verification_code}
        
        验证码有效期为5分钟,请尽快使用。
        """
        message.attach(MIMEText(body, 'plain', 'utf-8')) # 添加邮件正文

        # 连接SMTP服务器
        async with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server: # 连接SMTP服务器
            if SMTP_USE_TLS:
                server.starttls() # 开启TLS加密
            await server.login(SMTP_USERNAME, SMTP_PASSWORD) # 登录SMTP服务器
            await server.send_message(message) # 发送邮件
        
        return Response(status_code=status_codes.HTTP_200_OK, message="邮件发送成功")
    except Exception as e:
        print(f"发送邮件失败: {str(e)}")
        return Response(status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR, message="邮件发送失败")


# 生成验证码
def generate_verification_code():
    return hashlib.sha256(os.urandom(32)).hexdigest()[:6]  # 哈希生成6位数随机验证码
    

# # 保存到缓存
# def save_to_cache(key, value, expire=300):
#     cache.set(key, value, expire)

# # 从缓存获取
# def get_from_cache(key):
#     return cache.get(key)

# # 删除缓存
# def delete_from_cache(key):
#     cache.delete(key)





