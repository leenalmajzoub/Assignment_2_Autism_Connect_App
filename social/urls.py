from django.urls import path
from .views import PostListView, PostDetailView, PostEditView, PostDeleteView, CommentDeleteView, ProfileView, ProfileEditView, AddFollower, RemoveFollower, AddLike, AddDislike, UserSearch, ListFollowers, AddCommentLike, AddCommentDislike, CommentReplyView, PostNotification, FollowNotification, ThreadNotification, RemoveNotification, CreateThread, ListThreads, ThreadView, CreateMessage, SharedPostView, Explore, EventListView, EventDetailView, JoinEvent, UnjoinEvent, ListAttendees, RemoveAttendee
from .views import EventEditView, EventDeleteView, ShareEventView
from .views import NewsListView, NewsDetailView, NewsEditView, NewsDeleteView, NewsCommentReplyView, NewsCommentDeleteView, AddNewsCommentLike, AddNewsCommentDislike


urlpatterns = [

    # General URLs
    path('', PostListView.as_view(), name='post-list'),
    path('explore/', Explore.as_view(), name='explore'),
    path('search/', UserSearch.as_view(), name='profile-search'),

    # Events Related URLs
    path('event/', EventListView.as_view(), name='event-list'),
    path('event/<int:pk>/', EventDetailView.as_view(), name='event-detail'),
    path('event/<int:pk>/share/', ShareEventView.as_view(), name='share-event'),
    path('event/<int:pk>/join', JoinEvent.as_view(), name='join-event'),
    path('event/<int:pk>/unjoin', UnjoinEvent.as_view(), name='unjoin-event'),
    path('event/<int:pk>/attendees_list', ListAttendees.as_view(), name='list-attendees'),
    path('event/<int:pk>/remove_attendee/', RemoveAttendee.as_view(), name='remove-attendee'),
    path('event/edit/<int:pk>/', EventEditView.as_view(), name='event-edit'),
    path('event/<int:pk>/delete', EventDeleteView.as_view(), name='event-delete'),

    # News Related URLs
    path('news/', NewsListView.as_view(), name='news-list' ),
    path('news/<int:pk>', NewsDetailView.as_view(), name='news-detail' ),
    path('news/edit/<int:pk>', NewsEditView.as_view(), name='news-edit' ),
    path('news/delete/<int:pk>', NewsDeleteView.as_view(), name='news-delete' ),
    path('news/<int:news_pk>/comment/<int:pk>/reply', NewsCommentReplyView.as_view(), name='newscomment-reply'),
    path('news/<int:news_pk>/comment/delete/<int:pk>/', NewsCommentDeleteView.as_view(), name='newscomment-delete'),
    path('news/<int:news_pk>/comment/<int:pk>/like', AddNewsCommentLike.as_view(), name='newscomment-like'),
    path('news/<int:news_pk>/comment/<int:pk>/dislike', AddNewsCommentDislike.as_view(), name='newscomment-dislike'),

    # Post Related URLs
    path('post/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('post/edit/<int:pk>/', PostEditView.as_view(), name='post-edit'),
    path('post/delete/<int:pk>/', PostDeleteView.as_view(), name='post-delete'),
    path('post/<int:post_pk>/comment/delete/<int:pk>/', CommentDeleteView.as_view(), name='comment-delete'),
    path('post/<int:post_pk>/comment/<int:pk>/like', AddCommentLike.as_view(), name='comment-like'),
    path('post/<int:post_pk>/comment/<int:pk>/dislike', AddCommentDislike.as_view(), name='comment-dislike'),
    path('post/<int:post_pk>/comment/<int:pk>/reply', CommentReplyView.as_view(), name='comment-reply'),
    path('post/<int:pk>/like', AddLike.as_view(), name='like'),
    path('post/<int:pk>/dislike', AddDislike.as_view(), name='dislike'),
    path('post/<int:pk>/share', SharedPostView.as_view(), name='share-post'),

    # Profile Related URLs
    path('profile/<int:pk>/', ProfileView.as_view(), name='profile'),
    path('profile/edit/<int:pk>/', ProfileEditView.as_view(), name='profile-edit'),
    path('profile/<int:pk>/followers/', ListFollowers.as_view(), name='list-followers'),
    path('profile/<int:pk>/followers/add', AddFollower.as_view(), name='add-follower'),
    path('profile/<int:pk>/followers/remove', RemoveFollower.as_view(), name='remove-follower'),

    # Notifications Related URLs
    path('notification/<int:notification_pk>/post/<int:post_pk>', PostNotification.as_view(), name='post-notification'),
    path('notification/<int:notification_pk>/profile/<int:profile_pk>', FollowNotification.as_view(), name='follow-notification'),
    path('notification/<int:notification_pk>/thread/<int:object_pk>', ThreadNotification.as_view(), name='thread-notification'),
    path('notification/delete/<int:notification_pk>', RemoveNotification.as_view(), name='notification-delete'),

    # Messages Related URLs
    path('inbox/', ListThreads.as_view(), name='inbox'),
    path('inbox/create-thread/', CreateThread.as_view(), name='create-thread'),
    path('inbox/<int:pk>/', ThreadView.as_view(), name='thread'),
    path('inbox/<int:pk>/create-message/', CreateMessage.as_view(), name='create-message'),
]