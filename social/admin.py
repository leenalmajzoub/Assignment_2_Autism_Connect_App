from django.contrib import admin
from .models import Post, UserProfile, Comment, Notification, ThreadModel, Event, News, NewsComment, Tag, NewsTag, EventTag, MessageModel

admin.site.register(Post)
admin.site.register(UserProfile)
admin.site.register(Comment)
admin.site.register(Notification)
admin.site.register(ThreadModel)
admin.site.register(Event)
admin.site.register(News)
admin.site.register(NewsComment)
admin.site.register(Tag)
admin.site.register(NewsTag)
admin.site.register(EventTag)
admin.site.register(MessageModel)
