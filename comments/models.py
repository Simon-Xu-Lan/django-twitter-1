from django.db import models
from django.contrib.auth.models import User
from tweets.models import Tweet
from likes.models import Like
from django.contrib.contenttypes.models import ContentType

# Create your models here.
class Comment(models.Model):
    """
    在这个版本上，我们先实现一个比较简单的评论
    评论只评论在某个Tweet上，不能评论别人的评论
    """
    # User 和 comments是one to many. one user can have many comments. one comments can only belong to one user
    # So ForeignKey in many side, that is, on comments side
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    # Tweet and comments are one to many, one tweet can have many comments, one comment can only belong to one tweet
    # so ForeignKey is on comments side
    tweet = models.ForeignKey(Tweet, on_delete=models.SET_NULL, null=True)
    content = models.TextField(max_length=140)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        # Demand: sort all comments under one tweet.
        # 在某个tweet下排序所有 comments的需求
        index_together = (('tweet', 'created_at'),)

    @property
    def like_set(self):
        return Like.objects.filter(
            content_type=ContentType.objects.get_for_model(Comment),
            object_id=self.id,
        )

    def __str__(self):
        return '{} - {} says {} at tweet {}'.format(
            self.created_at,
            self.user,
            self.content,
            self.tweet_id,  # question: why tweet_id
        )
