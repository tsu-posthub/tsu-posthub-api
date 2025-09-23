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
    delete_images = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True,
        write_only=True
    )

    class Meta:
        model = Post
        fields = ["title", "text", "images", "delete_images"]

    def create(self, validated_data):
        images_data = validated_data.pop("images", [])
        post = Post.objects.create(author=self.context["request"].user, **validated_data)
        for img in images_data:
            PostImage.objects.create(post=post, image=img)
        return post

    def update(self, instance, validated_data):
        images_data = validated_data.pop("images", None)
        delete_images = validated_data.pop("delete_images", [])
        
        instance.title = validated_data.get("title", instance.title)
        instance.text = validated_data.get("text", instance.text)
        instance.save()

        if delete_images:
            images_to_delete = PostImage.objects.filter(post=instance, id__in=delete_images)
            for img in images_to_delete:
                if img.image:
                    img.image.delete(save=False)
            images_to_delete.delete()
        
        if images_data:
            for img in images_data:
                PostImage.objects.create(post=instance, image=img)

        return instance