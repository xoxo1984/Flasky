import os, configparser

basedir = os.path.abspath(os.path.dirname(__file__))
config = configparser.ConfigParser()
config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.ini') #assume that config.py and config.ini are in the save directory
config.read(config_path)


class Config:
    SECRET_KEY = config['SECURITY']['SECRET_KEY']
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = config['MAIL']['MAIL_SERVER']
    MAIL_PORT = config['MAIL']['MAIL_PORT']
    MAIL_USE_SSL = config['MAIL']['MAIL_USE_SSL']
    MAIL_USERNAME = [config['MAIL']['MAIL_USERNAME']]
    MAIL_PASSWORD = config['MAIL']['MAIL_PASSWORD']
    FLASKY_MAIL_SUBJECT_PREFIX = config['MAIL']['FLASKY_MAIL_SUBJECT_PREFIX']
    FLASKY_MAIL_SENDER = config['MAIL']['FLASKY_MAIL_SENDER']
    FLASKY_ADMIN = config['MAIL']['FLASKY_ADMIN']

    FLASKY_POST_PER_PAGE = 20
    FLASKY_FOLLOWERS_PER_PAGE = 20
    SQLALCHEMY_RECORD_QUERIES = True
    FLASKY_SLOW_DB_QUERY_TIME = 0.005

    try:
        UPLOADED_PHOTOS_DEST = os.path.join(basedir, 'app/static/avatar')
    except:
        UPLOADED_PHOTOS_DEST = os.path.join(basedir, 'app\\static\\avatar')

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    TYPE = config['DATABASE']['TYPE']
    DRIVER = config['DATABASE']['DRIVER']
    ACCOUNT = config['DATABASE']['ACCOUNT']
    PASSWORD = config['DATABASE']['PASSWORD']
    HOST = config['DATABASE']['HOST']
    DATABASE = config['DATABASE']['DATABASE']
    SQLALCHEMY_DATABASE_URI = TYPE + '+' + DRIVER + '://' + ACCOUNT + ':' + PASSWORD + '@' + HOST + '/' + DATABASE


class TestingConfig(Config):
    TESTING = True
    TYPE = config['DATABASE']['TYPE']
    DRIVER = config['DATABASE']['DRIVER']
    ACCOUNT = config['DATABASE']['ACCOUNT']
    PASSWORD = config['DATABASE']['PASSWORD']
    HOST = config['DATABASE']['HOST']
    DATABASE = config['DATABASE']['DATABASE']
    SQLALCHEMY_DATABASE_URI = TYPE + '+' + DRIVER + '://' + ACCOUNT + ':' + PASSWORD + '@' + HOST + '/' + DATABASE
    WTF_CSRF_ENABLE = False


class ProductionConfig(Config):
    TYPE = config['DATABASE']['TYPE']
    DRIVER = config['DATABASE']['DRIVER']
    ACCOUNT = config['DATABASE']['ACCOUNT']
    PASSWORD = config['DATABASE']['PASSWORD']
    HOST = config['DATABASE']['HOST']
    DATABASE = config['DATABASE']['DATABASE']
    SQLALCHEMY_DATABASE_URI = TYPE + '+' + DRIVER + '://' + ACCOUNT + ':' + PASSWORD + '@' + HOST + '/' + DATABASE


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}
