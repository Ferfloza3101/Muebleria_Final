"""
Custom storage backends for Azure Blob Storage
"""
from django.conf import settings
from storages.backends.azure_storage import AzureStorage
import os

class AzureMediaStorage(AzureStorage):
    account_name = os.environ.get('AZURE_STORAGE_ACCOUNT_NAME')
    account_key = os.environ.get('AZURE_STORAGE_ACCOUNT_KEY')
    azure_container = os.environ.get('AZURE_STORAGE_CONTAINER_NAME', 'media')
    expiration_secs = None
    file_overwrite = False
    custom_domain = f"{account_name}.blob.core.windows.net" if account_name else None

class AzureStaticStorage(AzureStorage):
    account_name = os.environ.get('AZURE_STORAGE_ACCOUNT_NAME')
    account_key = os.environ.get('AZURE_STORAGE_ACCOUNT_KEY')
    azure_container = os.environ.get('AZURE_STORAGE_CONTAINER_NAME', 'media')
    expiration_secs = None
    file_overwrite = False
    custom_domain = f"{account_name}.blob.core.windows.net" if account_name else None
