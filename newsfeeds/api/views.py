from rest_framework import viewsets, status
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from newsfeeds.models import NewsFeed
from newsfeeds.api.serializers import NewsFeedSerializer


class NewsFeedViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # 自定义queryset, 因为newsfeed的查看是有权限的
        # 只能看user=当前登录用户的newsfeed。
        # 当前登录用户就是self.request.user
        # 也可以是self.request.user.newsfeed_set.all()
        # 但是一般最好还是按照NewsFeed.objecs.filter的方式写，这样更清晰直观
        return NewsFeed.objects.filter(user=self.request.user)

    # list method only take the newsfeed of current user (self.request.user)
    def list(self, request):
        serializer = NewsFeedSerializer(self.get_queryset(), many=True)
        return Response({
            'newsfeeds': serializer.data,
        }, status=status.HTTP_200_OK)