from django.db import models
from django.conf import settings
from django.db.models import Q
from django.core.validators import MaxValueValidator, MinValueValidator
import uuid
import os
# Create your models here.
class DigitalMaterial (models.Model):
    id = models.UUIDField(primary_key=True, default= uuid.uuid4,editable=False)
    title = models.CharField(max_length=255)    
    author = models.CharField(max_length=100)
    CATEGORY = [
        ('BOOK','BOOK'),
        ('MAGAZINE','MAGAZINE'),
        ('RESEARCH PAPER','RESEARCH PAPER'),
        ('JOURNALS','JOURNALS'),
        ('THESIS','THESIS')
    ]
    category = models.CharField(max_length=100,choices=CATEGORY)
    genre = models.CharField(max_length=100)
    published_date = models.DateField()
    department = models.CharField(max_length=70)
    language = models.CharField(max_length=70)
    isbn = models.CharField(max_length=70,unique=True,null=True,blank=True)
    format = models.CharField(max_length=20)
    file_size = models.CharField(max_length=10)
    file = models.FileField(upload_to="digital_materials/")
    cover_image = models.ImageField(upload_to="material_covers/", null=True, blank=True)
    cover_generated_at = models.DateTimeField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    allow_downloadable = models.BooleanField(default=True)
    library = models.ForeignKey(
        "backend.Library",
        on_delete=models.PROTECT,
        related_name="digital_materials",
        null=True,
        blank=True,
    )
    created_by = models.ForeignKey(
        "backend.User",
        on_delete=models.SET_NULL,
        related_name='digital_material',
        null=True,         
        blank=True 
    )

    @staticmethod
    def _human_readable_size(size_in_bytes):
        if size_in_bytes < 1024:
            return f"{size_in_bytes} B"
        if size_in_bytes < 1024 * 1024:
            return f"{size_in_bytes / 1024:.1f} KB"
        if size_in_bytes < 1024 * 1024 * 1024:
            return f"{size_in_bytes / (1024 * 1024):.1f} MB"
        return f"{size_in_bytes / (1024 * 1024 * 1024):.1f} GB"

    def save(self, *args, **kwargs):
        if self.file:
            _, extension = os.path.splitext(self.file.name)
            self.format = extension.lstrip(".").upper() or "UNKNOWN"
            self.file_size = self._human_readable_size(self.file.size)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    
# Physical Material Table
class PhysicalMaterial (models.Model):
    id = models.UUIDField(primary_key=True, default= uuid.uuid4,editable=False)
    title = models.CharField(max_length=255)    
    author = models.CharField(max_length=100)
    CATEGORY = [
        ('BOOK','BOOK'),
        ('MAGAZINE','MAGAZINE'),
        ('RESEARCH PAPER','RESEARCH PAPER'),
        ('JOURNALS','JOURNALS'),
        ('THESIS','THESIS')
    ]
    category = models.CharField(max_length=100,choices=CATEGORY)
    genre = models.CharField(max_length=100)
    published_date = models.DateField()
    department = models.CharField(max_length=70)
    language = models.CharField(max_length=70)
    isbn = models.CharField(max_length=70,null=True,blank=True)
    barcode = models.CharField(max_length=100, unique=True, null=True, blank=True)
    total_copies = models.IntegerField()
    available_copies = models.IntegerField(null=True, blank=True)
    price = models.DecimalField(max_digits=10,decimal_places=2)
    CONDITION = [
        ('NEW','NEW'),
        ('GOOD','GOOD'),
        ('FAIR','FAIR'),
        ('DAMAGED','DAMAGED')
    ]
    condition = models.CharField(max_length=20,choices=CONDITION,default='GOOD')
    LOCATION = [
        ('STACK','STACK'),
        ('SHELF','SHELF')
    ]
    location = models.CharField(max_length=20,choices=LOCATION,default='STACK')
    can_borrow  = models.BooleanField(default=True)
    image = models.ImageField(upload_to="material_images/", null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    library = models.ForeignKey(
        "backend.Library",
        on_delete=models.PROTECT,
        related_name="physical_materials",
        null=True,
        blank=True,
    )
    created_by = models.ForeignKey(
        "backend.User",
        on_delete=models.SET_NULL,
        related_name='physical_material',
        null=True, 
        blank=True 
    )

    def save(self, *args, **kwargs):
        if self.available_copies is None:
            self.available_copies = self.total_copies
        # Auto-generate barcode if not provided
        if not self.barcode:
            try:
                import barcode
                from barcode.writer import ImageWriter
                # Use UUID as base for barcode code128
                code = str(self.id).replace('-', '')[:12]
                Code128 = barcode.get_barcode_class('code128')
                barcode_obj = Code128(code, writer=ImageWriter())
                # Save to temporary in-memory file
                from io import BytesIO
                buffer = BytesIO()
                barcode_obj.write(buffer)
                # Store PNG binary as base64 string (or keep as raw bytes for image endpoint) - here we store string identifier
                self.barcode = code
            except Exception as e:
                # Fallback: use UUID string directly
                self.barcode = str(self.id)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title


class MaterialFeedback(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="material_feedbacks",
    )
    physical_material = models.ForeignKey(
        "material_mgt.PhysicalMaterial",
        on_delete=models.CASCADE,
        related_name="feedbacks",
        null=True,
        blank=True,
    )
    digital_material = models.ForeignKey(
        "material_mgt.DigitalMaterial",
        on_delete=models.CASCADE,
        related_name="feedbacks",
        null=True,
        blank=True,
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        indexes = [
            models.Index(fields=["user", "updated_at"]),
            models.Index(fields=["physical_material", "updated_at"]),
            models.Index(fields=["digital_material", "updated_at"]),
            models.Index(fields=["rating"]),
        ]
        constraints = [
            models.CheckConstraint(
                name="material_feedback_exactly_one_material",
                condition=(
                    (Q(physical_material__isnull=False) & Q(digital_material__isnull=True))
                    | (Q(physical_material__isnull=True) & Q(digital_material__isnull=False))
                ),
            ),
            models.CheckConstraint(
                name="material_feedback_rating_range",
                condition=Q(rating__gte=1, rating__lte=5),
            ),
            models.UniqueConstraint(
                fields=["user", "physical_material"],
                condition=Q(physical_material__isnull=False),
                name="material_feedback_unique_user_physical",
            ),
            models.UniqueConstraint(
                fields=["user", "digital_material"],
                condition=Q(digital_material__isnull=False),
                name="material_feedback_unique_user_digital",
            ),
        ]


class MaterialFavorite(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="material_favorites",
    )
    physical_material = models.ForeignKey(
        "material_mgt.PhysicalMaterial",
        on_delete=models.CASCADE,
        related_name="favorites",
        null=True,
        blank=True,
    )
    digital_material = models.ForeignKey(
        "material_mgt.DigitalMaterial",
        on_delete=models.CASCADE,
        related_name="favorites",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "created_at"]),
            models.Index(fields=["physical_material", "created_at"]),
            models.Index(fields=["digital_material", "created_at"]),
        ]
        constraints = [
            models.CheckConstraint(
                name="material_favorite_exactly_one_material",
                condition=(
                    (Q(physical_material__isnull=False) & Q(digital_material__isnull=True))
                    | (Q(physical_material__isnull=True) & Q(digital_material__isnull=False))
                ),
            ),
            models.UniqueConstraint(
                fields=["user", "physical_material"],
                condition=Q(physical_material__isnull=False),
                name="material_favorite_unique_user_physical",
            ),
            models.UniqueConstraint(
                fields=["user", "digital_material"],
                condition=Q(digital_material__isnull=False),
                name="material_favorite_unique_user_digital",
            ),
        ]


class MaterialBookmark(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="material_bookmarks",
    )
    physical_material = models.ForeignKey(
        "material_mgt.PhysicalMaterial",
        on_delete=models.CASCADE,
        related_name="bookmarks",
        null=True,
        blank=True,
    )
    digital_material = models.ForeignKey(
        "material_mgt.DigitalMaterial",
        on_delete=models.CASCADE,
        related_name="bookmarks",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "created_at"]),
            models.Index(fields=["physical_material", "created_at"]),
            models.Index(fields=["digital_material", "created_at"]),
        ]
        constraints = [
            models.CheckConstraint(
                name="material_bookmark_exactly_one_material",
                condition=(
                    (Q(physical_material__isnull=False) & Q(digital_material__isnull=True))
                    | (Q(physical_material__isnull=True) & Q(digital_material__isnull=False))
                ),
            ),
            models.UniqueConstraint(
                fields=["user", "physical_material"],
                condition=Q(physical_material__isnull=False),
                name="material_bookmark_unique_user_physical",
            ),
            models.UniqueConstraint(
                fields=["user", "digital_material"],
                condition=Q(digital_material__isnull=False),
                name="material_bookmark_unique_user_digital",
            ),
        ]
    
class DigitalMaterialAccessLog(models.Model):
    EVENT_VIEW = 'VIEW'
    EVENT_DOWNLOAD = 'DOWNLOAD'
    EVENT_CHOICES = [(EVENT_VIEW, 'View'), (EVENT_DOWNLOAD, 'Download')]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    material = models.ForeignKey(
        DigitalMaterial,
        on_delete=models.CASCADE,
        related_name='access_logs',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='digital_access_logs',
    )
    event = models.CharField(max_length=10, choices=EVENT_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['material', 'event', 'timestamp']),
            models.Index(fields=['user', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.event} – {self.material_id} by {self.user_id} at {self.timestamp}"


class MaterialTransferRequest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    material = models.ForeignKey(
        PhysicalMaterial,
        on_delete=models.CASCADE,
        related_name="transfer_requests",
    )

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('IN_TRANSFER', 'In Transfer'),
        ('COMPLETED', 'Completed'),
        ('REJECTED', 'Rejected'),
        ('CANCELLED', 'Cancelled'),
    ]

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )

    requested_quantity = models.PositiveIntegerField(default=1)

    transferred_quantity = models.PositiveIntegerField(
        default=0
    )

    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="created_transfer_requests",
        null=True,
    )

    fulfilled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="fulfilled_transfer_requests",
        null=True,
        blank=True,
    )

    notes = models.TextField(blank=True, null=True)

    rejection_reason = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    completed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.material.title} ({self.requested_quantity}) - {self.status}"