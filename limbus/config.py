class Config:
    SUPPORTED_LANGUAGES = {"en": "English", "cy": "Cymraeg"}
    BABEL_DEFAULT_LOCALE = "en"

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True

class ProductionConfig(Config):
    DEBUG = False

app_config = {
    "dev" : DevelopmentConfig,
    "prod" : ProductionConfig
}