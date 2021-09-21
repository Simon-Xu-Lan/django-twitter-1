from friendships.models import Friendship
from newsfeeds.models import NewsFeed


class FriendshipService(object):

    # service 里大部分是class method， 因为不需要new instance 出来
    @classmethod
    def get_followers(cls, user):
        # 错误写法1
        # 这种写法会导致 N + 1 Queries 问题
        # filter出所有friendships耗费一次query
        # for循环每个friendship取from_user又耗费N次queries
        # 就是N次从 user table 中 query user
        # 这种写法会产生N次数据库操作，耗费时间很多，效率很低
        # friendships = Friendship.objects.filter(to_user=user)
        # return [friendship.from_user for friendship in friendships]

        # 错误写法2
        # 这样的写法用了JOIN操作， friendship table and user table 在from——user这个
        # 属性上JOIN起来。 join操作在大规模用户的web场景下是禁用的， 因为非常慢。
        # select_related === JOIN
        # friendships = Friendship.objects.filter(
        #     to_user=user
        # ).select_related('from_user')
        # return [friendship.from_user for friendship in friendships]

        # 正确写法一，自己动手filter ID， 使用IN Query 查询
        # 第二句写from_user_id 就只是从friendship里面拿出 from_user_id, 这样不涉及到join user table
        # 第二句形成了一个 from_user_id 的 list
        # 第三句用 in 语句做 query， 虽然in语句效率也不是很高，但是比join语句高多了
        # 这样总共是两句query
        # friendships = Friendship.objects.filter(to_user=user)
        # follower_ids = [friendship.from_user_id for friendship in friendships]
        # followers = User.objects.filter(id__in=follower_ids)


        # 正确写法二， 使用prefetch_related, 会自动执行成两条语句， 用In query查询
            # prefetch_related 就是上面正确写法1中的两条SQL语句。
            # DRF 提供 prefetch_related method 作为上面正确写法1的简单写法
        # 实际和正确写法1是一样的
        # 实际执行的SQL查询语句和上面一样的，一共两条SQL queries
        friendships = Friendship.objects.filter(
            to_user=user,
        ).prefetch_related('from_user')
        return [friendship.from_user for friendship in friendships]

