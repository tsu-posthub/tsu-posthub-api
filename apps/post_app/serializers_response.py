from rest_framework import serializers

from apps.post_app.models import Post
from apps.post_app.serializers import PostImageSerializer


class PostListResponseSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source="author.username", read_only=True)
    thumbnail = serializers.SerializerMethodField()
    preview_text = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            "id", 
            "title",
            "preview_text",
            "author_username", 
            "likes_count", 
            "thumbnail", 
            "created_at", 
            "updated_at"
        ]

    def get_preview_text(self, obj):
        return obj.text[:200] + "..." if len(obj.text) > 200 else obj.text
    
    def get_thumbnail(self, obj):
        first_image = obj.images.first()
        return first_image.image.url if first_image else None

class PostDetailResponseSerializer(serializers.ModelSerializer):
    author_id = serializers.IntegerField(source="author.id", read_only=True)
    author_username = serializers.CharField(source="author.username", read_only=True)
    images = PostImageSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "text",
            "likes_count",
            "author_id",
            "author_username",
            "images",
            "created_at",
            "updated_at",
        ]