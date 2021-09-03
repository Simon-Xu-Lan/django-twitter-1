from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import (
    login as django_login,
    logout as django_logout,
    authenticate as django_authenticate,
)
from accounts.api.serializers import UserSerializer, LoginSerializer, SignupSerializer


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated] # 针对每个操作进行检测

# ModelViewSet自带的操作： list，retrieve, put, patch, destroy
# 下面是我们自定义的viewset

class AccountViewSet(viewsets.ViewSet):
    # serializer_class = UserSerializer # 这个serializer指定了username和email， browser界面就会出现一个输=框，里面有username和email的输入位置
    # serializer_class = LoginSerializer
    serializer_class = SignupSerializer

    # detail=False: 意思是url不是accounts/pk/login_status, 而是accounts/login_status, 即不需要在主资源目录下加pk。是针对所有的accounts， 不是某个具体的account
    # 如果改成的tail=true，那需要这样修改
        # @action(methods=['GET'], detail=True)
        # def login_status(self, request， pk):
        # urls会是： api/accounts/1/login_status
    # self，request这两个参数是默认自带的，所以要包括
    @action(methods=['GET'], detail=False)
    def login_status(self, request):
        # 定义返回data是dict format
        data = {
            'has_logged_in': request.user.is_authenticated, #如果登录，is_authenticated返回True， 否则False
            'ip': request.META['REMOTE_ADDR']  # get 宿主机 IP地址
        }
        if request.user.is_authenticated:
            # UserSerializer从request里拿到user的数据， 然后转化成json格式，serrialize data into json format.
            data['user'] = UserSerializer(request.user).data
        # 把data放入Response，并返回Response
        return Response(data)

    # detail=False表示这个动作是针对根目录account的。此时访问是api/accounts/login_status
        # ulr不需要写成api/accounts/1/login_status
        # 表示不是定义在某个object得动作， 这是定义在整个根目录的动作
    # 如果detail=true，那就是针对具体object的动作，此时访问必须是 api/accounts/1/login_status,
    #   此时login-status参数要加上primary key， login_status(self,request,pk)
    #     @action(methods=['GET'], detail=True)
    #     def login_status(self, request, pk):

    @action(methods=['POST'], detail=False)
    def logout(self, request):
        django_logout(request)
        return Response({'success': True}) # status=200是默认的，不需要特别写出

    @action(methods=['POST'], detail=False)
    def login(self, request):
        # 从request得到用户信息username和password， 然后去登录
        # get username and password from request
        # 如果是GET method， 我们从这里拿到data： data=request.query_params
        # POST method是从 request.date 拿数据， request.data就是用户POST请求的数据
        # 先把数据传给serializer，进行数据验证。
        # 建立一个serializer的实例
        serializer = LoginSerializer(data=request.data)
        # is_valid(）回去调用验证，验证会根据在serializer中设的field进行验证
            # 就是根据下面两个field进行验证：
            # username = serializers.CharField()
            # password = serializers.CharField()
        if not serializer.is_valid():
            return Response({
                "success": False,
                "message": "Please check input",
                "errors": serializer.errors,
            }, status=400)  # 400是客户端的错误
        # validation ok, login
        # 从经过验证后的validated_data中取数据
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        # debug技巧, 以下语句在vagrant terminal 打印出SQL语句
        # queryset = User.objects.filter(username=username)
        # print(queryset.query)

        # 下面验证用户不存在是可以放到serializer中进行
        # username不存在的情况
        # if not User.objects.filter(username=username).exists():
        #     return Response({
        #         "success": False,
        #         "message": "User does not exist"
        #     }, status=400)

        # 只有authenticate后的user， 才能用来login， 不然会出错
        user = django_authenticate(username=username, password=password)
        if not user or user.is_anonymous:
            return Response({
                "success": False,
                "message": "Username and password does not match"
            }, status=400)

        # 完成login
        django_login(request, user)

        return Response({
            "success": True,
            "user": UserSerializer(instance=user).data  #此时instance=也可以不写，UserSerializer(user)， 第一个参数是instance
        })  # status默认是200， 此时不需要加： status=200
            
    @action(methods=['POST'], detail=False)
    def signup(self, request):
        # 这样写是创建， 没有传具体instance进去，这个操作就是创建
        # 第一个参数是instance， 所以要用data=request.data， 否则会赋给instance
        serializer = SignupSerializer(data=request.data)
        # 下面这样写是更新，不是创建
        # serializer = SignupSerializer(instance=request.user, data=request.data)
        # 下面这样写是更新，而不是创建
            # serializer = SignupSerializer(instance=request.user, request.data)
        if not serializer.is_valid():
            return Response({
                "success": False,
                "message": "Please check input",
                "errors": serializer.errors,
            }, status=400)  # 400是客户端的错误

        user = serializer.save()
        django_login(request, user)
        return Response({
            'success': True,
            'user': UserSerializer(user).data
        }, status=201) #201是created，创建成功
