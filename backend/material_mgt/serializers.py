from material_mgt.models import *
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from material_mgt.services import is_allowed_image_file
from django.db.models import Avg, Count


def _build_media_url(request, file_field):
    if not file_field:
        return None
    url = getattr(file_field, "url", str(file_field) or None)
    if not url:
        return None
    return request.build_absolute_uri(url) if request else url


class MaterialFeedbackPreviewSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = MaterialFeedback
        fields = ["id", "user_name", "rating", "comment", "created_at", "updated_at"]

    def get_user_name(self, obj):
        user = getattr(obj, "user", None)
        if not user:
            return None
        return f"{user.first_name} {user.last_name}".strip() or user.id_number


class MaterialFeedbackStatsMixin:
    average_rating = serializers.SerializerMethodField(read_only=True)
    ratings_count = serializers.SerializerMethodField(read_only=True)
    comments_count = serializers.SerializerMethodField(read_only=True)
    recent_feedbacks = serializers.SerializerMethodField(read_only=True)
    my_feedback_id = serializers.SerializerMethodField(read_only=True)
    my_rating = serializers.SerializerMethodField(read_only=True)
    my_comment = serializers.SerializerMethodField(read_only=True)

    def _get_feedback_queryset(self, obj):
        return getattr(obj, "feedbacks", None)

    def get_average_rating(self, obj):
        annotated = getattr(obj, "average_rating", None)
        if annotated is not None:
            return round(float(annotated or 0), 2)
        feedbacks = self._get_feedback_queryset(obj)
        if feedbacks is None:
            return 0
        result = feedbacks.aggregate(avg=Avg("rating"))
        return round(float(result.get("avg") or 0), 2)

    def get_ratings_count(self, obj):
        annotated = getattr(obj, "ratings_count", None)
        if annotated is not None:
            return int(annotated or 0)
        feedbacks = self._get_feedback_queryset(obj)
        if feedbacks is None:
            return 0
        return feedbacks.count()

    def get_comments_count(self, obj):
        annotated = getattr(obj, "comments_count", None)
        if annotated is not None:
            return int(annotated or 0)
        feedbacks = self._get_feedback_queryset(obj)
        if feedbacks is None:
            return 0
        return feedbacks.exclude(comment="").count()

    def get_recent_feedbacks(self, obj):
        feedbacks = self._get_feedback_queryset(obj)
        if feedbacks is None:
            return []
        rows = feedbacks.select_related("user").order_by("-updated_at")[:10]
        return MaterialFeedbackPreviewSerializer(rows, many=True, context=self.context).data

    def get_my_rating(self, obj):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return None
        feedbacks = self._get_feedback_queryset(obj)
        if feedbacks is None:
            return None
        row = feedbacks.filter(user=user).first()
        return row.rating if row else None

    def get_my_comment(self, obj):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return ""
        feedbacks = self._get_feedback_queryset(obj)
        if feedbacks is None:
            return ""
        row = feedbacks.filter(user=user).first()
        return row.comment if row else ""

    def get_my_feedback_id(self, obj):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return None
        feedbacks = self._get_feedback_queryset(obj)
        if feedbacks is None:
            return None
        row = feedbacks.filter(user=user).first()
        return str(row.id) if row else None

class PhysicalMaterialSerializer(MaterialFeedbackStatsMixin, serializers.ModelSerializer):
    created_by_name = serializers.CharField(source="created_by.full_name", read_only=True)
    library_name = serializers.CharField(source="library.name", read_only=True)

    average_rating = serializers.SerializerMethodField(read_only=True)
    ratings_count = serializers.SerializerMethodField(read_only=True)
    comments_count = serializers.SerializerMethodField(read_only=True)
    recent_feedbacks = serializers.SerializerMethodField(read_only=True)
    my_feedback_id = serializers.SerializerMethodField(read_only=True)
    my_rating = serializers.SerializerMethodField(read_only=True)
    my_comment = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = PhysicalMaterial
        fields = [
            "id", "title", "author", "category", "genre", "published_date", 
            "department", "language", "isbn", "barcode", "total_copies", 
            "available_copies", "price", "condition", "location", "can_borrow", 
            "image", "description", "library", "library_name", "created_by", "created_by_name",
            "average_rating", "ratings_count", "comments_count", "recent_feedbacks",
            "my_rating", "my_comment", "my_feedback_id"
        ]
        read_only_fields = ["created_by", "created_by_name", "library_name"]

    def validate_image(self, value):
        if value and not is_allowed_image_file(value):
            raise serializers.ValidationError(_("Only JPG, JPEG, PNG, WEBP, or GIF files are allowed."))
        return value


class DigitalMaterialSerializer(MaterialFeedbackStatsMixin, serializers.ModelSerializer):
    created_by_name = serializers.CharField(source="created_by.full_name", read_only=True)
    library_name = serializers.CharField(source="library.name", read_only=True)
    file = serializers.FileField(required=True)
    cover_image_url = serializers.SerializerMethodField(read_only=True)

    average_rating = serializers.SerializerMethodField(read_only=True)
    ratings_count = serializers.SerializerMethodField(read_only=True)
    comments_count = serializers.SerializerMethodField(read_only=True)
    recent_feedbacks = serializers.SerializerMethodField(read_only=True)
    my_feedback_id = serializers.SerializerMethodField(read_only=True)
    my_rating = serializers.SerializerMethodField(read_only=True)
    my_comment = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = DigitalMaterial
        fields = [
            "id", "title", "author", "category", "genre", "published_date",
            "department", "language", "isbn", "format", "file_size", "file",
            "cover_image", "cover_generated_at", "description", "allow_downloadable",
            "library", "library_name",
            "created_by", "created_by_name", "cover_image_url",
            "average_rating", "ratings_count", "comments_count", "recent_feedbacks",
            "my_rating", "my_comment", "my_feedback_id"
        ]
        read_only_fields = ["created_by", "created_by_name", "library_name", "format", "file_size"]

    def get_cover_image_url(self, obj):
        return _build_media_url(self.context.get("request"), getattr(obj, "cover_image", None))

    def validate_cover_image(self, value):
        if value and not is_allowed_image_file(value):
            raise serializers.ValidationError(_("Only JPG, JPEG, PNG, WEBP, or GIF files are allowed."))
        return value

    def validate(self, attrs):
        request = self.context.get("request")
        if request and request.method == "POST" and not attrs.get("file"):
            raise serializers.ValidationError({"file": "This field is required for digital material upload."})
        upload = attrs.get("file")
        if upload is not None:
            # Keep existing model fields populated from uploaded file metadata.
            name = str(getattr(upload, "name", ""))
            ext = name.rsplit(".", 1)[-1].upper() if "." in name else "UNKNOWN"
            size_bytes = int(getattr(upload, "size", 0) or 0)
            size_mb = round(size_bytes / (1024 * 1024), 2)
            attrs["format"] = ext
            attrs["file_size"] = f"{size_mb} MB"
        return attrs


MATERIAL_TYPE_CHOICES = (("physical", "physical"), ("digital", "digital"))


class MaterialTargetMixinSerializer(serializers.ModelSerializer):
    material_type = serializers.ChoiceField(choices=MATERIAL_TYPE_CHOICES, write_only=True, required=True)
    material_id = serializers.UUIDField(write_only=True, required=True)
    user_id = serializers.UUIDField(source="user.id", read_only=True)
    user_name = serializers.SerializerMethodField(read_only=True)
    material_title = serializers.SerializerMethodField(read_only=True)
    material = serializers.SerializerMethodField(read_only=True)

    def get_user_name(self, obj):
        user = getattr(obj, "user", None)
        if not user:
            return None
        return f"{user.first_name} {user.last_name}".strip() or user.id_number

    def get_material_title(self, obj):
        material = obj.physical_material or obj.digital_material
        return getattr(material, "title", None)

    def get_material(self, obj):
        material = obj.physical_material or obj.digital_material
        if not material:
            return None

        data = {
            "id": str(material.id),
            "title": getattr(material, "title", None),
            "author": getattr(material, "author", None),
            "category": getattr(material, "category", None),
            "genre": getattr(material, "genre", None),
            "department": getattr(material, "department", None),
            "language": getattr(material, "language", None),
            "isbn": getattr(material, "isbn", None),
            "published_date": getattr(material, "published_date", None),
            "library_id": str(material.library_id) if getattr(material, "library_id", None) else None,
            "library_name": getattr(getattr(material, "library", None), "name", None),
            "description": getattr(material, "description", None),
        }

        if getattr(obj, "physical_material_id", None):
            data.update(
                {
                    "condition": getattr(material, "condition", None),
                    "location": getattr(material, "location", None),
                    "available_copies": getattr(material, "available_copies", None),
                    "total_copies": getattr(material, "total_copies", None),
                    "can_borrow": getattr(material, "can_borrow", None),
                    "price": getattr(material, "price", None),
                }
            )
        else:
            data.update(
                {
                    "format": getattr(material, "format", None),
                    "file_size": getattr(material, "file_size", None),
                    "file_url": _build_media_url(self.context.get("request"), getattr(material, "file", None)),
                }
            )

        return data

    def _set_material_target(self, attrs, material_type, material_id):
        if material_type == "physical":
            material = PhysicalMaterial.objects.filter(pk=material_id).first()
            if not material:
                raise serializers.ValidationError({"material_id": "Physical material not found."})
            attrs["physical_material"] = material
            attrs["digital_material"] = None
        elif material_type == "digital":
            material = DigitalMaterial.objects.filter(pk=material_id).first()
            if not material:
                raise serializers.ValidationError({"material_id": "Digital material not found."})
            attrs["digital_material"] = material
            attrs["physical_material"] = None
        else:
            raise serializers.ValidationError({"material_type": "Invalid material type."})

    def validate(self, attrs):
        attrs = super().validate(attrs)
        material_type = attrs.pop("material_type", None)
        material_id = attrs.pop("material_id", None)

        if self.instance is None:
            if not material_type or not material_id:
                raise serializers.ValidationError(
                    {"detail": "Both material_type and material_id are required."}
                )
            self._set_material_target(attrs, material_type, material_id)
        elif material_type is not None or material_id is not None:
            if not material_type or not material_id:
                raise serializers.ValidationError(
                    {"detail": "Provide both material_type and material_id together when updating target."}
                )
            self._set_material_target(attrs, material_type, material_id)

        return attrs

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.physical_material_id:
            data["material_type"] = "physical"
            data["material_id"] = str(instance.physical_material_id)
        else:
            data["material_type"] = "digital"
            data["material_id"] = str(instance.digital_material_id)
        return data


class MaterialFeedbackSerializer(MaterialTargetMixinSerializer):
    rating = serializers.IntegerField(min_value=1, max_value=5)
    comment = serializers.CharField(required=False, allow_blank=True, max_length=2000)

    class Meta:
        model = MaterialFeedback
        fields = [
            "id",
            "user_id",
            "user_name",
            "material_type",
            "material_id",
            "material_title",
            "material",
            "rating",
            "comment",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "user_id", "user_name", "material_title", "created_at", "updated_at"]

    def validate(self, attrs):
        attrs = super().validate(attrs)
        request = self.context.get("request")
        user = getattr(request, "user", None)

        if self.instance is None and user and user.is_authenticated:
            exists = MaterialFeedback.objects.filter(
                user=user,
                physical_material=attrs.get("physical_material"),
                digital_material=attrs.get("digital_material"),
            ).exists()
            if exists:
                raise serializers.ValidationError(
                    {"detail": "You already rated this material. Use PATCH to update."}
                )

        return attrs


class MaterialFavoriteSerializer(MaterialTargetMixinSerializer):
    class Meta:
        model = MaterialFavorite
        fields = [
            "id",
            "user_id",
            "user_name",
            "material_type",
            "material_id",
            "material_title",
            "material",
            "created_at",
        ]
        read_only_fields = ["id", "user_id", "user_name", "material_title", "created_at"]


class MaterialBookmarkSerializer(MaterialTargetMixinSerializer):
    class Meta:
        model = MaterialBookmark
        fields = [
            "id",
            "user_id",
            "user_name",
            "material_type",
            "material_id",
            "material_title",
            "material",
            "created_at",
        ]
        read_only_fields = ["id", "user_id", "user_name", "material_title", "created_at"]


class MaterialTransferRequestSerializer(serializers.ModelSerializer):
    material_title = serializers.CharField(source="material.title", read_only=True)
    requested_by_name = serializers.SerializerMethodField(read_only=True)
    fulfilled_by_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = MaterialTransferRequest
        fields = [
            "id",
            "material",
            "material_title",
            "status",
            "requested_quantity",
            "transferred_quantity",
            "rejection_reason",
            "requested_by",
            "requested_by_name",
            "fulfilled_by",
            "fulfilled_by_name",
            "notes",
            "created_at",
            "completed_at",
        ]
        read_only_fields = [
            "id",
            "material_title",
            "transferred_quantity",
            "requested_by",
            "requested_by_name",
            "fulfilled_by",
            "fulfilled_by_name",
            "created_at",
            "completed_at",
        ]

    def validate(self, attrs):
        material = attrs.get("material")
        requested_quantity = attrs.get("requested_quantity", 1)

        if not material:
            raise serializers.ValidationError({"material": "Material is required."})

        if material.location != "STACK":
            raise serializers.ValidationError({"material": "Transfer requests can only be made for materials located in the STACK."})

        if requested_quantity <= 0:
            raise serializers.ValidationError({"requested_quantity": "Requested quantity must be greater than zero."})

        if material.available_copies < requested_quantity:
            raise serializers.ValidationError({"requested_quantity": f"Cannot request {requested_quantity} copies. Only {material.available_copies} available in STACK."})

        return attrs

    def get_requested_by_name(self, obj):
        if not obj.requested_by:
            return None
        return f"{obj.requested_by.first_name} {obj.requested_by.last_name}".strip() or obj.requested_by.id_number

    def get_fulfilled_by_name(self, obj):
        if not obj.fulfilled_by:
            return None
        return f"{obj.fulfilled_by.first_name} {obj.fulfilled_by.last_name}".strip() or obj.fulfilled_by.id_number

