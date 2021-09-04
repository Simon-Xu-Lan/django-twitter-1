from django.db import models
from django.contrib.auth.models import User
from tweets.models import Tweet


class NewsFeed(models.Model):
    # 注意这个user不是存储谁发了这条tweet， 而是谁可以看到这条tweet
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    tweet = models.ForeignKey(Tweet, on_delete=models.SET_NULL, null=True)
    # created_at is the same as created-at in tweet, however, we need created at to sort in newsfeed table,
    # it is very slow if we use created_at in tweet table, so we add a created_at column in newsfeed table.
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        index_together = (('user', 'created_at'), )
        unique_together = (('user', 'tweet'), )
        # ordering 的作用是拿去加载在queryset的后面
        ordering = ('-created_at',)

    def __str__(self):
        return f'{self.created_at} inbox of {self.user}: {self.tweet}'


