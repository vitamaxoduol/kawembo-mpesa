# from dotenv import load_dotenv
# import redis
import os
from datetime import timedelta
import configparser

# Loading the .env file
# load_dotenv()
config = configparser.ConfigParser()
config.read("config.ini")

class Config:
    # Define constant variables for the project
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///data_base.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True
    # SECRET_KEY = os.environ['SECRET_KEY']

    SESSION_TYPE = 'redis'
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    # SESSION_REDIS = redis.from_url('redis://127.0.0.1:6379')
    # SESSION_REDIS = redis.from_url(os.environ.get('REDIS_URL', 'redis://red-ckvtnp3amefc73bpiip0:6379'))

    # Additional JWT Configurations
    JWT_SECRET_KEY = os.urandom(32).hex()
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access']
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=2)


    # Email config
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USERNAME = 'Derexfinesse@gmail.com'
    MAIL_PASSWORD = "gggx zsjv rbsx reqi"
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True

#    MPESA CREDENTIALS
    BASE_URL = " https://sandbox.safaricom.co.ke/mpesa/"

    CONSUMER_KEY = os.getenv('key')
    CONSUMER_SECRET = os.getenv('ConsumerSecret')
    SECURITY_CREDENTIALS = os.getenv('securitycredentials')
    PASSKEY = os.getenv("passkey")
    SHORT_CODE = os.getenv('shortcode')

    # url configurations
    CONFIRM_URL = config.get("URLS", "confirmurl")
    VALIDATE_URL = config.get("URLS", "validateurl")
    TIMEOUT_URL = config.get("URLS", "timeouturl")
    RESULT_URL = config.get("URLS", "resulturl")
    CALLBACK_URL = config.get("URLS", "callbackurl")