from django.db import models
from django.contrib.auth.models import User


class Friendship(models.Model):
    # To define a many-to-one relationship, use django.db.models.ForeignKey.
    # The related_name attribute specifies the name of the reverse relation from the User model back to your model.
    # If you don't specify a related_name, Django automatically creates one using the name of your model with the suffix _set, for instance User.map_set.all()
    # Every relationship in Django automatically gets its reverse relation added to the model. In the case of a ForeignKey or ManyToManyField that relation contains several objects. In that case, the default attribute name is set to <model>_set
    # DRF 反查机制： user.tweet_set 等价于 Tweet.objects.filter(user=user)
    # user.following_friendship_set, user作为from_user的Friendship，
    # user.follower_friendship_set, 是user作为to_user的Friendship
    # 如果用user.friendship_set，此时不清楚是user作为from_user的Friendship还是to_user的Friendship
    # following_friendship_set 和 follower_friendship_set 是别名，用来区分上述情况。

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
        unique_together = (('from_user_id', 'to_user_id'), )

    def __str__(self):
        return f'{self.from_user_id} followed {self.to_user_id}'

