from accounts.api.serializers import UserSerializerForComment
from comments.models import Comment
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from tweets.models import Tweet


class CommentSerializer(serializers.ModelSerializer):
    # 这是的作用是把user解析成UserSerializerForComment的形式
    # UserSerializerForComment 在userSerializer中定义了
    # 如果不加下面这一句，fields里面的user会以 user_id 的形式来显示
    # 加了下面只一句，fields里面的user会以一个嵌套的user dict来显示
    # 这个dict是user的具体信息
    user = UserSerializerForComment()

    # 一般来说， serializer都是用于显示某个model对应的具体的object
    class Meta:
        # 把model Comment对应的信息放到class Meta当中去
        model = Comment
        # @ fields 把要展示的fields 以白名单的模式列在这里
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
    # 但是Django Rest Framework没有兼容 user 和 user_id / tweet 和 tweet_id
    # 这里先声明 tweet_id 和 user_id, 不然下面fields找不到 tweet_id 和 user_id
    # 同时validate tweet_id 和 user_id
    tweet_id = serializers.IntegerField()
    user_id = serializers.IntegerField()

    class Meta:
        model = Comment
        # 把要展示的field以白名单的形式写下来
        fields = ('content', 'tweet_id', 'user_id', )

        # 总共传进来三个参数， user_id, tweet_id, content
        # user_id 是当前登录用户的id，self.request.user.id, 不需要验证
            # 因为permission会验证，只有登录的用户才行
        # comments：会自动根据数据库的定义进行验证，这里不需要验证
        # 这里只对tweet_id进行验证， 验证这个tweet是否存在
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


class CommentSerializerForUpdate(serializers.ModelSerializer):

    class Meta:
        model = Comment
        # 用户只能改content， 不能改其他fields
        fields = ('content',)

    def update(self, instance, validated_data):
        instance.content = validated_data['content']
        instance.save()

        # update 方法要求return 修改后的 instance 作为返回值
        return instance

    # @ 默认的action， 6个
    # @ POST /api/comments/ -> create
    # @ GET /api/comments/ -> list
    # @ GET /api/comments/I/ -> retrieve （detail=True)
    # @ DELETE /api/comments/I/ -> destroy （detail=True)
    # @ PATCH /api/comments/I/ -> partial_update （detail=True)
    # @ PUT /api/comments/I/ -> update  （detail=True)
    # 这6个默认action用重写get_permissionS() method 来定义permission
    # 这6个默认action不用 @action [  ]
    # 除了这6个默认的action， 其他自己写的action 用@action[ ]中的permission_classes来定义permission

# @ 命名规范
# User is name of Model
# user is instance of User
# user_id is the primary key of the User, by default it is int.
# users is list of users or a queryset of User
# --

# Django 兼容下面两种写法
# Tweet.objects.filter(user=1)
# Tweet.objects.filter(user_id=1)
# 这两种写法是一样的
# 但是Django Rest Framework没有兼容 user 和 user_id