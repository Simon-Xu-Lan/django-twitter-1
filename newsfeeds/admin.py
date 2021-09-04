from django.contrib import admin
from newsfeeds.models import NewsFeed

# Register your models here.
@admin.register(NewsFeed)
class NewsFeedAdmin(admin.ModelAdmin):
    list_display = ('user', 'tweet', 'created_at')
    # 按照date_hierarchy进行时间得筛选
    date_hierarchy = 'created_at'
