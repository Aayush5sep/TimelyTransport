import re
import warnings
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from router import router


# Ignore Deprecation Warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

app = FastAPI()

class RegexCORSMiddleware(CORSMiddleware):
    def is_allowed_origin(self, origin: str) -> bool:
        for pattern in self.allow_origins:
            if re.fullmatch(pattern, origin):
                return True
        return False

allowed_origins = [
    "*",
]

app.add_middleware(
    RegexCORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)