from django.db import models
from django.contrib.auth.models import User
from utils.time_helper import utc_now
from likes.models import Like
from django.contrib.contenttypes.models import ContentType


class Tweet(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        help_text='Who posts this tweet',
        # verbose_name=u'谁发了这个贴'
    )
    content = models.CharField(max_length=255)
    # content = models.CharField(max_length=255， db_index=True) 单个索引设定
    created_at = models.DateTimeField(auto_now_add=True) #创建是更新值
    # update_at = models.DateTimeField(auto_noe=True) # 更改时更新值

    class Meta:
        index_together = (('user', 'created_at'),) #联合索引是需要在class Meta中指定
        # ordering 为查询操作指定默认排序规则， 先按照user升序排序，再按created_at降序排序
        # ordering设定了queryset的排序
        # ordering 对数据库不会产生影响，只会对queryset产生影响
        # -created是倒序排列
        ordering = ('user', '-created_at')

    @property
    def hours_to_now(self):
        # datetime.now 不带时区信息，需要增加上 utc 的时区信息
        # createed_at(): Django add time zone info to created_at automatically
        return (utc_now() - self.created_at).seconds // 3600

    # 下面在model里面定义获取comment
    # @property
    # def comments(self):
    #     return Comment.objects.filter(tweet=self)
    #       or
    #     return self.comment_set.all()

    @property
    def like_set(self):
        return Like.objects.filter(
            content_type=ContentType.objects.get_for_model(Tweet),
            object_id=self.id,
        ).order_by('-created_at')

    def __str__(self):
        # 这里是你执行 print(tweet instance) 的时候会显示的内容
        # Django damin site use it to display an object
        return f'{self.user} {self.created_at} : {self.content}'


# Each field is specified as a class attribute,
# and each attribute maps to a database column.
# id field is added automatically.
