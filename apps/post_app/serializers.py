from rest_framework import serializers

from apps.post_app.models import Post, PostImage


class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = ["id", "image"]

class CreatePostRequestSerializer(serializers.ModelSerializer):
    images = serializers.ListField(
        child=serializers.ImageField(),
        required=False,
        allow_empty=True,
        write_only=True
    )

    class Meta:
        model = Post
        fields = ["title", "text", "images"]

    def create(self, validated_data):
        images_data = validated_data.pop("images", [])
        post = Post.objects.create(author=self.context["request"].user, **validated_data)
        for img in images_data:
            PostImage.objects.create(post=post, image=img)
        return post