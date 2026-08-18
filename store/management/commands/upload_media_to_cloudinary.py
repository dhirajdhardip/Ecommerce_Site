"""Management command to upload all local media files to Cloudinary.

Run this once after setting up Cloudinary credentials:
    python manage.py upload_media_to_cloudinary
"""

import os

from django.conf import settings
from django.core.management.base import BaseCommand

import cloudinary
import cloudinary.uploader


class Command(BaseCommand):
    help = "Upload all local media files to Cloudinary for production use."

    def handle(self, *args, **options):
        cloud_name = settings.CLOUDINARY_STORAGE.get("CLOUD_NAME")
        api_key = settings.CLOUDINARY_STORAGE.get("API_KEY")
        api_secret = settings.CLOUDINARY_STORAGE.get("API_SECRET")

        if not all([cloud_name, api_key, api_secret]):
            self.stderr.write(self.style.ERROR(
                "Cloudinary credentials not configured. "
                "Set CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, "
                "and CLOUDINARY_API_SECRET environment variables."
            ))
            return

        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret,
            secure=True,
        )

        media_root = settings.MEDIA_ROOT
        if not os.path.exists(media_root):
            self.stderr.write(self.style.ERROR(
                f"Media root does not exist: {media_root}"
            ))
            return

        uploaded = 0
        skipped = 0
        errors = 0

        for dirpath, _dirnames, filenames in os.walk(media_root):
            for filename in filenames:
                if filename.startswith("."):
                    continue

                local_path = os.path.join(dirpath, filename)
                # Build the Cloudinary public_id matching Django's upload_to
                relative_path = os.path.relpath(local_path, media_root)
                public_id = os.path.splitext(relative_path)[0]

                try:
                    result = cloudinary.uploader.upload(
                        local_path,
                        public_id=public_id,
                        resource_type="auto",
                        overwrite=False,
                        unique_filename=False,
                        use_filename=True,
                    )
                    self.stdout.write(self.style.SUCCESS(
                        f"  ✓ Uploaded: {relative_path} -> {result['secure_url']}"
                    ))
                    uploaded += 1
                except Exception as exc:
                    self.stderr.write(self.style.WARNING(
                        f"  ✗ Error uploading {relative_path}: {exc}"
                    ))
                    errors += 1

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(
            f"Done! Uploaded: {uploaded}, Skipped: {skipped}, Errors: {errors}"
        ))
