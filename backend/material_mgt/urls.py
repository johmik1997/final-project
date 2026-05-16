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
    RatingViewSet,
)

router = DefaultRouter()
router.register("physical-materials", PhysicalMaterialViewSet, basename="physical-material")
router.register("digital-materials", DigitalMaterialViewSet, basename="digital-material")
router.register("feedback", MaterialFeedbackViewSet, basename="material-feedback")
router.register("ratings", RatingViewSet, basename="material-rating")
router.register("favorites", MaterialFavoriteViewSet, basename="material-favorite")
router.register("bookmarks", MaterialBookmarkViewSet, basename="material-bookmark")

urlpatterns = [
    path("assistant-chat/", LibraryAssistantChatAPIView.as_view(), name="library-assistant-chat"),
    path("generate-description/", GenerateMaterialDescriptionAPIView.as_view(), name="generate-material-description"),
    path("interactions/stats/", MaterialInteractionStatsAPIView.as_view(), name="material-interaction-stats"),
    path("", include(router.urls)),
]
