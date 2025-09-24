from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, parsers
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from core.mixins import ErrorResponseMixin
from core.serializers import ErrorResponseSerializer
from .models import Post
from .serializers import CreatePostRequestSerializer
from .serializers_response import PostListResponseSerializer, PostDetailResponseSerializer

title_param = openapi.Parameter(
    name="title",
    in_=openapi.IN_FORM,
    description="Заголовок поста",
    type=openapi.TYPE_STRING,
    required=True,
)
text_param = openapi.Parameter(
    name="text",
    in_=openapi.IN_FORM,
    description="Текст поста",
    type=openapi.TYPE_STRING,
    required=True,
)
images_param = openapi.Parameter(
    name="images",
    in_=openapi.IN_FORM,
    description="Изображения (можно загрузить несколько)",
    type=openapi.TYPE_ARRAY,
    items=openapi.Items(type=openapi.TYPE_FILE),
    required=False,
    collectionFormat="multi"
)
delete_images_param = openapi.Parameter(
    name="delete_images",
    in_=openapi.IN_FORM,
    type=openapi.TYPE_ARRAY,
    description="Список id изображений для удаления",
    items=openapi.Items(type=openapi.TYPE_INTEGER),
    required=False,
    collectionFormat="multi"
)

class PostListCreateView(ErrorResponseMixin, APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (parsers.MultiPartParser, parsers.FormParser)

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated()]
        return [AllowAny()]

    @swagger_auto_schema(
        tags=["posts"],
        operation_summary="Список постов",
        operation_description="Возвращает список всех постов с изображениями и автором",
        responses={
            200: openapi.Response(
                description="Список постов",
                schema=PostListResponseSerializer(many=True)
            ),
            500: openapi.Response(
                description="Внутренняя ошибка сервера",
                schema=ErrorResponseSerializer
            ),
        },
    )
    def get(self, request):
        posts = Post.objects.all().select_related("author").prefetch_related("images")
        serializer = PostListResponseSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        tags=["posts"],
        operation_summary="Создание поста",
        operation_description="Позволяет авторизованному пользователю создать новый пост",
        manual_parameters=[title_param, text_param, images_param],
        consumes=["multipart/form-data"],
        responses={
            201: openapi.Response(
                description="Пост успешно создан",
                schema=PostDetailResponseSerializer
            ),
            400: openapi.Response(
                description="Ошибка валидации данных",
                schema=ErrorResponseSerializer
            ),
            401: openapi.Response(
                description="Неавторизован",
                schema=ErrorResponseSerializer
            ),
            500: openapi.Response(
                description="Внутренняя ошибка сервера",
                schema=ErrorResponseSerializer
            ),
        },
    )
    def post(self, request):
        serializer = CreatePostRequestSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        post = serializer.save()
        return Response(PostDetailResponseSerializer(post).data, status=status.HTTP_201_CREATED)


class PostUpdateDetailView(ErrorResponseMixin, APIView):
    parser_classes = (parsers.MultiPartParser, parsers.FormParser)

    def get_permissions(self):
        if self.request.method in ["PUT", "DELETE"]:
            return [IsAuthenticated()]
        return [AllowAny()]

    @swagger_auto_schema(
        tags=["posts"],
        operation_summary="Получение деталей поста",
        operation_description="Возвращает детальную информацию о посте по ID",
        responses={
            200: openapi.Response(
                description="Детали поста",
                schema=PostDetailResponseSerializer
            ),
            404: openapi.Response(
                description="Пост не найден",
                schema=ErrorResponseSerializer
            ),
            500: openapi.Response(
                description="Внутренняя ошибка сервера",
                schema=ErrorResponseSerializer
            ),
        },
    )
    def get(self, request, post_id):
        try:
            post = Post.objects.select_related("author").prefetch_related("images").get(id=post_id)
        except Post.DoesNotExist:
            raise NotFound(f"Post with post_id={post_id} does not exist")

        serializer = PostDetailResponseSerializer(post)
        return Response(serializer.data)

    @swagger_auto_schema(
        tags=["posts"],
        operation_summary="Обновление поста",
        operation_description="Позволяет автору обновить пост",
        manual_parameters=[title_param, text_param, images_param, delete_images_param],
        consumes=["multipart/form-data"],
        responses={
            200: openapi.Response(
                description="Пост успешно обновлён",
                schema=PostDetailResponseSerializer
            ),
            400: openapi.Response(
                description="Ошибка валидации данных",
                schema=ErrorResponseSerializer
            ),
            401: openapi.Response(
                description="Неавторизован",
                schema=ErrorResponseSerializer
            ),
            403: openapi.Response(
                description="Нет прав на обновление поста",
                schema=ErrorResponseSerializer
            ),
            404: openapi.Response(
                description="Пост не найден",
                schema=ErrorResponseSerializer
            ),
            500: openapi.Response(
                description="Внутренняя ошибка сервера",
                schema=ErrorResponseSerializer
            ),
        },
    )
    def put(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return self.format_error(
                request,
                status.HTTP_404_NOT_FOUND,
                "Not Found",
                f"Post with post_id={post_id} does not exist"
            )

        if post.author != request.user:
            return self.format_error(
                request,
                status.HTTP_403_FORBIDDEN,
                "Forbidden",
                "You do not have permission to edit this post"
            )

        serializer = CreatePostRequestSerializer(
            post, data=request.data, partial=True, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        post = serializer.save()
        return Response(PostDetailResponseSerializer(post).data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        tags=["posts"],
        operation_summary="Удаление поста",
        operation_description="Позволяет автору удалить пост по ID",
        responses={
            204: "Пост успешно удалён",
            401: openapi.Response(
                description="Неавторизован",
                schema=ErrorResponseSerializer
            ),
            403: openapi.Response(
                description="Нет прав на удаление поста",
                schema=ErrorResponseSerializer
            ),
            404: openapi.Response(
                description="Пост не найден",
                schema=ErrorResponseSerializer
            ),
            500: openapi.Response(
                description="Внутренняя ошибка сервера",
                schema=ErrorResponseSerializer
            ),
        },
    )
    def delete(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return self.format_error(
                request,
                status.HTTP_404_NOT_FOUND,
                "Not Found",
                f"Post with post_id={post_id} does not exist"
            )

        if post.author != request.user:
            return self.format_error(
                request,
                status.HTTP_403_FORBIDDEN,
                "Forbidden",
                "You do not have permission to delete this post"
            )

        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
