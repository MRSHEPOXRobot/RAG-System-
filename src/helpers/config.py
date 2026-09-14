from pydantic_settings import BaseSettings,SettingsConfigDict
# فائدة ال Pydantic هي 1: تحميل القيم من ال .env
# التحقق من أنواع البيانات Validation
# تحويل البيانات للنوع المناسب Parsing 
class Settings(BaseSettings): # class settings inherts from class BaseSettings
    APP_NAME : str
    APP_VERSION : str

    FILE_ALLOWED_TYPES: list
    FILE_MAX_SIZE : int
    FILE_DEFAULT_CHUNK_SIZE : int

    MONGODB_URL : str
    MONGODB_DATABASE : str

    #Mandatory values
    GENERATION_BACKEND : str
    EMBEDDING_BACKEND : str

    OPENAI_API_KEY : str = None
    OPENAI_API_URL : str = None
    COHERE_API_KEY : str = None

    GENERATION_MODEL_ID : str = None
    EMBEDDING_MODEL_ID : str = None
    EMBEDDING_MODEL_SIZE : str = None

    INPUT_DEFAULT_MAX_CHARACTERS : int = None
    GENERATION_DEFAULT_MAX_TOKENS : int = None
    GENERATION_DEFAULT_TEMPERATURE : float = None

    VECTOR_DB_BACKEND : str
    VECTOR_DB_PATH : str
    VECTOR_DB_DISTANCE_METHOD : str = None

    DEFAULT_LANG: str = "eng" # Default language for the application
    PRIMARY_LANG: str = "eng" # Primary language for the application

    class Config:
        env_file = ".env" # كل إلي في ال .env هيحصله loaded ويتحول لكلاس أقدر أستخدمه

def get_settings():
    return Settings() # return object from Settings