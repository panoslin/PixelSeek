from mongoengine.queryset.visitor import Q
from rest_framework import (
    status,
    permissions,
)
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import (
    MultiPartParser,
    FormParser,
)
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import Video
from .serializers import (
    VideoSerializer,
    VideoListSerializer,
    VideoCreateSerializer,
)
from .tasks import extract_keyframes
from .weaviate_schema import weaviate_client


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        # Write permissions are only allowed to the owner
        return obj.owner == request.user


class StandardResultsSetPagination(PageNumberPagination):
    """
    Standard pagination for video results.
    """

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class VideoViewSet(ModelViewSet):
    """
    ViewSet for Video model providing CRUD operations.

    list:
        Get list of videos with pagination

    retrieve:
        Get detail for a specific video

    create:
        Create a new video

    update:
        Update an existing video (full update)

    partial_update:
        Update an existing video (partial update)

    destroy:
        Delete a video
    """

    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]

    # Define the action property type to help the IDE understand it's not a pytest fixture

    def get_queryset(self):
        """
        Filter videos based on user and access level.

        The 'action' attribute is provided by DRF's ViewSet and indicates
        the current action being performed (list, retrieve, etc.)
        """
        user = self.request.user

        # Different query for list vs. individual endpoints
        if self.action == "list":
            # Return public videos and the user's own videos
            return (
                Video.objects.filter(status="ready")
                .filter(
                    # Public videos OR user's own videos
                    (Q(is_public=True) & Q(access_level="public"))
                    | Q(owner=user)
                )
                .order_by("-created_at")
            )

        # For individual video access, handled by get_object and permissions
        return Video.objects.all()

    def get_serializer_class(self):
        """
        Return appropriate serializer based on action.
        """
        if self.action == "list":
            return VideoListSerializer
        elif self.action == "create":
            return VideoCreateSerializer
        return VideoSerializer

    def perform_create(self, serializer):
        """
        Set owner to current user when creating video.
        """
        video = serializer.save(owner=self.request.user)

        # Trigger async processing tasks
        extract_keyframes.delay(str(video.id))

    @action(detail=True, methods=["post"])
    def increment_view(self, request, pk=None):
        """
        Increment view count for a video.
        """
        video = self.get_object()
        video.view_count += 1
        video.save()
        return Response({"status": "view count incremented"})

    @action(detail=True, methods=["post"])
    def increment_download(self, request, pk=None):
        """
        Increment download count for a video.
        """
        video = self.get_object()
        video.download_count += 1
        video.save()
        return Response({"status": "download count incremented"})

    @action(detail=False, methods=["get"])
    def my_videos(self, request):
        """
        List only videos owned by the current user.
        """
        queryset = Video.objects.filter(owner=request.user).order_by("-created_at")
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = VideoListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = VideoListSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def popular(self, request):
        """
        List popular videos based on view count.
        """
        queryset = Video.objects.filter(
            is_public=True, access_level="public", status="ready"
        ).order_by("-view_count")[:20]

        serializer = VideoListSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(
        detail=False, methods=["post"], parser_classes=[MultiPartParser, FormParser]
    )
    def upload(self, request):
        """
        Upload a video file and create a video record.
        """
        from django.core.files.storage import default_storage
        from django.core.files.base import ContentFile
        import os
        import uuid

        # Get the uploaded file
        video_file = request.FILES.get("video")
        if not video_file:
            return Response(
                {"error": "No video file provided"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Create a unique filename
        file_extension = os.path.splitext(video_file.name)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"

        # Save file to media storage
        file_path = default_storage.save(
            f"videos/{unique_filename}", ContentFile(video_file.read())
        )
        file_url = default_storage.url(file_path)

        # Create a placeholder thumbnail (will be replaced by actual thumbnail after processing)
        thumbnail_path = "videos/thumbnails/placeholder.jpg"

        # Create serializer with the uploaded file data
        data = {
            "title": request.data.get("title", video_file.name),
            "description": request.data.get("description", ""),
            "file_path": file_url,
            "thumbnail_path": thumbnail_path,
            "tags": (
                request.data.get("tags", "").split(",")
                if request.data.get("tags")
                else []
            ),
            "is_public": request.data.get("is_public", "True").lower() == "true",
            "access_level": request.data.get("access_level", "public"),
        }

        serializer = VideoCreateSerializer(data=data)
        if serializer.is_valid():
            video = serializer.save(owner=request.user)

            # Trigger async processing tasks
            extract_keyframes.delay(str(video.id))

            return Response(VideoSerializer(video).data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["get"])
    def search(self, request):
        """
        Advanced search endpoint with text, tag, image, and color search capabilities.
        """
        # Get query parameters
        query_text = request.query_params.get("q", "")
        tags = request.query_params.getlist("tag", [])
        color = request.query_params.get("color", "")
        query_type = request.query_params.get(
            "type", "text"
        )  # text, image, color, keyframe
        limit = int(request.query_params.get("limit", 20))
        offset = int(request.query_params.get("offset", 0))

        # Build filters for Weaviate queries
        weaviate_filters = None
        if tags:
            # Create filter for tags
            weaviate_filters = {
                "path": ["tags"],
                "operator": "ContainsAny",
                "valueTextArray": tags,
            }

        # Handle different search types
        if query_type == "image" and "image" in request.FILES:
            try:
                # Process the uploaded image for search
                image_file = request.FILES["image"]
                image_data = image_file.read()

                # Perform image-based search
                results = weaviate_client.search_by_image(
                    image_data=image_data,
                    limit=limit,
                    offset=offset,
                    filters=weaviate_filters,
                )

                if results:
                    # Extract MongoDB IDs from results
                    mongo_ids = [
                        result.get("mongodb_id")
                        for result in results
                        if result.get("mongodb_id")
                    ]

                    # Get actual video objects from MongoDB
                    videos = self._filter_videos_by_permission(
                        Video.objects.filter(id__in=mongo_ids), request.user
                    )

                    # Sort videos to match the order from vector search
                    videos_dict = {str(video.id): video for video in videos}
                    sorted_videos = [
                        videos_dict.get(mongo_id)
                        for mongo_id in mongo_ids
                        if mongo_id in videos_dict
                    ]

                    serializer = VideoListSerializer(sorted_videos, many=True)
                    return Response(serializer.data)

                return Response([])

            except Exception as e:
                return Response(
                    {"error": f"Image search failed: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        elif query_type == "keyframe" and "image" in request.FILES:
            try:
                # Process the uploaded image for keyframe search
                image_file = request.FILES["image"]
                image_data = image_file.read()

                # Perform keyframe-based search
                results = weaviate_client.search_by_keyframe(
                    image_data=image_data,
                    limit=limit,
                    offset=offset,
                    filters=weaviate_filters,
                )

                if results:
                    # Extract MongoDB IDs from results
                    mongo_ids = [
                        result.get("mongodb_id")
                        for result in results
                        if result.get("mongodb_id")
                    ]

                    # Get actual video objects from MongoDB
                    videos = self._filter_videos_by_permission(
                        Video.objects.filter(id__in=mongo_ids), request.user
                    )

                    # Add keyframe data to response
                    response_data = []
                    videos_dict = {str(video.id): video for video in videos}

                    for result in results:
                        mongo_id = result.get("mongodb_id")
                        if mongo_id in videos_dict:
                            video_data = VideoListSerializer(videos_dict[mongo_id]).data
                            video_data["keyframes"] = result.get("keyframes", [])
                            response_data.append(video_data)

                    return Response(response_data)

                return Response([])

            except Exception as e:
                return Response(
                    {"error": f"Keyframe search failed: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        elif query_type == "color" and color:
            try:
                # Validate color format (simple validation)
                if not color.startswith("#") or len(color) != 7:
                    color = "#" + color if len(color) == 6 else "#000000"

                # Perform color-based search
                results = weaviate_client.search_by_color(
                    hex_color=color,
                    limit=limit,
                    offset=offset,
                    filters=weaviate_filters,
                )

                if results:
                    # Extract MongoDB IDs from results
                    mongo_ids = [
                        result.get("mongodb_id")
                        for result in results
                        if result.get("mongodb_id")
                    ]

                    # Get actual video objects from MongoDB
                    videos = self._filter_videos_by_permission(
                        Video.objects.filter(id__in=mongo_ids), request.user
                    )

                    # Sort videos to match the order from vector search
                    videos_dict = {str(video.id): video for video in videos}
                    sorted_videos = [
                        videos_dict.get(mongo_id)
                        for mongo_id in mongo_ids
                        if mongo_id in videos_dict
                    ]

                    serializer = VideoListSerializer(sorted_videos, many=True)
                    return Response(serializer.data)

                return Response([])

            except Exception as e:
                return Response(
                    {"error": f"Color search failed: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        elif query_text:
            # For text search, try vector search first, then fall back to traditional search
            try:
                # Perform vector-based text search
                results = weaviate_client.search_by_text(
                    query_text=query_text,
                    limit=limit,
                    offset=offset,
                    filters=weaviate_filters,
                )

                if results:
                    # Extract MongoDB IDs from results
                    mongo_ids = [
                        result.get("mongodb_id")
                        for result in results
                        if result.get("mongodb_id")
                    ]

                    # Get actual video objects from MongoDB
                    videos = self._filter_videos_by_permission(
                        Video.objects.filter(id__in=mongo_ids), request.user
                    )

                    # Sort videos to match the order from vector search
                    videos_dict = {str(video.id): video for video in videos}
                    sorted_videos = [
                        videos_dict.get(mongo_id)
                        for mongo_id in mongo_ids
                        if mongo_id in videos_dict
                    ]

                    serializer = VideoListSerializer(sorted_videos, many=True)
                    return Response(serializer.data)

            except Exception as e:
                # Log the error but continue with traditional search
                import logging

                logger = logging.getLogger(__name__)
                logger.error(
                    f"Vector text search failed, falling back to traditional search: {e}"
                )

            # Traditional MongoDB text search (fallback)
            videos = Video.objects.filter(status="ready")

            # Apply text search if query provided
            videos = videos.filter(
                Q(title__icontains=query_text)
                | Q(description__icontains=query_text)
                | Q(tags__icontains=query_text)
            )

            # Filter by tags if provided
            if tags:
                videos = videos.filter(tags__in=tags)

            # Apply permissions filtering
            videos = self._filter_videos_by_permission(videos, request.user)

            # Apply pagination
            page = self.paginate_queryset(videos.order_by("-created_at"))
            if page is not None:
                serializer = VideoListSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = VideoListSerializer(videos, many=True)
            return Response(serializer.data)

        else:
            # Tag-only search or empty search
            videos = Video.objects.filter(status="ready")

            # Filter by tags if provided
            if tags:
                videos = videos.filter(tags__in=tags)

            # Apply permissions filtering
            videos = self._filter_videos_by_permission(videos, request.user)

            # Apply pagination
            page = self.paginate_queryset(videos.order_by("-created_at"))
            if page is not None:
                serializer = VideoListSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = VideoListSerializer(videos, many=True)
            return Response(serializer.data)

    def _filter_videos_by_permission(self, queryset, user):
        """
        Filter videos based on user permissions.

        Args:
            queryset: The initial queryset to filter
            user: The user to check permissions against

        Returns:
            Filtered queryset
        """
        if not user.is_authenticated:
            return queryset.filter(is_public=True, access_level="public")

        return queryset.filter(
            Q(owner=user) | (Q(is_public=True) & Q(access_level="public"))
        )
