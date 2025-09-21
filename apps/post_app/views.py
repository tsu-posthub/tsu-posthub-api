from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, parsers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.mixins import ErrorResponseMixin
from core.serializers import ErrorResponseSerializer
from .serializers import CreatePostRequestSerializer
from .serializers_response import PostResponseSerializer


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

class PostCreateView(ErrorResponseMixin, APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (parsers.MultiPartParser, parsers.FormParser)

    @swagger_auto_schema(
        tags=["posts"],
        operation_summary="Создание поста",
        operation_description="Позволяет авторизованному пользователю создать новый пост",
        manual_parameters=[title_param, text_param, images_param],
        consumes=["multipart/form-data"],
        responses={
            201: openapi.Response(
                description="Пост успешно создан",
                schema=PostResponseSerializer
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
        return Response(PostResponseSerializer(post).data, status=status.HTTP_201_CREATED)
