from friendships.services import FriendshipService
from newsfeeds.models import NewsFeed


class NewsFeedService(object):

    # 一般service 里面的方法都是class method， 因为不太new一个instance出来。都是class直接调用
    @classmethod
    def fanout_to_followers(self, tweet):

        # 错误的做法
        # 在production里，不允许for + query
        # web server and DB server 不是一台机器
        # 即使在一个机架上，他们之间的联系也是有延迟。
        # 通常不会在一个机架上。
        # 他们之间会有几ms的延迟， 甚至十几毫秒
        # 这样N次循环就会把延迟放大
        # followers = FriendshipService.get_followers(tweet.user)
        # for follower in followers:
        #     NewsFeed.objects.create(user=follower, tweet=tweet)


        # 正确的做法
        # 使用bulk_create, 会把insert语句合成一条
        # 下面 new a list of instance, 只是new instance, 没有数据库操作
        newsfeeds = [
            # 这里只是new instance， 只有后面加.save(), 才会存入数据库
            NewsFeed(user=follower, tweet=tweet)
            for follower in FriendshipService.get_followers(tweet.user)
        ]
        #  把自己也加进去，因为自己不是自己的follower， 但是自己应该可以看到自己的tweet
        newsfeeds.append(NewsFeed(user=tweet.user, tweet=tweet))
        NewsFeed.objects.bulk_create(newsfeeds)
