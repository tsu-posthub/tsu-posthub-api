from rest_framework import serializers

from apps.post_app.models import Post
from apps.post_app.serializers import PostImageSerializer


class PostResponseSerializer(serializers.ModelSerializer):
    author_id = serializers.IntegerField(source="author.id", read_only=True)
    author_username = serializers.CharField(source="author.username", read_only=True)
    images = PostImageSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ["id", "title", "text", "likes_count", "author_id", "author_username", "images", "created_at"]