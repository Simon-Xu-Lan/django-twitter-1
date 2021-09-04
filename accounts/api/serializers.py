from django.contrib.auth.models import User, Group
from rest_framework import serializers, exceptions

# userSerializer的作用： 取出user的数据，并变成json格式
class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email']

# 不想包含email信息，所以新建一个serializer
class UserSerializerForTweet(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username')


class UserSerializerForComment(serSerializerForTweet):
    pass


# 不想包含email信息，所以新建一个serializer
class UserSerializerForFriendship(UserSerializerForTweet):
    pass


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    # 检测是否有username和password这两项


    def validate(self, data):
        if not User.objects.filter(username=data['username'].lower()).exists():
            raise exceptions.ValidationError({
                'username': 'User does not exist'
            })
        return data


class SignupSerializer(serializers.ModelSerializer): # 用modelSerializer, 在调用seriralizer.save时能够把这个用户实际创建出来
    username = serializers.CharField(max_length=20, min_length=6)
    password = serializers.CharField(max_length=20, min_length=6)
    email = serializers.EmailField()

    # 下面fields中指定的fields要和上面的一致，否则会报错。
    class Meta:
        model = User #指定model是User， 对应数据库中的user表
        fields = ('username', 'email', 'password') # 指定field有些什么， 如果user表单中还有其他fields, 我们在这次创建中是不会添加的

    # this validate method will be called when is_valid() is called
    # 加个下面这个validate method是做额外的验证， 不加这个validate的话，serializer就做上面field的验证
    # 上面的Emailfield只会做绝对等于的比较， 不会做大小写转换
    # 下面增加的validate去做大小写转换后的验证
    # 前提是在存储username 和 email是存入小写
    # __iexact 效率地，尽量不要用
    def validate(self, data):
        # user表单里寸的是小写，此时把用户输入的username转化成小写，然后到user表单中找，看看是否存在这个username
        # 这样做就可以忽略用户输入的大小写
        # 看看username有没有重复（小写情况下）， 如果有重复就抛出异常
        if User.objects.filter(username=data['username'].lower()).exists():
            raise exceptions.ValidationError({

                'username': 'This username has been occupied'

            })
        # 看看email有没有重复（小写情况下）， 如果有重复就抛出异常
        if User.objects.filter(email=data['email'].lower()).exists():
            raise exceptions.ValidationError({

                'email': 'This email address has been occupied'

            })
        # 如果以上通过就返回data， 这里没有对data做特别处理
        return data

    def create(self, validated_data):
        # 加lower()的目的就是把用户输入的username和password转化为小写存入表单中
        # 因为用户一般会忘记大小写，所以这里就不区分大小写
        username = validated_data['username'].lower()
        email = validated_data['email'].lower()
        password = validated_data['password']

        # 这里的create_user是django自己定义的method, 主要是把password加密处理后存入表单
        # 一般使用create（）
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
        )

        return user

