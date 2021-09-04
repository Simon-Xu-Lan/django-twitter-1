from accounts.api.serializers import UserSerializerForComment
from comments.models import Comment
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from tweets.models import Tweet


class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializerForComment()

    class Meta:
        model = Comment
        fields = (
            'id',
            'tweet_id',
            'user',
            'content',
            'created_at',
            'updated_at',
        )


class CommentSerializerForCreate(serializers.ModelSerializer):
    # 这两项必须手动添加
    # 因为默认的ModelSerializer里面只会自动包含user和tweet，而不是user_id 和 tweet_id
    tweet_id = serializers.IntegerField()
    user_id = serializers.IntegerField()

    class Meta:
        model = Comment
        fields = ('content', 'tweet_id', 'user_id' )

        def validate(self, data):
            tweet_id = data["tweet_id"]
            if not Tweet.objects.filter(id=tweet_id).exists():
                raise ValidationError({'message': 'tweet does not exist'})
            # 必须是return validated data
            # 也就是经过验证之后，进行过处理的（当然也可以不作处理）输入数据
            return data

        def create(self, validated_data):
            return Comment.objects.create(
                user_id=validated_data['user_id'],
                tweet_id=validated_data['tweet_id'],
                content=validated_data['content'],
            )



    # POST /api/comments/ -> create
    # GET /api/comments/ -> list
    # GET /api/comments/I/ -> retrieve
    # DELETE /api/comments/I/ -> destroy
    # PATCH /api/comments/I/ -> partial update
    # PUT /api/comments/I/ -> update