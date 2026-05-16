# E-Library Features Implementation Guide

## Features Implemented

This document describes the features implemented in this release.

### 1. Email Notification System ✅

**Status:** Core infrastructure implemented, ready for integration

**What's included:**
- `EmailTemplate` model - Reusable email templates
- `EmailLog` model - Email audit trail and history
- `EmailService` class - Service for sending emails
- Management command `init_email_templates` - Initialize 5 templates:
  - OVERDUE - Overdue material notifications
  - RESERVED_AVAILABLE - Reserved material available alerts
  - BORROW_CONFIRMATION - Successful borrow confirmations
  - RETURN_CONFIRMATION - Return success notifications
  - CUSTOM - Custom email templates

**Files:**
- `user_mgt/models.py` - EmailTemplate, EmailLog models
- `user_mgt/email_service.py` - EmailService class
- `user_mgt/admin.py` - Admin registration
- `transactions/management/commands/init_email_templates.py` - Template initialization

**Integration points:**
- Email templates use Django's string formatting with {variable} syntax
- Service methods: send_overdue_notification(), send_reserved_available_notification(), send_borrow_confirmation(), send_return_confirmation()

**To use:**
```python
from user_mgt.email_service import EmailService

# Send overdue notification
email_log = EmailService.send_overdue_notification(borrow_instance)

# Send borrow confirmation
email_log = EmailService.send_borrow_confirmation(borrow_instance)

# Send return confirmation
email_log = EmailService.send_return_confirmation(return_instance)
```

---

### 2. Rating System Backend ✅

**Status:** Complete API endpoints and serializers ready

**What's included:**
- `Rating` model - 1-5 star ratings with optional reviews
- `MaterialFeedback` model - Legacy compatibility layer
- `RatingViewSet` - Full CRUD API for ratings
- `RatingSerializer` - Create/update serializer
- `RatingListSerializer` - List serializer with user info
- `RatingStatisticsSerializer` - Rating statistics
- Material serializers enhanced with:
  - `image_url` field
  - `average_rating` field
  - `total_ratings` field

**Files:**
- `material_mgt/models.py` - Rating model
- `material_mgt/serializers.py` - Rating serializers
- `material_mgt/views.py` - RatingViewSet
- `material_mgt/urls.py` - Routing
- `material_mgt/admin.py` - Admin registration

**API Endpoints:**
```
GET/POST  /api/materials/ratings/          - List/create ratings
GET/PUT/DELETE /api/materials/ratings/{id}/  - Retrieve/update/delete
GET       /api/materials/feedback/          - List feedback (legacy)
GET       /api/materials/interactions/stats/ - Material interaction stats
```

**Key features:**
- One rating per user per material (enforced by unique constraints)
- Average rating automatically calculated
- User can only rate materials from their library
- Staff can view all ratings

**Example request:**
```json
{
  "material_type": "physical",
  "material_id": "uuid-here",
  "rating": 5,
  "review": "Excellent book!"
}
```

---

### 3. Material Image Support ✅

**Status:** Models and services ready, ImageField added

**What's included:**
- Image fields added to both DigitalMaterial and PhysicalMaterial
- `ImageService` class for:
  - Image validation (format, size, dimensions)
  - PDF cover generation using PyMuPDF
  - Image processing with fallback error handling
- Validation rules:
  - Formats: JPG, PNG, GIF, WebP
  - Max size: 5MB
  - Min dimensions: 100x100px
  - Max dimensions: 4000x4000px
- Auto-generate covers from PDF first page (if no custom image)
- Manual image takes priority over auto-generated

**Files:**
- `material_mgt/models.py` - Image fields
- `material_mgt/image_service.py` - ImageService class
- `material_mgt/serializers.py` - Enhanced serializers
- `requirements.txt` - PyMuPDF dependency

**Usage:**
```python
from material_mgt.image_service import ImageService

# Validate image
is_valid, error = ImageService.validate_image(image_file)

# Generate PDF cover
content_file, error = ImageService.generate_pdf_cover(pdf_file)

# Process material image (validates custom or generates from PDF)
material = ImageService.process_material_image(
    material=material_instance,
    image_file=custom_image,
    pdf_file=pdf_file
)
```

---

### 4. Chatbot Improvements

**Status:** Infrastructure in place, requires configuration

The chatbot system requires:
- Integration with recommendation_system app
- Enhanced query parsing for library data
- Context awareness improvements

**Existing infrastructure:**
- `LibraryAssistantChatAPIView` - Chat API endpoint
- Prompt building with conversation history
- OpenAI integration

**Next steps for completion:**
- Build query builder for materials, borrows, reservations
- Add language detection for Amharic support
- Implement fallback responses
- Test with various user queries

---

### 5. Translation Feature Fixes

**Status:** Infrastructure exists, needs completion

**Existing:**
- Django i18n configured
- Frontend supports English and Amharic

**To complete:**
- Audit all untranslated strings
- Add missing translation keys to frontend locales
- Translate validation error messages
- Translate chatbot responses
- Create comprehensive translation guide

---

## Database Migrations

Two new migrations have been created:

1. **user_mgt/migrations/0003_email_models.py**
   - Creates EmailTemplate model
   - Creates EmailLog model
   - Adds indexes for performance

2. **material_mgt/migrations/0002_rating_and_images.py**
   - Adds image field to DigitalMaterial
   - Adds image field to PhysicalMaterial
   - Creates Rating model
   - Adds indexes and constraints

**To apply migrations:**
```bash
python manage.py migrate
```

**To initialize email templates:**
```bash
python manage.py init_email_templates
```

---

## Configuration

### Email Settings (in .env)
```
DEFAULT_FROM_EMAIL=your-email@example.com
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True
EMAIL_DEV_FALLBACK_TO_CONSOLE=True
```

### Image Settings
- Images stored in `media/material_images/digital/` and `media/material_images/physical/`
- Generated PDF covers stored in `media/generated_covers/`

---

## Admin Interface

New admin interfaces available:
- **Email Templates** (`/admin/backend/emailtemplate/`)
  - Create/edit reusable email templates
  - View template variables
  
- **Email Logs** (`/admin/backend/emaillog/`)
  - Audit trail of all sent emails
  - Filter by status, type, date
  
- **Ratings** (`/admin/material_mgt/rating/`)
  - View user ratings
  - Search by user or material
  - Filter by rating level

---

## Testing

### Email Service
```python
from user_mgt.email_service import EmailService
from transactions.models import Borrow

# Test overdue notification
borrow = Borrow.objects.first()
EmailService.send_overdue_notification(borrow)
```

### Rating API
```bash
# List ratings for a material
curl "http://localhost:8000/api/materials/ratings/?material_type=physical&material_id=<uuid>"

# Create rating
curl -X POST http://localhost:8000/api/materials/ratings/ \
  -H "Authorization: Bearer <token>" \
  -d '{
    "material_type": "physical",
    "material_id": "<uuid>",
    "rating": 5,
    "review": "Great book!"
  }'
```

### Image Upload
Images are included in material create/update endpoints:
```bash
curl -X POST http://localhost:8000/api/materials/physical-materials/ \
  -F "image=@/path/to/image.jpg" \
  -F "title=Book Title" \
  ... other fields
```

---

## Breaking Changes

None - The system maintains backward compatibility:
- `MaterialFeedback` remains as a legacy model
- Existing feedback API endpoints still work
- Rating system is additive (new model alongside feedback)

---

## Dependencies Added

- `PyMuPDF==1.24.4` - PDF to image conversion

Install with:
```bash
pip install -r requirements.txt
```

---

## Notes for Frontend Integration

1. **Rating System:**
   - Update endpoints to use new `/api/materials/ratings/` instead of `/feedback/`
   - Serializer field changed from `comment` to `review`
   - Response includes `average_rating` and `total_ratings` on material details

2. **Material Images:**
   - New `image_url` field in material serializers
   - Images are optional (nullable)
   - Staff users can upload images via form data

3. **Email Notifications:**
   - No frontend changes needed
   - Automatic background notifications
   - Optional integration with websockets for real-time alerts

---

## Known Limitations & Future Improvements

1. **Chatbot:**
   - Requires OpenAI API configuration
   - Needs enhanced intent recognition
   - Amharic support in progress

2. **Email Notifications:**
   - Currently uses Django send_mail (sync)
   - Future: Integrate Celery for async sending
   - Could add template customization UI

3. **Image Processing:**
   - PDF cover generation only uses first page
   - Could add image optimization/compression
   - Could support batch image uploads

4. **Translations:**
   - Not all error messages translated yet
   - Admin interface not translated
   - Chat responses need translation

---

## Contact & Support

For issues or questions about these features, refer to the implementation files:
- Email system: `user_mgt/email_service.py`
- Rating system: `material_mgt/views.py`, `material_mgt/serializers.py`
- Image handling: `material_mgt/image_service.py`
