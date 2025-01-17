import os
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import aiosmtplib
from robyn import Response, status_codes
from dotenv import load_dotenv
from pathlib import Path
from core.logger import setup_logger

# 设置日志记录器
logger = setup_logger('user_utils')

# 获取项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# 加载环境变量，指定.env文件路径
load_dotenv(os.path.join(BASE_DIR, "robyn.env"))

# SMTP配置
SMTP_SERVER = 'smtp.163.com'  # 电子邮箱服务器的域名
SMTP_PORT = 25  # SSL/TLS加密端口
SMTP_USERNAME = 'ackerman0919@163.com'  # 网站官方邮箱地址
SMTP_PASSWORD = 'XZfLeejapK58EuVS'  # 邮箱接口授权码
SMTP_USE_TLS = False  # 使用 SSL/TLS 加密
SMTP_FROM_EMAIL = 'ackerman0919@163.com'  # 网站官方邮箱地址
SMTP_FROM_NAME = 'RobynVue'  # 网站名称

async def send_verification_email(email: str, verification_code: str) -> bool:
    """
    发送邮箱验证码
    :param email: 收件人邮箱
    :param verification_code: 验证码
    :return: 是否发送成功
    """
    try:
        logger.info(f"Preparing to send verification email to: {email}")
        
        # 创建邮件内容
        message = MIMEMultipart()
        message['From'] = f"{SMTP_FROM_NAME} <{SMTP_FROM_EMAIL}>"
        message['To'] = email
        message['Subject'] = "RobynVue - 注册验证码"

        # 邮件正文
        body = f"""
        尊敬的用户：
        
        您好！感谢您注册 RobynVue。
        
        您的验证码是：{verification_code}
        
        该验证码将在5分钟后失效，请尽快完成注册。
        
        如果这不是您的操作，请忽略此邮件。
        
        祝您使用愉快！
        RobynVue 团队
        """
        message.attach(MIMEText(body, 'plain', 'utf-8'))

        # 使用异步SMTP客户端发送邮件
        try:
            async with aiosmtplib.SMTP(hostname=SMTP_SERVER, 
                                     port=SMTP_PORT, 
                                     use_tls=SMTP_USE_TLS) as server:
                await server.login(SMTP_USERNAME, SMTP_PASSWORD)
                await server.send_message(message)
                
            logger.info(f"Verification email sent successfully to: {email}")
            return True
            
        except aiosmtplib.SMTPException as smtp_error:
            logger.error(f"SMTP error while sending email: {str(smtp_error)}")
            return False
            
    except Exception as e:
        logger.error(f"Failed to send verification email: {str(e)}")
        return False

def generate_numeric_verification_code(length: int = 6) -> str:
    """
    生成指定长度的数字验证码
    :param length: 验证码长度，默认6位
    :return: 数字验证码字符串
    """
    # 生成指定长度的随机数字
    verification_code = ''.join([str(random.randint(0, 9)) for _ in range(length)])
    return verification_code





