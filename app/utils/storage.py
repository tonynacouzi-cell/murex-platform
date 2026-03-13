"""
Storage utility — Cloudinary (free 25GB)
Replaces AWS S3/MinIO for Railway + Vercel deployment.
Cloudinary free tier: 25GB storage, 25GB bandwidth/month, no credit card.
Sign up: https://cloudinary.com/users/register/free
"""

import cloudinary
import cloudinary.uploader
import cloudinary.api
from app.core.config import settings

cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True,
)


async def upload_media_file(file_bytes: bytes, filename: str, folder: str = "murex/media") -> dict:
    """
    Upload audio/video to Cloudinary.
    Returns: {public_id, secure_url, resource_type, bytes, format}
    """
    result = cloudinary.uploader.upload(
        file_bytes,
        folder=folder,
        resource_type="auto",        # auto-detects video/audio/image
        public_id=filename,
        overwrite=False,
        use_filename=True,
    )
    return {
        "public_id": result["public_id"],
        "secure_url": result["secure_url"],
        "resource_type": result["resource_type"],
        "bytes": result["bytes"],
        "format": result["format"],
    }


async def upload_image(file_bytes: bytes, filename: str, folder: str = "murex/images") -> dict:
    """Upload image (shopper photos, audit evidence)."""
    result = cloudinary.uploader.upload(
        file_bytes,
        folder=folder,
        public_id=filename,
        overwrite=False,
    )
    return {"public_id": result["public_id"], "secure_url": result["secure_url"]}


def get_media_url(public_id: str, resource_type: str = "video") -> str:
    """Get a signed URL for a stored media file."""
    return cloudinary.utils.cloudinary_url(
        public_id,
        resource_type=resource_type,
        secure=True,
    )[0]


def delete_media(public_id: str, resource_type: str = "video") -> bool:
    """Delete a media file from Cloudinary."""
    result = cloudinary.uploader.destroy(public_id, resource_type=resource_type)
    return result.get("result") == "ok"
