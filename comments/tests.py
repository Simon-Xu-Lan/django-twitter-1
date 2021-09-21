from testing.testcases import TestCase

# Create your tests here.
class CommentModelTests(TestCase):

    def setUp(self):
        self.user = self.create_user('linghu')
        self.tweet = self.create_tweet(self.user)
        self.comment = self.create_comment(self.user, self.tweet)

    def test_comment(self):
        self.assertNotEqual(self.comment.__str__(), None)
        # comment_str = '{} - {} says {} at tweet {}'.format(
        #     comment.created_at,
        #     comment.user,
        #     comment.content,
        #     comment.tweet_id,
        # )
        # self.assertEqual(comment.__str__(), comment_str)

    def test_like_set(self):
        self.create_like(self.user, self.comment)
        self.assertEqual(self.comment.like_set.count(), 1)

        # 不重复创建
        self.create_like(self.user, self.comment)
        self.assertEqual(self.comment.like_set.count(), 1)

        dongxie = self.create_user('dongxie')
        self.create_like(dongxie, self.comment)
        self.assertEqual(self.comment.like_set.count(), 2)


