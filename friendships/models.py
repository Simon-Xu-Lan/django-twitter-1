from django.db import models
from django.contrib.auth.models import User


class Friendship(models.Model):
    from_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='following_friendship_set',
    )
    to_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='follower_friendship_set',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        index_together: (
            # 获取我关注的所有人，按照关注时间排序
            ('from_user_id', 'created_at'),
            # 获得关注我的所有人，按照关注时间排序
            ('to_user_id', 'created_at')
        )
        # 一组字段名，合起来必须是唯一的
        # 在数据库层面设定唯一性约束， 避免出现重复，在高并发情况下会出现重复
        unique_together = (('from_user_id', 'to_user_id'))

    def __str__(self):
        return f'{self.from_user_id} followed {self.to_user_id}'

