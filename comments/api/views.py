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
from utils.decorators import required_params


class CommentViewSet(viewsets.GenericViewSet):
    """
    只实现list, create, update, destroy的方法
    不实现retrieve(查询单个comment）的方法， 因为没有这个需求
    """

    # serializer_class 作用：
    # 在Django Rest Framework 的 UL界面中基于哪个serializer去渲染表单
    # 现在就是基于 "CommentSerializerForCreate"来渲染表单
    serializer_class = CommentSerializerForCreate
    # queryset可加可不加
    # self.get_object()是基于设定的queryset的
    # 当url是/api/comments/1/时， self.get_objects()是get comment_id=1 的comment
    # self.get_object() === Comment.objects.all().get(id=1)
    queryset = Comment.objects.all()

    # 下面是为了给Django_filter设置的
    # 只有一项时，逗号必须加，不然就是tuple
    # 表示可以用queryset 去filter tweet_id
    filterset_fields = ('tweet_id',)

    # POST /api/comments/ -> create
    # GET /api/comments/ -> list
    # GET /api/comments/1/ -> retrieve
    # DELETE /api/comments/1/ -> destroy
    # PATCH /api/comments/1/ -> partial_update
    # PUT /api/comments/1/ -> update

    # @get_permissions是用来对默认action的permission定义的
    def get_permissions(self):
        # 注意要加括号 AllowAny() / IsAuthenticated() 实例化出对象
        # 而不是AllowAny / IsAuthenticated 这样只是一个类名
        if self.action == 'create':
            return [IsAuthenticated()]
        if self.action in ['destroy', 'update']:
            return [IsAuthenticated(), IsObjectOwner()]
        return [AllowAny()]

    # 通常把list写在靠前的位置
    # comments list permission is AllowAny
    @required_params(params=['tweet_id'])
    def list(self, request, *args, **kwargs):
        # /api/comments/?tweet_id=1
        # the following block (check params) is moved to the decorator "required_params"
        # if 'tweet_id' not in request.query_params:
        #     return Response(
        #         {
        #             'message': 'missing tweet_id in request',
        #             'success': False,
        #         },
        #         status=status.HTTP_400_BAD_REQUEST,
        #     )

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
        # 这个方法要用 django_filters, 需要安装 pin install django_filter
        queryset = self.get_queryset()
        # filter_queryset 会从request里的qurey_params中读数据
        # 来看看是否要进行相应的filter
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
            'user_id': request.user.id,  # 当前登录用户的id
            # POST 的数据在 request.data 里面
            # GET 的数据在 request.query_params 里面
            # 下面是拿 post 过来的数据
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

    # 基本不用partial_update, 一般只用update
    def update(self, request, *args, **kwargs):
        # get_object是 DRF 包装的一个函数， 会在找不到的情况下 raise 404 error
        # 所以这里无需做额外判断
        # self.get_object()先把url里面的id拿出来，然后在通过queryset把id对应的object拿出来
        comment = self.get_object()
        serializer = CommentSerializerForUpdate(
            instance=comment,
            data=request.data,
        )

        # is_valid()就是看传进来的comments是否超过140个字符， 如果超过会报错
        # serializer会根据数据库的定义自动检测，不需要我们自己写这个逻辑
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


    # GenericViewSet vs ModelViewSet
    # GenericViewSet inherits from GenericAPIView
    # but does not provide any implementations of basic actions.
    # Just only get_object, get_queryset.
    # 所以要实现其他action，必须自己加
    # GenericViewSet 不包含 增，删，改 的 actions
    # ModelViewSet inherits from GenericAPIView
    # and includes implementations for various actions.
    # In other words you dont need implement basic actions
        # as list, retrieve, create, update or destroy.
    # Of course you can override them and implement your own list or your own create methods.
    # ModelViewSet 已经包含了增，删，查，改 的 actions


    # get_object
