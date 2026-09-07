from __future__ import annotations

from azure.core.credentials import AzureKeyCredential

from common.auth import get_token_credential
from common.config import Settings


def search_admin_credential():
    s = Settings()
    return AzureKeyCredential(s.search_admin_key) if s.search_admin_key else get_token_credential()


def search_query_credential():
    s = Settings()
    key = s.search_query_key or s.search_admin_key
    return AzureKeyCredential(key) if key else get_token_credential()
