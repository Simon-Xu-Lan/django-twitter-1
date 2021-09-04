from django.test import TestCase as DjangoTestCase
from django.contrib.auth.models import User
from tweets.models import Tweet
from rest_framework.test import APIClient

class TestCase(DjangoTestCase):

    @property
    def anonymous_client(self):
        # 错误写法
        # 这样写的话， 每次调用anonymous_client都会 New 一个APIClient()出来
        # return APIClient()

        # 正确写法
        # 只需要第一次调用anonymous_client 时 new 一个APIClient()出来
        # 我们在self内部设一个_anonymous_client， 相当于内部缓存， instance level的cache， 实在instance内部的
        # 如果没有_anonymous_client就new一个出来，如果有就直接返回 _anonymous_client。所以只在第一次调用anonymous_client才会new一个出来
        # 这样对某一个打类的 test， 比如 newsfeed.api.test, 就只会生成一个 _anonymous_client
        # 但是对于其他类，就是不同的instance， 不同的_anonymous_client
        if hasattr(self, '_anonymous_client'):
            return self._anonymous_client
        self._anonymous_client = APIClient()
        return self._anonymous_client



    def create_user(self, username, email=None, password=None):
        if password is None:
            password = 'generic password'
        if email is None:
            email = f'{username}@jiuzhang.com'

        return User.objects.create_user(username, email, password)

    def create_tweet(self, user, content=None):
        if content is None:
            content = 'default tweet content'
        return Tweet.objects.create(user=user, content=content)

