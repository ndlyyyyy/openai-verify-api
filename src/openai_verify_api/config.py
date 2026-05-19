from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    host: str = "127.0.0.1"
    port: int = 8000
    openai_verify_page_url: str = "https://openai.com/research/verify/"
    openai_verify_api_url: str = "https://openai.com/verify/api/provenance_checks"
    browser_headless: bool = True
    browser_humanize: bool = True
    navigation_timeout_ms: int = 120_000
    token_timeout_ms: int = 30_000
    upload_timeout_seconds: int = 120
    curl_impersonate: str = "chrome"

    model_config = SettingsConfigDict(env_prefix="OPENAI_VERIFY_", extra="ignore")


settings = Settings()
