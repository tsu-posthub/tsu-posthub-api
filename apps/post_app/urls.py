from django.urls import path
from .views import PostListCreateView, PostUpdateDetailView, PostLikeView, PostUnlikeView

urlpatterns = [
    path("", PostListCreateView.as_view(), name="post-list-create"),
    path("<int:post_id>/", PostUpdateDetailView.as_view(), name="post-detail-update"),
    path("<int:post_id>/like/", PostLikeView.as_view(), name="post-like"),
    path("<int:post_id>/unlike/", PostUnlikeView.as_view(), name="post-unlike"),
]
