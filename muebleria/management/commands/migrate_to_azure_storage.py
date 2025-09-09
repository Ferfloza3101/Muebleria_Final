"""
Management command to migrate existing media files to Azure Blob Storage
"""
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from azure.storage.blob import BlobServiceClient
from pathlib import Path

class Command(BaseCommand):
    help = 'Migrate existing media files to Azure Blob Storage'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be uploaded without actually uploading',
        )

    def handle(self, *args, **options):
        # Check if Azure Storage is configured
        account_name = os.environ.get('AZURE_STORAGE_ACCOUNT_NAME')
        account_key = os.environ.get('AZURE_STORAGE_ACCOUNT_KEY')
        container_name = os.environ.get('AZURE_STORAGE_CONTAINER_NAME', 'media')

        if not account_name or not account_key:
            self.stdout.write(
                self.style.ERROR('Azure Storage credentials not found in environment variables')
            )
            return

        # Initialize Azure Blob Service Client
        blob_service_client = BlobServiceClient(
            account_url=f"https://{account_name}.blob.core.windows.net",
            credential=account_key
        )

        # Get local media directory
        media_root = Path(settings.MEDIA_ROOT)
        if not media_root.exists():
            self.stdout.write(
                self.style.WARNING(f'Media directory {media_root} does not exist')
            )
            return

        # Upload files
        uploaded_count = 0
        skipped_count = 0
        error_count = 0

        for file_path in media_root.rglob('*'):
            if file_path.is_file():
                # Get relative path from media root
                relative_path = file_path.relative_to(media_root)
                blob_name = f"media/{relative_path.as_posix()}"

                try:
                    if options['dry_run']:
                        self.stdout.write(f'Would upload: {file_path} -> {blob_name}')
                        uploaded_count += 1
                    else:
                        # Check if blob already exists
                        blob_client = blob_service_client.get_blob_client(
                            container=container_name, 
                            blob=blob_name
                        )
                        
                        if blob_client.exists():
                            self.stdout.write(
                                self.style.WARNING(f'Skipping existing: {blob_name}')
                            )
                            skipped_count += 1
                            continue

                        # Upload file
                        with open(file_path, 'rb') as data:
                            blob_client.upload_blob(data, overwrite=True)
                        
                        self.stdout.write(f'Uploaded: {file_path} -> {blob_name}')
                        uploaded_count += 1

                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Error uploading {file_path}: {str(e)}')
                    )
                    error_count += 1

        # Summary
        if options['dry_run']:
            self.stdout.write(
                self.style.SUCCESS(f'Dry run complete. Would upload {uploaded_count} files')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Migration complete. Uploaded: {uploaded_count}, '
                    f'Skipped: {skipped_count}, Errors: {error_count}'
                )
            )
