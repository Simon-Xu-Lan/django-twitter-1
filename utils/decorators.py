from rest_framework.response import Response
from rest_framework import status
from functools import wraps

def required_params(request_attr='query_params', params=None):
    """
    当我们使用 @required_params(params=['some_param']) 的时候
    这个 required_params 函数应该需要返回一个 decorator 函数，这个 decorator 函数的参数
    就是被 @required_params 包裹起来的函数 view_func
    """

    # 用GET方法时， 数据是在request.query_params
    # 用POST方法时，数据是在request.data

    # 从效果上说， 参数中写params=[], 很多时候也没有太大问题
    # 但是从好的编程习惯来说， 函数的参数列表中的值不能是一个mutable的参数
    if params is None:
        params = []

    def decorator(view_func):
        """
        decorator 函数通过 wraps 来将 view_func 里的参数解析出来传递给 _wrapped_view
        这里的 instance 参数其实就是在 view_func 里的 self
        """
        # wraps的作用是把view_func这个函数的参数全部拿出来，传到下面一层
        @wraps(view_func)
        def _wrapped_view(instance, request, *args, **kwargs):
            data = getattr(request, request_attr)
            missing_params = [
                param
                for param in params
                if param not in data
            ]
            if missing_params:
                params_str = ','.join(missing_params)
                return Response({
                    'message': 'missing {} in request'.format(params_str),
                    'success': False,
                }, status=status.HTTP_400_BAD_REQUEST)

            # 做完检测之后，再去调用被 @required_params 包裹起来的 view_func
            return view_func(instance, request, *args, **kwargs)
        return _wrapped_view
    return decorator