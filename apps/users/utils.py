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

import time
import struct

class Snowflake:
    '''
    雪花算法生成用户id
    '''
    def __init__(self, worker_id=0, data_center_id=0):
        self.worker_id = worker_id
        self.data_center_id = data_center_id
        self.sequence = 0
        self.timestamp_left_shift = 22
        self.worker_id_bits = 5
        self.data_center_id_bits = 5
        self.max_worker_id = -1 ^ (-1 << self.worker_id_bits)
        self.max_data_center_id = -1 ^ (-1 << self.data_center_id_bits)
        self.sequence_mask = -1 ^ (-1 << 12)
        self.twepoch = 1609459200000  # 2021-01-01 00:00:00.000Z

    def _tilt(self, timestamp):
        return timestamp - self.twepoch

    def _generate_id(self, timestamp):
        id = timestamp << self.timestamp_left_shift
        id |= self.data_center_id << (self.timestamp_left_shift - self.data_center_id_bits)
        id |= self.worker_id << (self.timestamp_left_shift - self.worker_id_bits - self.data_center_id_bits)
        id |= self.sequence
        return id

    def generate(self):
        timestamp = int(time.time() * 1000)
        tilted = self._tilt(timestamp)
        if tilted < 0:
            raise Exception("Clock is moving backwards")
        id = self._generate_id(tilted)
        self.sequence = (self.sequence + 1) & self.sequence_mask
        return id

def generate_user_id():
    '''
    生成用户id
    '''
    snowflake = Snowflake()
    return snowflake.generate()


async def send_verification_email(email: str, code: str, username: str = None) -> bool:
    """
    发送邮箱验证码
    :param email: 收件人邮箱
    :param code: 验证码
    :return: 是否发送成功
    """
    try:
        logger.info(f"Preparing to send verification email to: {email}")
        
        # 创建邮件内容
        message = MIMEMultipart()
        message['From'] = f"{SMTP_FROM_NAME} <{SMTP_FROM_EMAIL}>"
        message['To'] = email
        message['Subject'] = "RobynVue - 注册验证码"

        if not username:
            username = ""
            
        # 邮件正文
        body = f"""
        尊敬的用户{username}：
        
        您好！感谢您注册 RobynVue。
        
        您的验证码是：{code}
        
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





