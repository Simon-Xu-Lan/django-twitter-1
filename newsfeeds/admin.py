from django.contrib import admin
from newsfeeds.models import NewsFeed

# Register your models here.
@admin.register(NewsFeed)
class NewsFeedAdmin(admin.ModelAdmin):
    list_display = ('user', 'tweet', 'created_at')
    # 按照date_hierarchy进行时间得筛选
    # date_hierarchy = 'created_at'
    # date_hierarchy: the change list page gets a date drill-down navigation bar at the top of the list
    # date_hierarchy 就是在 admin界面 comments list 页面上免加一行 data的menu