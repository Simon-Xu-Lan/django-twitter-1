from rest_framework.permissions import BasePermission


class IsObjectOwner(BasePermission):
    """
    这个Permission负责检查obj.user 是不是 == request.user
    这个类是比较通用的， 今后如果有其他地方用到这个类， 可以将这个文件放到一个共享的位置
    Permission会一个一个被执行
    - 如果是 detail=False 的action， 只检测 has_permission
    - 如果是 detail=True 的action，只检测 has_permission 和 has_object_permission
    如果出错的时候，默认的错误信息会显示 IsObjectOwner.message 中的内容
    """

    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        return request.user == obj.user