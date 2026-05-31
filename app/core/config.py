from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "FaceRatioOps"
    app_version: str = "0.2.0"
    environment: str = "development"
    log_level: str = "INFO"
    max_upload_bytes: int = Field(default=5_242_880, description="Maximum upload size in bytes.")
    max_image_pixels: int = Field(default=12_000_000, description="Maximum decoded image pixel count.")
    max_inference_dimension: int = Field(
        default=1024,
        ge=64,
        le=8192,
        description="Longest image side (px) fed to the landmark model; larger images are downscaled first.",
    )
    max_detected_faces: int = Field(default=2, ge=1, le=5)
    min_detection_confidence: float = Field(default=0.5, ge=0.0, le=1.0)


@lru_cache
def get_settings() -> Settings:
    return Settings()
