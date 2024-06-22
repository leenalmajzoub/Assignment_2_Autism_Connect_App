from django.test import TestCase, Client
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User
from social.models import Event, ThreadModel, MessageModel, News, NewsComment, Post, Comment, UserProfile, Notification, ThreadModel, MessageModel
from social.forms import ThreadForm

# Test Event Views
class EventViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.event1 = Event.objects.create(
            title="Event 1", description="Description 1",
            start_time="2024-06-21 12:00:00", end_time="2024-06-21 14:00:00",
            organizer=self.user, place="Place 1"
        )
        self.event2 = Event.objects.create(
            title="Event 2", description="Description 2",
            start_time="2024-06-22 12:00:00", end_time="2024-06-22 14:00:00",
            organizer=self.user, place="Place 2"
        )

    def test_event_list_view(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('event-list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'social/event_list.html')
        self.assertIn('event_list', response.context)
        self.assertIn('form', response.context)
        self.assertIn('shareform', response.context)
    
    def test_event_detail_view_get(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('event-detail', args=[self.event1.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'social/event_detail.html')
        self.assertIn('event', response.context)
        self.assertIn('share_form', response.context)

    def test_share_event_view_post(self):
        self.client.login(username='testuser', password='password')
        response = self.client.post(reverse('share-event', args=[self.event1.pk]), {'recipient_username': 'recipient'})
        self.assertRedirects(response, reverse('event-detail', args=[self.event1.pk]))

    def test_join_event_post(self):
        self.client.login(username='testuser', password='password')
        response = self.client.post(reverse('join-event', args=[self.event1.pk]), {'next': '/'})
        self.assertRedirects(response, '/')
        self.assertTrue(self.event1.attendees.filter(pk=self.user.pk).exists())

    
    def test_unjoin_event_post(self):
        self.client.login(username='testuser', password='password')
        self.event1.attendees.add(self.user)
        response = self.client.post(reverse('unjoin-event', args=[self.event1.pk]), {'next': '/'})
        self.assertRedirects(response, '/')
        self.assertFalse(self.event1.attendees.filter(pk=self.user.pk).exists())
    
    def test_list_attendees_view(self):
        self.client.login(username='testuser', password='password')
        self.event1.attendees.add(self.user)
        response = self.client.get(reverse('list-attendees', args=[self.event1.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'social/attendees_list.html')
        self.assertIn('event', response.context)
        self.assertIn('attendees', response.context)
    
    def test_remove_attendee_post(self):
        self.client.login(username='testuser', password='password')
        self.event1.attendees.add(self.user)
        response = self.client.post(reverse('remove-attendee', args=[self.event1.pk]), {'attendee_pk': self.user.pk, 'next': '/'})
        self.assertRedirects(response, '/')
        self.assertFalse(self.event1.attendees.filter(pk=self.user.pk).exists())
    
    def test_event_edit_view(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('event-edit', args=[self.event1.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'social/event_edit.html')

    def test_event_edit_post(self):
        self.client.login(username='testuser', password='password')
        response = self.client.post(reverse('event-edit', args=[self.event1.pk]), {
            'title': 'Updated Title',
            'description': 'Updated Description',
            'start_time': '2024-06-21 15:00:00',
            'end_time': '2024-06-21 17:00:00',
            'attendees_allowed': 20,
            'place': 'Updated Place'
        })
        self.assertRedirects(response, reverse('event-detail', args=[self.event1.pk]))
        self.event1.refresh_from_db()
        self.assertEqual(self.event1.title, 'Updated Title')
        self.assertEqual(self.event1.description, 'Updated Description')

    def test_event_delete_view(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('event-delete', args=[self.event1.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'social/event_delete.html')

    def test_event_delete_post(self):
        self.client.login(username='testuser', password='password')
        response = self.client.post(reverse('event-delete', args=[self.event1.pk]))
        self.assertRedirects(response, reverse('post-list'))
        with self.assertRaises(Event.DoesNotExist):
            Event.objects.get(pk=self.event1.pk)

# Test News Views
class NewsViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.other_user = User.objects.create_user(username='otheruser', password='password')

        self.news = News.objects.create(
            title='Test News',
            body='This is a test news article.',
            author=self.user,
            created_on=timezone.now()
        )

        self.comment = NewsComment.objects.create(
            news=self.news,
            author=self.user,
            comment='Test comment on news.',
            created_on=timezone.now()
        )

    def test_news_list_view(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('news-list'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['news_list'], [self.news])

    def test_news_detail_view(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('news-detail', args=[self.news.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['news'], self.news)
        self.assertContains(response, self.news.title)
        self.assertContains(response, self.news.body)

    def test_news_edit_view(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('news-edit', args=[self.news.pk]))
        self.assertEqual(response.status_code, 200)
        
        edited_title = 'Edited News Title'
        edited_body = 'This is an edited news article.'
        response = self.client.post(reverse('news-edit', args=[self.news.pk]), {
            'title': edited_title,
            'body': edited_body
        })
        self.assertRedirects(response, reverse('news-detail', args=[self.news.pk]))
        self.news.refresh_from_db()
        self.assertEqual(self.news.title, edited_title)
        self.assertEqual(self.news.body, edited_body)

    def test_news_edit_view_with_wrong_user(self):
        self.client.login(username='otheruser', password='password')
        response = self.client.get(reverse('news-edit', args=[self.news.pk]))
        self.assertEqual(response.status_code, 403)  

    def test_news_delete_view(self):
        self.client.login(username='testuser', password='password')
        response = self.client.post(reverse('news-delete', args=[self.news.pk]))
        self.assertRedirects(response, reverse('post-list'))
        self.assertFalse(News.objects.filter(pk=self.news.pk).exists())

    def test_news_delete_view_with_wrong_user(self):
        self.client.login(username='otheruser', password='password')
        response = self.client.post(reverse('news-delete', args=[self.news.pk]))
        self.assertEqual(response.status_code, 403)  

    def test_news_comment_reply_view(self):
        self.client.login(username='testuser', password='password')
        response = self.client.post(reverse('newscomment-reply', args=[self.news.pk, self.comment.pk]), {
            'comment': 'Reply to comment.',
        })
        self.assertRedirects(response, reverse('news-detail', args=[self.news.pk]))
        self.assertTrue(NewsComment.objects.filter(comment='Reply to comment.').exists())

    def test_news_comment_delete_view(self):
        self.client.login(username='testuser', password='password')
        response = self.client.post(reverse('newscomment-delete', args=[self.news.pk, self.comment.pk]))
        self.assertRedirects(response, reverse('news-detail', args=[self.news.pk]))
        self.assertFalse(NewsComment.objects.filter(pk=self.comment.pk).exists())

    def test_add_news_comment_like_view(self):
        self.client.login(username='testuser', password='password')
        response = self.client.post(reverse('newscomment-like', args=[self.news.pk, self.comment.pk]))
        self.assertRedirects(response, '/')
        self.assertIn(self.user, self.comment.likes.all())

    def test_add_news_comment_dislike_view(self):
        self.client.login(username='testuser', password='password')
        response = self.client.post(reverse('newscomment-dislike', args=[self.news.pk, self.comment.pk]))
        self.assertRedirects(response, '/')
        self.assertIn(self.user, self.comment.dislikes.all())

# Test Post Views
class PostViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username='testuser', password='password')
        self.user2 = User.objects.create_user(username='testuser 2', password='password')
        userprofile1 = UserProfile.objects.get(user=self.user1)
        userprofile1.followers.add(self.user2)

        self.client.login(username='testuser 2', password='password')

        self.post = Post.objects.create(
            body='Test Post',
            author=self.user1,
            created_on=timezone.now()
        )

        self.comment = Comment.objects.create(
            comment='Test Comment',
            author=self.user1,
            post=self.post,
        )

        self.event = Event.objects.create(
            title='Test Event',
            organizer=self.user1,
            description='Test event description',
            end_time=timezone.now() + timezone.timedelta(days=1),
            attendees_allowed = 10,
            place = 'Test Place',
        )


        self.news = News.objects.create(
            title='Test News',
            body='Test News body',
            author=self.user1,
        )

    def test_post_list_view(self):

        expected_context = {
            'event_list': [self.event],
            'post_list': [self.post],
            'news_list': [self.news],
        }

        url = reverse('post-list')
        response = self.client.get(url)

        actual_context = {
            'event_list': list(response.context['event_list']),
            'post_list': list(response.context['post_list']),
            'news_list': list(response.context['news_list']),
        }

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'social/post_list.html')
        self.assertDictEqual(expected_context, actual_context)

    def test_post_detail_view(self):

        expected_context = {
            'post': self.post,
            'comments': [self.comment],
        }

        url = reverse('post-detail', args=[self.post.pk])
        response = self.client.get(url)

        actual_context = {
            'post': response.context['post'],
            'comments': list(response.context['comments']),
        }

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'social/post_detail.html')
        self.assertDictEqual(expected_context, actual_context)

    def test_post_creation(self):
        url = reverse('post-list')
        data = {
            'form_type': 'post',
            'body': 'New test post',
        }
        
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, 200)  

        self.assertTrue(Post.objects.filter(body='New test post').exists())

    def test_event_creation(self):
        url = reverse('post-list')
        data = {
            'form_type': 'event',
            'title': 'New test event',
            'description': 'New description for event',
            'attendees_allowed': 10,
            'place': 'New Test Place',
            'start_time': timezone.now(),
            'end_time': timezone.now() + timezone.timedelta(days=1)
        }
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, 200)  

        self.assertTrue(Event.objects.filter(title='New test event').exists())

    def test_news_creation(self):
        url = reverse('post-list')
        data = {
            'form_type': 'news',
            'title': 'New test news',
            'body': 'Test news body',
        }
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, 200)  

        self.assertTrue(News.objects.filter(title='New test news').exists())

    def test_comment_creation(self):
        url = reverse('post-detail', args=[self.post.pk])
        data = {
            'comment': 'New test comment',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)  

        self.assertTrue(Comment.objects.filter(comment='New test comment').exists())

    def test_post_edit_view(self):
        self.client.login(username='testuser', password='password')

        url = reverse('post-edit', args=[self.post.pk])
        data = {
            'body': 'Updated test post',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302) 

        self.post.refresh_from_db()
        self.assertEqual(self.post.body, 'Updated test post')

    def test_post_delete_view(self):
        self.client.login(username='testuser', password='password')

        url = reverse('post-delete', args=[self.post.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)  

        self.assertFalse(Post.objects.filter(pk=self.post.pk).exists())

    def test_comment_delete_view(self):
        self.client.login(username='testuser', password='password')

        url = reverse('comment-delete', args=[self.post.pk, self.comment.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)  

        self.assertFalse(Comment.objects.filter(pk=self.comment.pk).exists())

    def test_add_like_view(self):
        url = reverse('like', args=[self.post.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)  

        self.assertTrue(self.post.likes.filter(pk=self.user2.pk).exists())

    def test_add_dislike_view(self):
        url = reverse('dislike', args=[self.post.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)  

        self.assertTrue(self.post.dislikes.filter(pk=self.user2.pk).exists())

    def test_add_comment_like_view(self):
        url = reverse('comment-like', args=[self.post.pk, self.comment.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)  

        self.assertTrue(self.comment.likes.filter(pk=self.user2.pk).exists())

    def test_add_comment_dislike_view(self):
        url = reverse('comment-dislike', args=[self.post.pk, self.comment.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)  

        self.assertTrue(self.comment.dislikes.filter(pk=self.user2.pk).exists())

    def test_shared_post_view(self):
        url = reverse('share-post', args=[self.post.pk])
        data = {
            'body': 'Shared post body',
        }

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)  

        self.assertTrue(Post.objects.filter(shared_body='Shared post body').exists())

    def test_explore_view(self):
        url = reverse('explore')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'social/explore.html')

    def test_explore_search(self):
        url = reverse('explore')
        data = {
            'query': 'test',
            'active_form': 'post'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)  

# Test Profile Views
class ProfileViewsTest(TestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='password')
        self.user2 = User.objects.create_user(username='user2', password='password')

        self.profile1 = UserProfile.objects.get(user=self.user1)
        self.profile2 = UserProfile.objects.get(user=self.user2)

        self.post = Post.objects.create(author=self.user1, body='Test Post')

        self.client.login(username='user1', password='password')

    def test_profile_view(self):
        url = reverse('profile', args=[self.profile1.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'social/profile.html')
        self.assertEqual(response.context['user'], self.user1)
        self.assertEqual(response.context['profile'], self.profile1)
        self.assertQuerysetEqual(response.context['posts'], Post.objects.filter(author=self.user1))
        self.assertEqual(response.context['number_of_followers'], self.profile1.followers.count())
        self.assertFalse(response.context['is_following'])

    def test_profile_edit_view(self):
        url = reverse('profile-edit', args=[self.profile1.pk])
        data = {
            'name': 'Updated User One',
            'bio': 'Updated bio',
            'birth_date': '2000-01-01',
            'location': 'Updated Location',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)  # Redirect status

        self.profile1.refresh_from_db()
        self.assertEqual(self.profile1.name, 'Updated User One')
        self.assertEqual(self.profile1.bio, 'Updated bio')
        self.assertEqual(self.profile1.birth_date.strftime('%Y-%m-%d'), '2000-01-01')
        self.assertEqual(self.profile1.location, 'Updated Location')

    def test_add_follower(self):
        url = reverse('add-follower', args=[self.profile2.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)  # Redirect status

        self.assertTrue(self.profile2.followers.filter(pk=self.user1.pk).exists())
        self.assertTrue(Notification.objects.filter(notification_type=3, from_user=self.user1, to_user=self.user2).exists())

    def test_remove_follower(self):
        self.profile2.followers.add(self.user1)
        url = reverse('remove-follower', args=[self.profile2.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)  # Redirect status

        self.assertFalse(self.profile2.followers.filter(pk=self.user1.pk).exists())

    def test_user_search(self):
        url = reverse('profile-search')
        response = self.client.get(url, {'query': 'user1'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'social/search.html')
        self.assertQuerysetEqual(response.context['profile_list'], UserProfile.objects.filter(user__username__icontains='user1'))

    def test_list_followers(self):
        self.profile1.followers.add(self.user2)
        url = reverse('list-followers', args=[self.profile1.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'social/followers_list.html')
        self.assertQuerysetEqual(response.context['followers'], self.profile1.followers.all())

# Test Notifications Views
class NotificationViewsTest(TestCase):
    def setUp(self):

        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')

        self.other_user = User.objects.create_user(username='otheruser', password='12345')
        self.post = Post.objects.create(author=self.other_user, body='Test post')
        self.profile = UserProfile.objects.get(user=self.other_user)
        self.thread = ThreadModel.objects.create(user=self.other_user, receiver=self.user)
        
        self.notification_post = Notification.objects.create(notification_type=1, from_user=self.other_user, to_user=self.user, post=self.post)
        self.notification_follow = Notification.objects.create(notification_type=2, from_user=self.other_user, to_user=self.user)
        self.notification_thread = Notification.objects.create(notification_type=3, from_user=self.other_user, to_user=self.user, thread=self.thread)
        self.notification_general = Notification.objects.create(notification_type=4, from_user=self.other_user, to_user=self.user)

    def test_post_notification_view(self):
        url = reverse('post-notification', kwargs={'notification_pk': self.notification_post.pk, 'post_pk': self.post.pk})
        response = self.client.get(url)

        self.notification_post.refresh_from_db()
        self.assertTrue(self.notification_post.user_has_seen)
        self.assertRedirects(response, reverse('post-detail', kwargs={'pk': self.post.pk}))

    def test_follow_notification_view(self):
        url = reverse('follow-notification', kwargs={'notification_pk': self.notification_follow.pk, 'profile_pk': self.profile.pk})
        response = self.client.get(url)

        self.notification_follow.refresh_from_db()
        self.assertTrue(self.notification_follow.user_has_seen)
        self.assertRedirects(response, reverse('profile', kwargs={'pk': self.profile.pk}))

    def test_thread_notification_view(self):
        url = reverse('thread-notification', kwargs={'notification_pk': self.notification_thread.pk, 'object_pk': self.thread.pk})
        response = self.client.get(url)

        self.notification_thread.refresh_from_db()
        self.assertTrue(self.notification_thread.user_has_seen)
        self.assertRedirects(response, reverse('thread', kwargs={'pk': self.thread.pk}))

    def test_remove_notification_view(self):
        url = reverse('notification-delete', kwargs={'notification_pk': self.notification_general.pk})
        response = self.client.delete(url)

        self.notification_general.refresh_from_db()
        self.assertTrue(self.notification_general.user_has_seen)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), 'Success')

# Thread Views Test
class ThreadViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')

        self.other_user = User.objects.create_user(username='otheruser', password='12345')
        self.thread = ThreadModel.objects.create(user=self.user, receiver=self.other_user)
        self.message = MessageModel.objects.create(thread=self.thread, sender_user=self.user, receiver_user=self.other_user, body='Test message')

    def test_list_threads_view(self):
        url = reverse('inbox')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'social/inbox.html')
        self.assertIn(self.thread, response.context['threads'])

    def test_create_thread_get_view(self):
        url = reverse('create-thread')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'social/create_thread.html')
        self.assertIsInstance(response.context['form'], ThreadForm)

    def test_create_thread_post_view(self):
        url = reverse('create-thread')
        data = {
            'username': 'otheruser',
        }
        response = self.client.post(url, data)
        
        thread = ThreadModel.objects.filter(user=self.user, receiver=self.other_user).first()

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('thread', kwargs={'pk': thread.pk}))
        self.assertIsNotNone(thread)

    def test_thread_view(self):
        url = reverse('thread', kwargs={'pk': self.thread.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'social/thread.html')
        self.assertEqual(response.context['thread'], self.thread)
        self.assertIn(self.message, response.context['message_list'])

    def test_create_message_view(self):
        url = reverse('create-message', kwargs={'pk': self.thread.pk})
        data = {
            'body': 'New message',
        }
        response = self.client.post(url, data)

        message = MessageModel.objects.filter(thread=self.thread, body='New message').first()

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('thread', kwargs={'pk': self.thread.pk}))
        self.assertIsNotNone(message)