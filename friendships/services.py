from friendships.models import Friendship
from newsfeeds.models import NewsFeed


class FriendshipService(object):

    @classmethod
    def get_followers(cls, user):
        # 错误写法1
        # 这种写法会导致 N + 1 Queries 问题
        # filter出所有friendships耗费一次query
        # for循环每个friendship取from_user又耗费N次queries
        # friendships = Friendship.objects.filter(to_user=user)
        # return [friendship.from_user for friendship in friendships]

        # 错误写法2
        # 这样的写法用了JOIN操作， friendship table and user table 在from——user这个
        # 属性上JOIN起来。 join操作在大规模用户的web场景下是禁用的， 因为非常慢。
        # select_related -> JOIN
        # friendships = Friendship.objects.filter(
        #     to_user=user
        # ).select_related('from_user')
        # return [friendship.from_user for friendship in friendships]

        # 正确写法一，自己动手filter ID， 使用IN Query 查询
        # friendships = Friendship.objects.filter(to_user=user)
        # follower_ids = [friendship.from_user_id for friendship in friendships]
        # followers = User.objects.filter(id__in=follower_ids)


        # 正确写法二， 使用prefetch_related, 会自动执行成两条语句， 用In query查询
        # 实际执行的SQL查询语句和上面一样的，一共两条SQL queries
        friendships = Friendship.objects.filter(
            to_user=user,
        ).prefetch_related('from_user')
        return [friendship.from_user for friendship in friendships]

