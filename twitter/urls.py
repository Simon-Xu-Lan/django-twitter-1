"""twitter URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from accounts.api.views import UserViewSet, AccountViewSet
from comments.api.views import CommentViewSet
from django.contrib import admin
from django.urls import include, path
from friendships.api.views import FriendshipViewSet
from newsfeeds.api.views import NewsFeedViewSet
from rest_framework import routers
from tweets.api.views import TweetViewSet
from likes.api.views import LikeViewSet

import debug_toolbar

# Django Rest Framework 用router regieter urls
# 每行注册都是一口气注册了多个url，每个url注册包括viewset里面的所有urls
# Create a router and register our viewsets with it.
# using a Router class. All we need to do is register the appropriate view sets with a router, and let it do the rest.
# We don't need to design the URL conf by ourselves
# DefaultRouter automatically creats the API root view for us
# The basename argument is used to specify the initial part of the view name pattern
router = routers.DefaultRouter()
router.register(r'api/users', UserViewSet)
router.register(r'api/accounts', AccountViewSet, basename='accounts') #为了避免冲突，需要有一个 basename，不加不行
router.register(r'api/tweets', TweetViewSet, basename='tweets') # 对应TweetViewSet里面的所有url， for example, api/tweets/
router.register(r'api/friendships', FriendshipViewSet, basename='friendships')
router.register(r'api/newsfeeds', NewsFeedViewSet, basename='newsfeeds')
router.register(r'api/comments', CommentViewSet, basename='comments')
router.register(r'api/likes', LikeViewSet, basename='likes')


# Django框架的URL是写在urlpatterns里面
# Django是用for循环来匹配urls
# For example, 首先匹配'admin/', 如果匹配不上，接着匹配''， 此时包括上面所有router register的urls。如果匹配不上，接下来匹配'api-auth/'， 再接着'__debug__'
urlpatterns = [
    path('admin/', admin.site.urls),
    # 这句话把上面router register的urls全部包括进来
    # The API URLs are now determined automatically by the router.
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('__debug__', include(debug_toolbar.urls)),
]