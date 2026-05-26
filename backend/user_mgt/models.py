from django.db import models
from django.contrib.auth.models import AbstractUser,BaseUserManager
from django.core.exceptions import ValidationError
import uuid

class UserManager(BaseUserManager):
    use_in_migrations = True
    
    def _create_user(self, id_number, password, **extra_fields):
        if not id_number:
            raise ValueError("The ID number must be set")
        email = extra_fields.get("email")
        if not email:
            raise ValueError("The email must be set")
        extra_fields["email"] = self.normalize_email(email)

        user = self.model(id_number=id_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, id_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('role', 'MEMBER')
        extra_fields.setdefault('status', 'ACTIVE')
        return self._create_user(id_number, password, **extra_fields)

    def create_superuser(self, id_number, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'SUPER ADMIN')
        extra_fields.setdefault('status', 'ACTIVE')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(id_number, password, **extra_fields)
    
    
class User(AbstractUser):
    
    id = models.UUIDField(primary_key=True, default= uuid.uuid4,editable=False)
    username = None
    id_number = models.CharField(max_length=30,unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(max_length=100,unique=True)
    ROLE_CHOICES = [
        ('STACK STAFF', 'STACK STAFF'),
        ('TECHNICAL STAFF', 'TECHNICAL STAFF'),
        ('FRONT DESK STAFF', 'FRONT DESK STAFF'),
        ('ADMIN', 'ADMIN'),
        ('DEPARTMENT HEAD', 'DEPARTMENT HEAD'),
        ('MEMBER', 'MEMBER'),
        ('SUPER ADMIN', 'SUPER ADMIN'),
    ]
    role = models.CharField(max_length=30,choices=ROLE_CHOICES, default='MEMBER')
    photo = models.ImageField(upload_to='profile_photo', blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    department = models.CharField(max_length=70, blank=True, null=True)
    work_shift = models.CharField(max_length=15, blank=True, null=True)
    USER_TYPE = [
        ('TEACHER','TEACHER'),
        ('STUDENT','STUDENT'),
    ]
    user_type = models.CharField(max_length=15, choices=USER_TYPE, blank=True, null=True)
    library = models.ForeignKey(
        "backend.Library",
        on_delete=models.SET_NULL,
        related_name="users",
        null=True,
        blank=True,
    )
    STATUS_CHOICES = [
        ('ACTIVE', 'ACTIVE'),
        ('INACTIVE', 'INACTIVE'),
        ('SUSPENDED', 'SUSPENDED'),
        ('DEACTIVATED', 'DEACTIVATED'),
    ]
    status = models.CharField(max_length=30,choices=STATUS_CHOICES, default='ACTIVE')
    must_change_password = models.BooleanField(default=False)
    USERNAME_FIELD = "id_number"
    REQUIRED_FIELDS = ["email"]
    objects = UserManager()

    def clean(self):
        super().clean()
        role = (self.role or "").strip().upper()
        staff_roles = {"STACK STAFF", "TECHNICAL STAFF", "FRONT DESK STAFF", "ADMIN", "SUPER ADMIN"}

        if role in {"MEMBER", "DEPARTMENT HEAD"} and not (self.department or "").strip():
            raise ValidationError({"department": "Department is required for MEMBER and DEPARTMENT HEAD."})

        if role == "MEMBER" and not self.user_type:
            raise ValidationError({"user_type": "User type is required for MEMBER."})

        if role != "MEMBER" and self.user_type:
            raise ValidationError({"user_type": "User type is only valid for MEMBER."})

        if role in staff_roles:
            return
        if self.work_shift:
            raise ValidationError({"work_shift": "Work shift is only valid for staff roles."})

    def __str__(self):
        return self.id_number

class Notification(models.Model):
    id = models.UUIDField(primary_key=True, default= uuid.uuid4,editable=False)
    member_id = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notification'
    ) 
    borrow_id = models.ForeignKey(
        "transactions.Borrow",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='notification'
    ) 
    reserve_id = models.ForeignKey(
        "transactions.Reservation",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='notification'
    ) 
    message = models.CharField(max_length=200)
    STATUS = [
        ('SENT','SENT'),
        ('READ','READ'),
        ('UNREAD','UNREAD'),
    ]
    status = models.CharField(max_length=20,choices=STATUS,default='UNREAD')
    sent_at = models.DateTimeField(auto_now_add=True)


# Library Table
class Library(models.Model):
    id = models.UUIDField(primary_key=True, default= uuid.uuid4,editable=False)
    name = models.CharField(max_length=100,unique=True)
    campus = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class LibraryPolicy(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    library = models.ForeignKey(
        Library,
        on_delete=models.CASCADE,
        related_name="policies",
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=120, default="Default Library Policy")
    is_active = models.BooleanField(default=True)
    borrow_duration_days = models.PositiveIntegerField(default=7)
    max_active_borrows = models.PositiveIntegerField(default=3)
    reservation_hold_hours = models.PositiveIntegerField(default=24)
    overdue_daily_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fair_condition_penalty_percent = models.DecimalField(max_digits=6, decimal_places=2, default=10)
    damaged_condition_penalty_percent = models.DecimalField(max_digits=6, decimal_places=2, default=35)
    lost_condition_penalty_percent = models.DecimalField(max_digits=6, decimal_places=2, default=100)
    grace_period_days = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["library__name", "-is_active", "-updated_at"]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.is_active:
            queryset = LibraryPolicy.objects.exclude(pk=self.pk).filter(is_active=True)
            if self.library_id:
                queryset = queryset.filter(library_id=self.library_id)
            else:
                queryset = queryset.filter(library__isnull=True)
            queryset.update(is_active=False)

    def __str__(self):
        if self.library_id:
            return f"{self.library.name} - {self.name}"
        return self.name
