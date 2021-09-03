from accounts.api.serializers import UserSerializerForFriendship
from friendships.models import Friendship
from rest_framework import serializers
from rest_framework.exceptions import ValidationError


class FriendshipSerializerForCreate(serializers.ModelSerializer):
    from_user_id = serializers.IntegerField()
    to_user_id = serializers.IntegerField()

    class Meta:
        model = Friendship
        fields = ('from_user_id', 'to_user_id') # 这里定义需要用户提供的数据

    def validate(self, attrs):
        if attrs['from_user_id'] == attrs['to_user_id']:
            raise ValidationError({
                'message': 'from_user_id and to_user_id should be different'
            })
        return attrs

    # 定义个create方法用于保存数据
    def create(self, validated_date):
        from_user_id = validated_date['from_user_id']
        to_user_id = validated_date['to_user_id']
        return Friendship.objects.create(
            from_user_id=from_user_id,
            to_user_id=to_user_id,
        )


# 可以通过 source=xxx 指定去访问每个 model instance 的 xxx 方法
# 即 model_instance.xxx 来获得数据
# https://www.django-rest-framework.org/api-guide/serializers/#specifying-fields-explicitly
class FollowingSerializer(serializers.ModelSerializer):
    # 添加FollowingSerializer，用于获取粉丝记录
    # source='to_user'表示是从model里面的'to_user'去拿数据
    user = UserSerializerForFriendship(source='to_user')
    # created_at = serializers.DateTimeField()

    class Meta:
        model = Friendship
        fields = ('user', 'created_at')


class FollowerSerializer(serializers.ModelSerializer):
    # 添加FollowerSerializer，用于获取关注记录
    # source='from_user'表示是从model里面的'from_user'去拿数据
    user = UserSerializerForFriendship(source='from_user')
    # 下面这个没有必要加， 因为model里面已经定义了crated_at是DateTimeField()
    # created_at = serializers.DateTimeField()

    class Meta:
        model = Friendship
        fields = ('user', 'created_at')
        # fields里面的'user'先去上面的"user = UserSerializerForFriendship(source='from_user')"去找
        # 如果找不到，再到model去找。



