class Config(object):
    DEBUG = False
    TESTING = False

    SECRET_KEY = 'the waters'

    DB_NAME = 'production-db'
    DB_USERNAME = 'root'
    DB_PASSWORD = ''
    MAX_IMAGE_FILESIZE = 0.5 * 1024 * 1024
    # IMAGE_UPLOADS="/home/zakhele/Documents/app/app/static/img"
    
    UPLOADS="/home/mshengu/Desktop/mysql-matcha/app/static/img"
    SESSION_COOKIE_SECURE = True



class ProductionConfig(Config):
    SECRET_KEY = 'the waters'

class DevelopmentConfig(Config):
    DEBUG = True
    SECRET_KEY = 'the waters'
    
    
    #init email
    MAIL_SERVER='smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USERNAME = 'mzekemadi@gmail.com'
    MAIL_PASSWORD = '181991Ma'
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True

    DB_NAME="develpment-db"
    DB_USERNAME="root"
    DB_PASSWORD=""
    IMAGE_UPLOADS = "/home/mshengu/Desktop/mysql-matcha/app/static/img"
    ALLOWED_IMAGE_EXTENSIONS = ["PNG","JPG","JPEG","GIF"]

    UPLOADS="/home/mshengu/Desktop/mysql-matcha/app/static/img"
    SESSION_COOKIE_SECURE=False

class TestingConfig(Config):
    TESTING=True

    DB_NAME="production-db"
    DB_USERNAME="root"
    DB_PASSWORD=""
    SECRET_KEY = 'the waters'

    UPLOADS ="/home/mshengu/Desktop/mysql-matcha/app/static/img"
    SESSION_COOKIE_SECURE=False