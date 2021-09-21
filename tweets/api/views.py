from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from tweets.api.serializers import (
    TweetSerializer,
    TweetSerializerForCreate,
    TweetSerializerWithComments,
)
from tweets.models import Tweet
from newsfeeds.services import NewsFeedService
from utils.decorators import required_params


class TweetViewSet(viewsets.GenericViewSet):
    queryset = Tweet.objects.all()
    serializer_class = TweetSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:  # action代表每一个带request parameter的方法
            return [AllowAny()]  # AllowAny 允许没有登录的客户访问
        return [IsAuthenticated()]

    # list API, Django Rstt Framework 把 list all info 叫做 list API
    @required_params(params=['user_id'])
    def list(self, request, *args, **kwargs):
        """
        重载 list 方法，不列出所有 tweets，必须要求指定 user_id 作为筛选条件
        """
        # 以下功能被decorator "required_params"代替
        # if 'user_id' not in request.query_params:
        #     return Response('missing user_id', status=400)

        # 这句查询会被翻译为： SELECT * FROM twitter_tweets WHERE user_id = xxx ORDER BY created_at DESC
        # 这句SQL语句会用到user和Created_at的联合索引
        # 单独user的索引是不够的
        tweets = Tweet.objects.filter(
            user_id=request.query_params['user_id']  # query_params['user_id']是个字符串，Django会自动转换成int
        ).order_by('-created_at')
        # To serialize a queryset or list of objects instead of a single object instance,
        # you should pass the many=True flag when instantiating the serializer.
        # You can then pass a queryset or list of objects to be serialized.
        serializer = TweetSerializer(tweets, many=True) # many=True 表示 return list of dict
        return Response({'tweets': serializer.data}) # 一般来说 json 格式的 response 默认都要用 dict 的格式而不能用 list 的格式（约定俗成）在外面套一个dict 「'tweets': }

    def retrieve(self, request, *args, **kwargs):
        tweet = self.get_object()
        return Response(TweetSerializerWithComments(tweet).data)

    def create(self, request):
        """
        重写create method， 因为需要默认当前登录客户作为tweet.user
        """

        serializer = TweetSerializerForCreate(
            data=request.data,
            context={'request': request}
        )
        if not serializer.is_valid():
            return Response({
                "success": False,
                "message": "please check input.",
                "errors": serializer.errors,
            }, status=400)
        # save() will call create() method in TweetSerializerForCreate in serializers.py
        tweet = serializer.save()
        # 创建newsfeed
        NewsFeedService.fanout_to_followers(tweet)

        # When to display data, use the serializer for display, not use serializer for create
        # 下面是去展示tweet，所以要用 TweetSerializer, 而不是 TweetSerializerForCreate
        return Response(TweetSerializer(tweet).data, status=201)



