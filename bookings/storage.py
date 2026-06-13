"""
Custom storage backend that compresses images before uploading to Cloudinary.
This ensures large images (>10MB) are automatically resized to fit within
Cloudinary's free plan limits without the owner needing to resize manually.
"""

import io
from PIL import Image as PILImage


def compress_image(file, max_size_bytes=8 * 1024 * 1024, max_dimension=1920):
    """
    Compress an image file to fit within max_size_bytes.
    Resizes if needed and reduces quality progressively.
    Returns the compressed file as a BytesIO object.
    """
    try:
        # Open the image
        img = PILImage.open(file)

        # Convert RGBA/P to RGB for JPEG compatibility
        if img.mode in ('RGBA', 'P', 'LA'):
            background = PILImage.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            if img.mode in ('RGBA', 'LA'):
                background.paste(img, mask=img.split()[-1])
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')

        # Resize if larger than max_dimension
        width, height = img.size
        if width > max_dimension or height > max_dimension:
            img.thumbnail((max_dimension, max_dimension), PILImage.LANCZOS)

        # Try progressive quality reduction until under size limit
        quality = 85
        output = io.BytesIO()
        while quality >= 40:
            output.seek(0)
            output.truncate(0)
            img.save(output, format='JPEG', quality=quality, optimize=True)
            if output.tell() <= max_size_bytes:
                break
            quality -= 10

        output.seek(0)
        return output

    except Exception as e:
        # If compression fails for any reason, return original file
        print(f"Image compression failed: {e} — uploading original")
        file.seek(0)
        return file


try:
    from cloudinary_storage.storage import MediaCloudinaryStorage

    class CompressedCloudinaryStorage(MediaCloudinaryStorage):
        """
        Extends MediaCloudinaryStorage to compress images before upload.
        Handles large files that would exceed Cloudinary's 10MB free limit.
        """

        def _save(self, name, content):
            # Only compress image files
            image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.tiff')
            lower_name = name.lower()

            if any(lower_name.endswith(ext) for ext in image_extensions):
                try:
                    content.seek(0)
                    file_size = len(content.read())
                    content.seek(0)

                    # Only compress if file is larger than 8MB (safe buffer under 10MB limit)
                    if file_size > 8 * 1024 * 1024:
                        print(f"Compressing large image: {name} ({file_size / 1024 / 1024:.1f}MB)")
                        compressed = compress_image(content)
                        # Change extension to .jpg after compression
                        if not lower_name.endswith(('.jpg', '.jpeg')):
                            name = name.rsplit('.', 1)[0] + '.jpg'
                        content = compressed
                        print(f"Compressed to: {content.seek(0, 2) / 1024 / 1024:.1f}MB")
                        content.seek(0)
                except Exception as e:
                    print(f"Pre-compression check failed: {e}")
                    try:
                        content.seek(0)
                    except Exception:
                        pass

            return super()._save(name, content)

except ImportError:
    # Cloudinary not installed — no-op
    pass
