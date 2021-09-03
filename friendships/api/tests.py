from friendships.models import Friendship
from rest_framework import status
from rest_framework.test import APIClient
from testing.testcases import TestCase

FOLLOW_URL = '/api/friendships/{}/follow/'
UNFOLLOW_URL = '/api/friendships/{}/unfollow/'
FOLLOWERS_URL = '/api/friendships/{}/followers/'
FOLLOWINGS_URL = '/api/friendships/{}/followings/'

# 测试要求
# 必须登录
# 必须带content， 长度不能太短或太长
# 发布失败返回状态吗400， 发布成功返回状态吗201
# 需要user_id参数
# user_id以查询参数的形式出现在url的？后面
# 以列表形式返回所有推文

class FriendshipApiTests(TestCase):

    # 每次调用TweetApiTests类下面的test_开头的方法 之前，都会先去执行setUp方法，
    # 所以我们可以将每 个test_xx方法公用的初始化信息都写在这里。
    def setUp(self):
        self.anonymous_client = APIClient()

        # user1, user2 are authenticated
        self.user1 = self.create_user('user1')
        self.user1_client = APIClient()
        self.user1_client.force_authenticate(self.user1)

        self.user2 = self.create_user('user2')
        self.user2_client = APIClient()
        self.user2_client.force_authenticate(self.user2)

        # create followers for user2
        for i in range(2):
            follower = self.create_user(f'user2_follower {i}')
            Friendship.objects.create(from_user=follower, to_user=self.user2)
        # create following for user2
        for i in range(3):
            following = self.create_user(f'user2_following {i}')
            Friendship.objects.create(from_user=self.user2, to_user=following)

    def test_follow(self):
        url = FOLLOW_URL.format(self.user1.id)

        # 需要登录才能 follow 别人
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # 要用 get 来 follow
        response = self.user2_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # 不可以 follow 自己
        response = self.user1_client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # follow 成功
        response = self.user2_client.post(url)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # 重复 follow 静默成功
        response = self.user2_client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['duplicate'], True)

        # 反向关注创建新的数据
        count = Friendship.objects.count()
        response = self.user1_client.post(FOLLOW_URL.format(self.user2.id))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Friendship.objects.count(), count + 1)


    def test_unfollow(self):
        url = UNFOLLOW_URL.format(self.user1.id)

        # 需要登录才能 unfollow 别人
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # 不能用 get 来 unfollow 别人
        response = self.user2_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        # 不能 unfollow 自己
        response = self.user1_client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # unfollow 成功
        Friendship.objects.create(from_user=self.user2, to_user=self.user1)
        count = Friendship.objects.count()
        response = self.user2_client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['deleted'], 1)
        self.assertEqual(Friendship.objects.count(), count - 1)

        # 未 follow 的情况下 unfollow 静默处理
        count = Friendship.objects.count()
        response = self.user2_client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['deleted'], 0)
        self.assertEqual(Friendship.objects.count(), count)

    def test_followings(self):
        url = FOLLOWINGS_URL.format(self.user2.id)
        # post method is not allowed
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        # get method is ok
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['followings']), 3)
        # make sure 按照时间倒序
        ts0 = response.data['followings'][0]['created_at']
        ts1 = response.data['followings'][1]['created_at']
        ts2 = response.data['followings'][2]['created_at']
        self.assertEqual(ts0 > ts1, True)
        self.assertEqual(ts1 > ts2, True)
        self.assertEqual(
            response.data['followings'][0]['user']['username'],
            'user2_following 2',
        )
        self.assertEqual(
            response.data['followings'][1]['user']['username'],
            'user2_following 1',
        )
        self.assertEqual(
            response.data['followings'][2]['user']['username'],
            'user2_following 0',
        )

    def test_followers(self):
        url = FOLLOWERS_URL.format(self.user2.id)
        # post method is not allowed
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)
        # get method is ok
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code,
                         status.HTTP_200_OK)
        # make sure 按照时间倒序
        ts0 = response.data['followers'][0]['created_at']
        ts1 = response.data['followers'][1]['created_at']
        self.assertEqual(ts0 > ts1, True)
        self.assertEqual(
            response.data['followers'][0]['user']['username'],
            'user2_follower 1',
        )
        self.assertEqual(
            response.data['followers'][1]['user']['username'],
            'user2_follower 0',
        )






