"""Image service for material cover generation and validation."""
import logging
import io
from PIL import Image
from django.core.files.base import ContentFile
from django.conf import settings

logger = logging.getLogger(__name__)


class ImageService:
    """Service for image handling, validation, and PDF cover generation."""
    
    ALLOWED_IMAGE_FORMATS = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
    MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
    MIN_IMAGE_DIMENSIONS = (100, 100)
    MAX_IMAGE_DIMENSIONS = (4000, 4000)
    
    @classmethod
    def validate_image(cls, image_file):
        """
        Validate uploaded image file.
        
        Args:
            image_file: Django UploadedFile object
        
        Returns:
            (is_valid, error_message)
        """
        if not image_file:
            return True, None  # Image is optional
        
        # Check file size
        if image_file.size > cls.MAX_IMAGE_SIZE:
            return False, f"Image size exceeds {cls.MAX_IMAGE_SIZE / 1024 / 1024:.0f}MB limit"
        
        # Check file format
        try:
            # Get file extension
            name = str(getattr(image_file, "name", ""))
            ext = name.rsplit(".", 1)[-1].lower() if "." in name else ""
            
            if ext not in cls.ALLOWED_IMAGE_FORMATS:
                return False, f"Image format '{ext}' not allowed. Allowed: {', '.join(cls.ALLOWED_IMAGE_FORMATS)}"
            
            # Validate it's actually an image and check dimensions
            image_file.seek(0)  # Reset file pointer
            img = Image.open(image_file)
            img.verify()  # This will raise if not a valid image
            
            # Check dimensions
            width, height = img.size
            if (width, height) < cls.MIN_IMAGE_DIMENSIONS:
                return False, f"Image dimensions {width}x{height} are too small. Minimum: {cls.MIN_IMAGE_DIMENSIONS[0]}x{cls.MIN_IMAGE_DIMENSIONS[1]}"
            
            if (width, height) > cls.MAX_IMAGE_DIMENSIONS:
                return False, f"Image dimensions {width}x{height} exceed maximum. Maximum: {cls.MAX_IMAGE_DIMENSIONS[0]}x{cls.MAX_IMAGE_DIMENSIONS[1]}"
            
            image_file.seek(0)  # Reset for actual use
            return True, None
            
        except Exception as exc:
            logger.error(f"Image validation error: {exc}")
            return False, f"Invalid image file: {str(exc)}"
    
    @classmethod
    def generate_pdf_cover(cls, pdf_file, output_format='PNG'):
        """
        Generate a cover image from the first page of a PDF file.
        
        Args:
            pdf_file: File object or path to PDF
            output_format: Output image format (PNG, JPG, etc.)
        
        Returns:
            (image_content_file, error_message) - ContentFile object or None, error message
        """
        try:
            # Try to import PyMuPDF (fitz)
            try:
                import fitz
            except ImportError:
                logger.error("PyMuPDF not installed. Install with: pip install PyMuPDF")
                return None, "PDF cover generation not available. PyMuPDF not installed."
            
            # Open PDF
            if isinstance(pdf_file, str):
                doc = fitz.open(pdf_file)
            else:
                pdf_file.seek(0)
                pdf_bytes = pdf_file.read()
                doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            
            # Get first page
            if doc.page_count == 0:
                return None, "PDF file is empty"
            
            page = doc[0]
            
            # Render page to image with good DPI
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for better quality
            
            # Convert to PIL Image
            img_data = pix.tobytes("ppm")
            img = Image.open(io.BytesIO(img_data))
            
            # Convert to target format
            output = io.BytesIO()
            img.save(output, format=output_format.upper())
            output.seek(0)
            
            # Create ContentFile
            filename = f"pdf_cover_{timezone.now().timestamp()}.{output_format.lower()}"
            content_file = ContentFile(output.getvalue(), name=filename)
            
            logger.info(f"PDF cover generated successfully: {filename}")
            return content_file, None
            
        except Exception as exc:
            logger.error(f"PDF cover generation error: {exc}")
            return None, f"Failed to generate PDF cover: {str(exc)}"
    
    @classmethod
    def process_material_image(cls, material, image_file=None, pdf_file=None):
        """
        Process material image - either use custom upload or generate from PDF.
        
        Args:
            material: Material model instance
            image_file: Custom uploaded image (optional)
            pdf_file: PDF file for cover generation (optional)
        
        Returns:
            Updated material instance or None if error
        """
        if image_file:
            # Custom image takes priority
            is_valid, error = cls.validate_image(image_file)
            if not is_valid:
                logger.error(f"Image validation failed: {error}")
                return None
            material.image = image_file
            return material
        
        # Try to generate from PDF
        if pdf_file and not material.image:
            content_file, error = cls.generate_pdf_cover(pdf_file)
            if error:
                logger.warning(f"Could not generate PDF cover: {error}")
                return material  # Return without image
            
            if content_file:
                material.image = content_file
                return material
        
        return material


# Import timezone for timestamp
from django.utils import timezone
