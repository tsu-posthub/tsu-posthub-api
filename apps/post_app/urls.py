from django.urls import path
from .views import PostListCreateView, PostUpdateDetailView

urlpatterns = [
    path("", PostListCreateView.as_view(), name="post-list-create"),
    path("<int:post_id>/", PostUpdateDetailView.as_view(), name="post-detail-update"),
]
