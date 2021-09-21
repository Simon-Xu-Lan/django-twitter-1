from accounts.api.serializers import UserSerializerForTweet
from comments.api.serializers import CommentSerializer
from rest_framework import serializers
from tweets.models import Tweet


class TweetSerializer(serializers.ModelSerializer):
    user = UserSerializerForTweet()

    class Meta:
        model = Tweet
        fields = ('id', 'user', 'created_at', 'content')


class TweetSerializerForCreate(serializers.ModelSerializer):
    content = serializers.CharField(min_length=6, max_length=140)

    class Meta:
        model = Tweet
        fields = ('content',)
        # 此时不能写user，因为user是来自当时的登录用户

        # model: the model for Serializer
        # fields: a tuple of field names to be included in the serialization

    # If we want to be able to return complete object instances based on the validated data
    # we need to implement one or both of the .create() and .update() methods.
    # Now when deserializing data, we can call .save() to return an object instance, based on the validated data.
    # serializer.save() will call create method
    def create(self, validated_data):
        user = self.context['request'].user
        content = validated_data['content']
        tweet = Tweet.objects.create(user=user, content=content)
        return tweet


class TweetSerializerWithComments(serializers.ModelSerializer):
    user = UserSerializerForTweet()
    comments = CommentSerializer(source='comment_set', many=True)


    class Meta:
        model = Tweet
        fields = ('id', 'user', 'comments', 'created_at', 'content')

    # <HOMEWORK> 使用 serialziers.SerializerMethodField 的方式实现 comments
    # comments = serializers.SerializerMethodField()
    #
    # def get_comments(self, obj):
    #     return CommentSerializer(obj.comment_set.all(), many=True).data

