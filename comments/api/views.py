from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from comments.models import Comment
from comments.api.serializers import (
    CommentSerializer,
    CommentSerializerForCreate,
    CommentSerializerForUpdate,
)
from comments.api.permissions import IsObjectOwner


class CommentViewSet(viewsets.GenericViewSet):
    """
    只实现list, create, update, destroy的方法
    不实现retrieve(查询单个comment）的方法， 因为没有这个需求
    """

    serializer_class = CommentSerializerForCreate
    queryset = Comment.objects.all()
    # 只有一项时，逗号必须加，不然就是tuple
    filterset_fields = ('tweet_id',)

    # POST /api/comments/ -> create
    # GET /api/comments/ -> list
    # GET /api/comments/1/ -> retrieve
    # DELETE /api/comments/1/ -> destroy
    # PATCH /api/comments/1/ -> partial_update
    # PUT /api/comments/1/ -> update


    def get_permissions(self):
        # 注意要加括号 AllowAny() / IsAuthenticated() 实例化出对象
        # 而不是AllowAny / IsAuthenticated 这样只是一个类名
        if self.action == 'create':
            return [IsAuthenticated()]
        if self.action in ['destroy', 'update']:
            return [IsAuthenticated(), IsObjectOwner()]
        return [AllowAny()]

    # 通常把list写在靠前的位置
    # comments list permission is allowany
    def list(self, request, *args, **kwargs):
        # /api/comments/?tweet_id=1
        if 'tweet_id' not in request.query_params:
            return Response(
                {
                    'message': 'missing tweet_id in request',
                    'success': False,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        # Solution 1
        # Filter comments by tweet_id
        # 此时不需要做类型转换N
        # tweet_id = request.query_params["tweet_id"]
        # comments = Comment.objects.filter(tweet_id=tweet_id).order_by('created_at')
        # 下面这句话和上面这就话是兼容的
        # 原因是Django自动做了转换， 在Comment model 定义了tweet这个attribute
        # 这是tweet是个实例，但是接到一个数字，那就按照数字处理，当作tweet_id
        # Comment.objects.filter(tweet=tweet_id)

        # Solution 2
        queryset = self.get_queryset()
        comments = self.filter_queryset(queryset)\
            .prefetch_related('user')\
            .order_by('created_at')
        # prefetch_related 优化处理

        # many=True 表示返回是list of dict
        serializer = CommentSerializer(comments, many=True)
        # 不直接写 serializer.data 是因为return 风格的要求： 返回必须是个dict， 不能是list
        return Response(
            {"comments": serializer.data},
            status=status.HTTP_200_OK,
        )

    def create(self, request, *args, **kwargs):
        data = {
            'user_id': request.user.id,
            'tweet_id': request.data.get('tweet_id'),
            'content': request.data.get('content'),
        }
        # 注意这里必须要加'data='来指定参数是传给data的
        # 因为默认的第一个参数是instance
        serializer = CommentSerializerForCreate(data=data)
        if not serializer.is_valid():
            return Response({
                'message': 'Please check input',
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)
        # save方法会触发serializer里面的create方法，
        comment = serializer.save()
        return Response(
            CommentSerializer(comment).data,
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        # get_object是 DRF 包装的一个函数， 会在找不到的情况下 raise 404 error
        # 所以这里无需做额外判断
        serializer = CommentSerializerForUpdate(
            instance=self.get_object(),
            data=request.data,
        )

        if not serializer.is_valid():
            return Response({
                'message': 'Please check input',
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)
        # save 方法会触发 serializer 里的 update 方法，点进save的具体实现可以看到
        # save  是根据 instance 参数有没有来决定是否触发create 或是 update 方法
        comment = serializer.save()

        return Response(
            CommentSerializer(comment).data,
            status=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        comment = self.get_object()
        comment.delete()

        # DRF里面默认destroy返回的是 status code = 204 no content
        # 这里return success=True 更直观的让前端去做判断， 所以 return 200 更合适
        return Response(
            {'success': True},
            status=status.HTTP_200_OK,
        )