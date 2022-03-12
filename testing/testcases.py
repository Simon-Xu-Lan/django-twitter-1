from comments.models import Comment
from django.contrib.auth.models import User
from django.test import TestCase as DjangoTestCase
from rest_framework.test import APIClient
from tweets.models import Tweet
from likes.models import Like
from django.contrib.contenttypes.models import ContentType


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

    def create_comment(self, user, tweet, content=None):
        if content is None:
            content = 'default comment content'
        return Comment.objects.create(user=user, tweet=tweet, content=content)

    def create_like(self, user, target):
        # 第二个返回结果是created or not.
        # Returns a tuple of (object, created),
        # where object is the retrieved or created object
        # created is a boolean specifying whether a new object was created.
        instance, _ = Like.objects.get_or_create(
            # target.__class__: get the class name of target
            # Then get the content type of the class name
            # 这个方法可以根据target class name 拿到 对应的 content_type_id
            content_type=ContentType.objects.get_for_model(target.__class__),
            object_id=target.id,
            user=user,
        )
        # 此时不可以用create， 因为有可能会违反数据库model设定的唯一性约束。
        # instance = Like.objects.create(
        #     content_type_id=ContentType.objects.get_for_model(target.__class__),
        #     object_id=target.id,
        #     user=user,
        # )
        return instance

    def create_user_and_client(self, *args, **kwargs):
        user = self.create_user(*args, **kwargs)
        client = APIClient()
        client.force_authenticate(user)
        return user, client

