from newsfeeds.models import NewsFeed
from friendships.models import Friendship
from rest_framework.test import APIClient
from testing.testcases import TestCase
from rest_framework import status


NEWSFEEDS_URL ='/api/newsfeeds/'
POST_TWEETS_URL = '/api/tweets/'
FOLLOW_URL = '/api/friendships/{}/follow/'


class NewsFeedApiTests(TestCase):

    def setUp(self):
        self.linghu = self.create_user('linghu')
        self.linghu_client = APIClient()
        self.linghu_client.force_authenticate(self.linghu)

        self.dongxie = self.create_user('dongxie')
        self.dongxie_client = APIClient()
        self.dongxie_client.force_authenticate(self.dongxie)

        # 下面没有用到
        # Create followers for dongxie
        # for i in range(2):
        #     follower = self.create_user('dongxie_follower{}'.format(i))
        #     Friendship.objects.create(from_user=follower, to_user=self.dongxie)

        # Create followings for dongxie
        # for i in range(3):
        #     following = self.create_user('dongxie_follower{}'.format(i))
        #     Friendship.objects.create(from_user=self.dongxie, to_user=following)

    def test_list(self):
        # 需要登录
        response = self.anonymous_client.get(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # 不能用POST
        response = self.linghu_client.post(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # 一开始啥都没有
        response = self.linghu_client.get(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["newsfeeds"]), 0)

        # 自己发的信息自己可以看到
        self.linghu_client.post(POST_TWEETS_URL, {'content': 'Hello World'})
        response = self.linghu_client.get(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["newsfeeds"]), 1)

        # 关注dongxie后可有看到别人发的tweets
        self.linghu_client.post(FOLLOW_URL.format(self.dongxie.id))
        response = self.dongxie_client.post(POST_TWEETS_URL, {
            'content': 'Hello Twitter',
        })
        posted_tweet_id = response.data['id']
        response = self.linghu_client.get(NEWSFEEDS_URL)
        # print("%%%%%%%")
        # print(response.data['newsfeeds'])
        self.assertEqual(len(response.data['newsfeeds']), 2)
        self.assertEqual(response.data['newsfeeds'][0]['tweet']['id'], posted_tweet_id)