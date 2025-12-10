from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseModel):
    HASHNODE_TOKEN: str | None = os.getenv("HASHNODE_TOKEN", "a6b35612-92c1-464a-953f-f0b105de8026")
    HASHNODE_PUBLICATION_ID: str | None = os.getenv("HASHNODE_PUBLICATION_ID")

    LINKEDIN_ACCESS_TOKEN: str | None = os.getenv("LINKEDIN_ACCESS_TOKEN")
    FACEBOOK_PAGE_ACCESS_TOKEN: str | None = os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN")
    FACEBOOK_PAGE_ID: str | None = os.getenv("FACEBOOK_PAGE_ID")
    INSTAGRAM_ACCESS_TOKEN: str | None = os.getenv("INSTAGRAM_ACCESS_TOKEN")
    INSTAGRAM_BUSINESS_ID: str | None = os.getenv("INSTAGRAM_BUSINESS_ID")

    ELEVENLABS_API_KEY: str | None = os.getenv("ELEVENLABS_API_KEY", "sk_bcdb849f7a903076c4fb58d06a7cce041dd170154c4373f1")
    OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")

    ARTIFACTS_DIR: str = os.getenv("ARTIFACTS_DIR", "artifacts")
    ELEVEN_LABS_API: str = os.getenv("ELEVEN_LABS_API", "https://api.elevenlabs.io/v1")
    RUNWAY_API: str = os.getenv("RUNWAY_API", "https://api.runwayml.com/v1")


settings = Settings()

