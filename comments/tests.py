from testing.testcases import TestCase

# Create your tests here.
class CommentModelTests(TestCase):

    def test_comment(self):
        user = self.create_user('linghu')
        tweet = self.create_tweet(user)
        comment = self.create_comment(user, tweet)
        comment_str = '{} - {} says {} at tweet {}'.format(
            comment.created_at,
            comment.user,
            comment.content,
            comment.tweet_id,
        )
        self.assertEqual(comment.__str__(), comment_str)
