from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    mongodb_url: str = "mongodb+srv://subh_25:12345SH@evcharging.gyy7knt.mongodb.net/?retryWrites=true&w=majority"
    database_name: str = "ev_charging_db"
    secret_key: str = "your-secret-key-here-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    class Config:
        env_file = ".env"

settings = Settings()