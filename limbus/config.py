class Config:
    pass

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True

class ProductionConfig(Config):
    DEBUG = False

app_config = {
    "dev" : DevelopmentConfig,
    "prod" : ProductionConfig
}