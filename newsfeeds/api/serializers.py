from rest_framework import serializers
from newsfeeds.models import NewsFeed
from tweets.api.serializers import TweetSerializer

class NewsFeedSerializer(serializers.ModelSerializer):
    tweet = TweetSerializer()

    class Meta:
        model = NewsFeed
        fields = ('id', 'created_at', 'tweet')
        # user 不需要展示，这里的user就是登录的user