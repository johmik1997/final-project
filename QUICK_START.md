# Quick Start Guide for E-Library Features

## Installation

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Run Migrations
```bash
python manage.py migrate
```

### 3. Initialize Email Templates
```bash
python manage.py init_email_templates
```

### 4. Create Superuser (if not exists)
```bash
python manage.py createsuperuser
```

---

## Configuration

### Email Settings (.env file)
```bash
# Gmail example
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=your-email@gmail.com
EMAIL_DEV_FALLBACK_TO_CONSOLE=True
```

For development, emails will print to console if SMTP is unavailable.

### Image Storage
Images are stored in:
- Physical materials: `media/material_images/physical/`
- Digital materials: `media/material_images/digital/`
- Generated covers: `media/generated_covers/`

Ensure `media/` directory exists and is writable.

---

## API Endpoints Reference

### Rating Endpoints
```
GET    /api/materials/ratings/                    List all ratings
POST   /api/materials/ratings/                    Create rating
GET    /api/materials/ratings/{id}/               Get specific rating
PUT    /api/materials/ratings/{id}/               Update rating
DELETE /api/materials/ratings/{id}/               Delete rating

Query Parameters:
  ?material_type=physical&material_id=<uuid>     Filter by material
  ?mine=true                                      Only user's ratings
```

### Material Details (Enhanced)
```
GET /api/materials/physical-materials/{id}/
GET /api/materials/digital-materials/{id}/

New fields in response:
  {
    ...,
    "image_url": "http://...",
    "average_rating": 4.5,
    "total_ratings": 12
  }
```

### Interaction Statistics
```
GET /api/materials/interactions/stats/
    ?material_type=physical&material_id=<uuid>

Response:
  {
    "material_type": "physical",
    "material_id": "...",
    "material_title": "...",
    "average_rating": 4.5,
    "ratings_count": 12,
    "reviews_count": 8,
    "favorites_count": 45,
    "bookmarks_count": 23,
    "is_favorited": true,
    "is_bookmarked": false,
    "my_rating": 5,
    "my_review": "..."
  }
```

---

## Admin Interface

### Email Templates
Access: `/admin/backend/emailtemplate/`

Create custom templates with variables:
- {member_name}
- {material_title}
- {material_author}
- {due_date}
- {return_date}
- {overdue_days}
- {fine_amount}
- {library_name}

### Email Logs
Access: `/admin/backend/emaillog/`

Monitor:
- Email sending status (SENT, FAILED, PENDING)
- Error messages for failed sends
- Email type and recipient
- Timestamps

### Ratings
Access: `/admin/material_mgt/rating/`

Search and filter by:
- User (ID, name)
- Rating level (1-5 stars)
- Date range

---

## Code Examples

### Sending Overdue Notification
```python
from user_mgt.email_service import EmailService
from transactions.models import Borrow

borrow = Borrow.objects.get(id='...')
email_log = EmailService.send_overdue_notification(borrow)

if email_log.status == 'SENT':
    print("Email sent successfully")
else:
    print(f"Email failed: {email_log.error_message}")
```

### Creating a Rating
```python
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

client = APIClient()
user = User.objects.first()
token = RefreshToken.for_user(user).access_token
client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

response = client.post('/api/materials/ratings/', {
    'material_type': 'physical',
    'material_id': 'material-uuid',
    'rating': 5,
    'review': 'Excellent book, highly recommended!'
})

print(response.data)
```

### Validating Image Upload
```python
from material_mgt.image_service import ImageService

image_file = request.FILES['image']
is_valid, error = ImageService.validate_image(image_file)

if not is_valid:
    return Response({'error': error}, status=400)

# Process the image
material = Material.objects.get(id='...')
material.image = image_file
material.save()
```

### Generating PDF Cover
```python
from material_mgt.image_service import ImageService

pdf_file = request.FILES['file']  # Uploaded PDF

content_file, error = ImageService.generate_pdf_cover(pdf_file)

if error:
    print(f"Cover generation failed: {error}")
    # Material will just not have a cover
else:
    material.image = content_file
    material.save()
```

---

## Testing with cURL

### Create a Rating
```bash
curl -X POST http://localhost:8000/api/materials/ratings/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "material_type": "physical",
    "material_id": "12345678-1234-1234-1234-123456789012",
    "rating": 5,
    "review": "Excellent material!"
  }'
```

### List Ratings for Material
```bash
curl http://localhost:8000/api/materials/ratings/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  '?material_type=physical&material_id=12345678-1234-1234-1234-123456789012'
```

### Upload Material Image
```bash
curl -X POST http://localhost:8000/api/materials/physical-materials/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "title=Book Title" \
  -F "author=Author Name" \
  -F "image=@/path/to/image.jpg" \
  -F "category=BOOK" \
  -F "genre=Fiction" \
  -F "published_date=2024-01-01" \
  -F "department=Literature" \
  -F "language=English" \
  -F "total_copies=5" \
  -F "price=29.99"
```

---

## Troubleshooting

### Email Not Sending
1. Check email configuration in .env
2. Verify SMTP credentials
3. Check EmailLog table for error message
4. For Gmail: Use app-specific password, enable "Less secure apps"

### Image Upload Fails
1. Verify file format (JPG, PNG, GIF, WebP)
2. Check file size (max 5MB)
3. Check image dimensions (100x100 to 4000x4000)
4. Check media directory permissions

### PDF Cover Generation Fails
1. Ensure PyMuPDF is installed: `pip install PyMuPDF`
2. Verify PDF is not corrupted
3. Check error message in ImageLog (if logging implemented)
4. Material will work without cover image

### Migration Issues
```bash
# Check migration status
python manage.py showmigrations

# Roll back if needed
python manage.py migrate user_mgt 0002_initial

# Reapply
python manage.py migrate
```

---

## Performance Tips

### Email Sending
- Use Celery for async email sending (future enhancement)
- Monitor EmailLog for failed sends and retry manually
- Set up cron job for batch overdue notifications

### Image Handling
- Implement image compression for uploaded files
- Cache generated PDF covers
- Use CDN for serving images in production

### Rating Queries
- Use select_related for user data
- Index on material_id + user_id for fast lookups
- Cache average ratings if needed

---

## Security Considerations

1. **Email Templates:** Users cannot edit templates, only staff/admin
2. **Image Upload:** Validates MIME type and file format
3. **Rating Permissions:** Users can only rate materials they borrowed
4. **Email Logs:** Not directly exposed via API, admin only

---

## Future Enhancements

1. **Async Email:** Integrate Celery for background email sending
2. **Batch Operations:** Bulk email sending for overdue materials
3. **Image Processing:** Auto-optimize/compress uploaded images
4. **Analytics:** Dashboard showing rating trends
5. **Notifications:** WebSocket support for real-time alerts
6. **Translations:** Complete translation of all strings

---

## Support & Documentation

- API Documentation: `/api/docs/` (Swagger UI)
- Admin Interface: `/admin/`
- Feature Guide: See `FEATURES_IMPLEMENTED.md`
- Implementation Status: See `IMPLEMENTATION_CHECKLIST.md`

---

## Version Info
- Django: 6.0.2
- DRF: 3.16.1
- PyMuPDF: 1.24.4
- Pillow: 12.1.0
