from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    DigitalMaterialViewSet,
    GenerateMaterialDescriptionAPIView,
    LibraryAssistantChatAPIView,
    MaterialBookmarkViewSet,
    MaterialFavoriteViewSet,
    MaterialFeedbackViewSet,
    MaterialInteractionStatsAPIView,
    PhysicalMaterialViewSet,
    MaterialTransferRequestViewSet,
    BarcodeImageAPIView,
    PhysicalMaterialXLSImportAPIView,
)

router = DefaultRouter()
router.register("physical-materials", PhysicalMaterialViewSet, basename="physical-material")
router.register("digital-materials", DigitalMaterialViewSet, basename="digital-material")
router.register("feedback", MaterialFeedbackViewSet, basename="material-feedback")
router.register("favorites", MaterialFavoriteViewSet, basename="material-favorite")
router.register("bookmarks", MaterialBookmarkViewSet, basename="material-bookmark")
router.register("transfer-requests", MaterialTransferRequestViewSet, basename="transfer-request")

urlpatterns = [
    path("assistant-chat/", LibraryAssistantChatAPIView.as_view(), name="library-assistant-chat"),
    path("generate-description/", GenerateMaterialDescriptionAPIView.as_view(), name="generate-material-description"),
    path("interactions/stats/", MaterialInteractionStatsAPIView.as_view(), name="material-interaction-stats"),
    path("barcode/<uuid:pk>/", BarcodeImageAPIView.as_view(), name="barcode-image"),
    path("physical-materials/import-xls/", PhysicalMaterialXLSImportAPIView.as_view(), name="physical-material-import-xls"),
    path("", include(router.urls)),
]

