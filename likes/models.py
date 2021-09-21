from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


# Create your models here.
class Like(models.Model):
    # ContentType: https://docs.djangoproject.com/en/3.1/ref/contrib/contenttypes/#generic-relations
    # ContentType: 是指不同的model
    # A normal Foreignkey can only "point to" ont other models.
    # The Foreignkey allows the relationship to be with one and only one models
    # The contentType provides a special field key(GenericForeignKey),which allows the relationship to be with any models.
    object_id = models.PositiveIntegerField() # tweet_id or comment_id
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True)
    # content_object不是一个实际的column， 数据库表中没有这一列
    # content_object只是一个快捷方式, 根据（'content_type', 'object_id'这两个参数）去拿到具体的object(tweet or comment)，
    content_object = GenericForeignKey('content_type', 'object_id')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateField(auto_now_add=True)

    class Meta:
        # 这里使用 unigue_together, 也就会建一个 <user, content_tpye, object_id>的索引。
        # 这个索引同时还可以具备查询某个user like 了哪些不同的objects的功能
        # 因此如果 unique together 改成 < content_type, object_id, user> 就没有这样的效果了
        # web是个高并发的环境，如果在API中设定唯一性，有可能在数据库在创建2个相同的like
        # 只有在数据库层面设定唯一性，才能取保唯一性
        unique_together = (('user', 'content_type', 'object_id'), )  # 最后这个逗号一定要加

        index_together = (
            # 这个 index 的作用是可以按时间排序某个被 like 的 content_object 的所有 likes
            # 比如： 某个tweet下面的所有likes
            ('content_type', 'object_id', 'created_at'),
            # 可以查询一个user在那些tweet上点了赞
            ('user', 'content_type', 'created_at'),
        )  # 最后这个逗号一定要加
        # 这里使用 unique together 也就会建一个 <user, content_type, object_id>的索引。
        # 这个索引同时还可以具备查询某个 user like 了哪些不同的 objects 的功能
        # 因此如果 unique together 改成 <content_type, object_id, user>
        # 就没有这样的效果了

    def __str__(self):
        return '{} - {} liked {} {}'.format(
            self.created_at,
            self.user,
            self.content_type,
            self.object_id,
        )