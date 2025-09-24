from django.contrib import admin
from .models import Post, PostImage

class PostImageInline(admin.TabularInline):
    model = PostImage
    extra = 1
    readonly_fields = ["id"]
    fields = ["image"]

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "author", "likes_count", "created_at", "updated_at")
    list_filter = ("created_at", "author")
    search_fields = ("title", "text", "author__username")
    inlines = [PostImageInline]

@admin.register(PostImage)
class PostImageAdmin(admin.ModelAdmin):
    list_display = ("id", "post", "image")
    list_filter = ("post",)
    search_fields = ("post__title",)
