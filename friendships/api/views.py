from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from friendships.models import Friendship
from friendships.api.serializers import (
    FriendshipSerializerForCreate,
    FollowerSerializer,
    FollowingSerializer,
    FriendshipsSerializer,
)
from django.contrib.auth.models import User


class FriendshipViewSet(viewsets.GenericViewSet):
    # 我们希望 POST /api/friendship/1/follow 是去 follow user_id=1 的用户, 此时pk=1
    # 因此这里 queryset 需要是 User.objects.all()
    # 如果是 Friendship.objects.all() 的话就会出现 404 Not Found
    # 因为 detail=True 的 actions 会默认先去调用 get_object() 也就是
    # queryset.filter(pk=1) 查询一下这个 object 在不在

    # detail=True, or detail=False
    # if you pass detail=True it means that that router will return you a single object
    # whilst if you don't pass detail=True or pass detail=False it will return a list of objects.
    # if you are not doing anything or don’t need a single object in this function, you can set the detail=False

    # SX understanding: 在这种情况下, url必须提供具体的信息，下面这种情况就是pk,即user_id
    # SX，url的组成就是 /api/friendships/pk/followers， /api/base name/具体信息/函数名称


    # GET method 不需要 serializer_class
    # 但是，POST method必须有 serialized_class. DRF需要一个serializer class 把 POST的表格来填充好。
    serializer_class = FriendshipSerializerForCreate
    queryset = User.objects.all()

    @action(methods=['GET'], detail=True, permission_classes=[AllowAny])
    def followers(self, request, pk):
        # GET /api/friendships/1/followers, pk 就是 1
        friendships = Friendship.objects.filter(to_user_id=pk).order_by('-created_at')
        serializer = FollowerSerializer(friendships, many=True)
        # if there is url field in FollowerSerializer defination, "context={'request': request}" is needed when instantiating the serializer
        # serializer = FollowerSerializer(friendships, context={'request': request}, many=True)

        return Response(
            {'followers': serializer.data},
            status=status.HTTP_200_OK,
        )

    @action(methods=['GET'], detail=True, permission_classes=[AllowAny])
    def followings(self, request, pk):
        friendships = Friendship.objects.filter(from_user_id=pk).order_by('-created_at')
        serializer = FollowingSerializer(friendships, many=True)
        # To serialize a queryset or list of objects instead of a single object instance, you should pass the "many=True" flag when instantiating the serializer. You can then pass a queryset or list of objects to be serialized.

        return Response(
            {'followings': serializer.data},
            status=status.HTTP_200_OK,
        )


    # 因为是创建了一条新的记录， 所以用'POST'
    # 因为是基于某一个用户，所以 detail=True
    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated])
    def follow(self, request, pk):
        # /api/friendships/pk/follow : 当前登录的用户 follow user_id=pk 的用户
        # 特殊判断重复follow的情况（比如前端猛点好多少次follow)
        # 静默处理，不报错，因为这类重复操作因为网络延迟的原因会比较多，没必要当做错误处理
        # 如果没有下面的处理， 因为friendship model中设定了唯一性约束（unique_together)
        # FriendshipSerializerForCreate 在检测数据是会报错， 400 错误， "The fields from_user_id, to_user_id must make a unique set."
        # 因此，下面这几行对于重复的（from_user, to_user)做静默处理。


        # 下面get_object以pk作为id去取这个user， 如果取到就返回这个user，如果取不到，就返回404
        # 这是另一种方法检测 to_user是否存在
        # follow_user = self.get_object()

        if Friendship.objects.filter(
                from_user=request.user,
                to_user=pk,
        ).exists():
            return Response({
                'success': True,
                'duplicate': True
            }, status=status.HTTP_201_CREATED)

        serializer = FriendshipSerializerForCreate(data={
            # 不能是user_id， 因为request object has no attribute 'user_id'
            # request.user 是当前用户
            'from_user_id': request.user.id,
            'to_user_id': pk,
        })
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        instance = serializer.save()

        return Response(
            # 通过FollowingSerializer(instance)， 可以得到nested dict， 就是把user的信息嵌套进去
            FollowingSerializer(instance).data,
            # {'success': True},
            status=status.HTTP_201_CREATED
        )

    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated])
    def unfollow(self, request, pk):
        # /api/friendships/pk/unfollow/
        # 当前登录的用户 unfollow user_id=pk 的用户
        # detail=True时， 会调用一个seLf.get_object()的方法
            # self.get_object()
        # 用get_object(）检测 pk作为id的user是否存在
        # raise 404 if no user id = pk
        unfollow_user = self.get_object()
        # 1-检测不是自己unfollow自己
        # 注意 pk 的类型是 str，所以要做类型转换
        if request.user.id == int(pk):
            return Response({
                'success': False,
                'message': 'You cannot unfollow yourself',
            }, status=status.HTTP_400_BAD_REQUEST)
        # https://docs.djangoproject.com/en/3.1/ref/models/querysets/#delete
        # Queryset 的 delete 操作返回两个值，一个是删了多少数据，一个是具体每种类型删了多少
        # 为什么会出现多种类型数据的删除？因为可能因为 foreign key 设置了 cascade 出现级联
        # 删除，也就是比如 A model 的某个属性是 B model 的 foreign key，并且设置了
        # on_delete=models.CASCADE, 那么当 B 的某个数据被删除的时候，A 中的关联也会被删除。
        # 所以 CASCADE 是很危险的，我们一般最好不要用，而是用 on_delete=models.SET_NULL
        # 取而代之，这样至少可以避免误删除操作带来的多米诺效应。
        deleted, _ = Friendship.objects.filter(
            from_user=request.user,
            to_user=unfollow_user,
            # to_user=pk, # to_user=unfollow_user 和 to_user=pk 是一样的
        ).delete()

        return Response({'success': True, 'deleted': deleted})

    # 必须定义一个list API， admin page 才有friensships这个url
    # /api/friendships/
    def list(self, request):
        # 重写list，
        # friendships = Friendship.objects.all()
        # serializer = FriendshipsSerializer(friendships, many=True)
        # return Response({'friendships': serializer.data})

        # return Response({'message': 'This is friendships home page'})

        # determine the queryset based on query parameters in the url
        # /api/friendships/?to_user_id=1
        # /api/friendships/?from_user_id=1

        to_user_id = request.query_params.get('to_user_id')
        from_user_id = request.query_params.get('from_user_id')
        if to_user_id and from_user_id:
            friendships = Friendship.objects.filter(
                to_user_id=to_user_id,
                from_user_id=from_user_id,
            )
            # To serialize a queryset or list of objects instead of a single object instance, you should pass the many=True flag when instantiating the serializer. You can then pass a queryset or list of objects to be serialized.
            serializer = FollowerSerializer(friendships, many=True)
            return Response(
                {'friendship': serializer.data},
                status=status.HTTP_200_OK,
            )
        elif to_user_id:
            friendships = Friendship.objects.filter(
                to_user_id=to_user_id
            )
            serializer = FollowerSerializer(friendships, many=True)
            return Response(
                {'followers': serializer.data},
                status=status.HTTP_200_OK,
            )
        elif from_user_id:
            friendships = Friendship.objects.filter(
                from_user_id=from_user_id
            )
            serializer = FollowingSerializer(friendships, many=True)
            return Response(
                {'followings': serializer.data},
                status=status.HTTP_200_OK,
            )
        else:
            friendships = Friendship.objects.all()
            serializer = FriendshipsSerializer(friendships, many=True)
            return Response(
                {'friendships': serializer.data},
                status=status.HTTP_200_OK
            )



# 工程经验：mySQL
# 1。 join 不要用， join会把操作变成n*n
# 2. CASCADE 不要用
# 3。 DROP Foreign key constraint, 用integer 类型


