"""Google Drive integration for uploading resumes."""

import logging
from typing import Optional
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError


logger = logging.getLogger(__name__)


class GoogleDriveUploader:
    """Uploads files to Google Drive."""

    def __init__(self, folder_id: str = None):
        """Initialize Google Drive client."""
        self.folder_id = folder_id

        try:
            # Build Drive service
            self.service = build('drive', 'v3')
            logger.info("Initialized Google Drive client")
        except Exception as e:
            logger.error(f"Error initializing Google Drive: {str(e)}")
            self.service = None

    def upload_file(
        self,
        file_path: str,
        folder_id: str = None,
        file_name: str = None
    ) -> Optional[str]:
        """
        Upload file to Google Drive.

        Args:
            file_path: Path to file to upload
            folder_id: Google Drive folder ID (optional)
            file_name: Name for the file in Drive (optional)

        Returns:
            File ID if successful, None otherwise
        """
        if not self.service:
            logger.error("Google Drive service not initialized")
            return None

        try:
            file_path = Path(file_path)
            if not file_path.exists():
                logger.error(f"File not found: {file_path}")
                return None

            # Use provided folder ID or default
            target_folder = folder_id or self.folder_id

            # Prepare file metadata
            file_metadata = {
                'name': file_name or file_path.name
            }

            if target_folder:
                file_metadata['parents'] = [target_folder]

            # Determine MIME type
            mime_type = self._get_mime_type(file_path.suffix)

            # Upload file
            media = MediaFileUpload(
                str(file_path),
                mimetype=mime_type,
                resumable=True
            )

            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, webViewLink'
            ).execute()

            file_id = file.get('id')
            web_link = file.get('webViewLink')

            logger.info(f"Uploaded file to Google Drive: {file_path.name}")
            logger.info(f"Drive link: {web_link}")

            return file_id

        except HttpError as e:
            logger.error(f"Google Drive API error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error uploading to Google Drive: {str(e)}")
            return None

    def get_file_link(self, file_id: str) -> Optional[str]:
        """Get shareable link for a file."""
        if not self.service:
            return None

        try:
            # Make file readable by anyone with link
            permission = {
                'type': 'anyone',
                'role': 'reader'
            }

            self.service.permissions().create(
                fileId=file_id,
                body=permission
            ).execute()

            # Get file metadata with webViewLink
            file = self.service.files().get(
                fileId=file_id,
                fields='webViewLink'
            ).execute()

            return file.get('webViewLink')

        except Exception as e:
            logger.error(f"Error getting file link: {str(e)}")
            return None

    def create_folder(self, folder_name: str, parent_id: str = None) -> Optional[str]:
        """Create a folder in Google Drive."""
        if not self.service:
            return None

        try:
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }

            if parent_id:
                file_metadata['parents'] = [parent_id]

            folder = self.service.files().create(
                body=file_metadata,
                fields='id'
            ).execute()

            folder_id = folder.get('id')
            logger.info(f"Created folder: {folder_name} (ID: {folder_id})")

            return folder_id

        except Exception as e:
            logger.error(f"Error creating folder: {str(e)}")
            return None

    def list_files(self, folder_id: str = None, max_results: int = 100) -> list:
        """List files in a folder."""
        if not self.service:
            return []

        try:
            query = f"'{folder_id}' in parents" if folder_id else None

            results = self.service.files().list(
                q=query,
                pageSize=max_results,
                fields="files(id, name, mimeType, createdTime, webViewLink)"
            ).execute()

            files = results.get('files', [])
            return files

        except Exception as e:
            logger.error(f"Error listing files: {str(e)}")
            return []

    def _get_mime_type(self, extension: str) -> str:
        """Get MIME type from file extension."""
        mime_types = {
            '.pdf': 'application/pdf',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.doc': 'application/msword',
            '.txt': 'text/plain',
            '.json': 'application/json',
            '.html': 'text/html'
        }

        return mime_types.get(extension.lower(), 'application/octet-stream')
