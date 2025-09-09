"""
Azure Blob Storage configuration for Django
"""
from azure.storage.blob import BlobServiceClient
from django.conf import settings
import os

class AzureBlobStorage:
    def __init__(self):
        self.account_name = os.environ.get('AZURE_STORAGE_ACCOUNT_NAME')
        self.account_key = os.environ.get('AZURE_STORAGE_ACCOUNT_KEY')
        self.container_name = os.environ.get('AZURE_STORAGE_CONTAINER_NAME', 'media')
        
        if self.account_name and self.account_key:
            self.blob_service_client = BlobServiceClient(
                account_url=f"https://{self.account_name}.blob.core.windows.net",
                credential=self.account_key
            )
        else:
            self.blob_service_client = None
    
    def upload_file(self, file, blob_name):
        """Upload a file to Azure Blob Storage"""
        if not self.blob_service_client:
            return None
            
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name, 
                blob=blob_name
            )
            blob_client.upload_blob(file, overwrite=True)
            return f"https://{self.account_name}.blob.core.windows.net/{self.container_name}/{blob_name}"
        except Exception as e:
            print(f"Error uploading file: {e}")
            return None
    
    def delete_file(self, blob_name):
        """Delete a file from Azure Blob Storage"""
        if not self.blob_service_client:
            return False
            
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name, 
                blob=blob_name
            )
            blob_client.delete_blob()
            return True
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False
    
    def get_file_url(self, blob_name):
        """Get the public URL for a file"""
        if not self.account_name:
            return None
        return f"https://{self.account_name}.blob.core.windows.net/{self.container_name}/{blob_name}"

# Global instance
azure_storage = AzureBlobStorage()
