import datetime
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone
from social.models import Event, EventTag, News, NewsTag, NewsComment, Post, Tag, Comment, UserProfile, Notification, ThreadModel, MessageModel

class EventTest(TestCase):

    def setUp(self):
        self.admin_user = User.objects.create_superuser(username='adminuser', email='admin@example.com', password='password')
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client = Client()
        self.event = Event.objects.create(
            title='Test Event 1',
            description='This is a test event',
            start_time=timezone.now(),
            end_time=timezone.now(),
            organizer=self.user,
            attendees_allowed=10,
            place='Test Place 1'
        )

    def test_event_count(self):
        self.assertEqual(Event.objects.count(), 1)

        event = Event.objects.create(
            title='Test Event 2',
            description='This is a test event 2',
            start_time=timezone.now(),
            end_time=timezone.now(),
            organizer=self.user,
            attendees_allowed=20,
            place='Test Place 2'
        )

        self.assertEqual(Event.objects.count(), 2)
    
    def test_event_created_correctly(self):

        start_time = timezone.now()
        end_time = timezone.now()

        event = Event.objects.create(
            title='Test Event 1',
            description='This is a test event',
            start_time=start_time,
            end_time=end_time,
            organizer=self.user,
            attendees_allowed=10,
            place='Test Place 1'
        )

        event_from_database = Event.objects.get(pk = event.pk)
        self.assertEqual(event_from_database.title, 'Test Event 1')
        self.assertEqual(event_from_database.description, 'This is a test event')
        self.assertEqual(event_from_database.start_time, start_time)
        self.assertEqual(event_from_database.end_time, end_time)
        self.assertEqual(event_from_database.organizer, self.user)
        self.assertEqual(event_from_database.attendees_allowed, 10)
        self.assertEqual(event_from_database.place, 'Test Place 1')

    def test_can_join(self):
        
        self.assertTrue(self.event.can_join)
    
    def test_add_user_to_attendees(self):

        # There was no attendees in self.event
        self.assertEqual(self.event.attendees.count(), 0)

        # Add a user to the event.attendees
        self.event.attendees.add(self.user)

        # Check if user is in attendee
        self.assertIn(self.user, self.event.attendees.all())
        
        # Check the number of attendees after user joined
        self.assertEqual(self.event.attendees.count(), 1)      

    def test_cant_join(self):
        event = Event.objects.create(
            title='Test Event 2',
            description='This is a test event 2',
            start_time=timezone.now(),
            end_time=timezone.now(),
            organizer=self.user,
            attendees_allowed=2,
            place='Test Place 2'
        )

        event.attendees.add(self.user)
        event.attendees.add(self.admin_user)
        
        self.assertEqual(event.attendees.count(), event.attendees_allowed)
        self.assertFalse(event.can_join())
    
    def test_create_tags(self):

        self.assertEqual(EventTag.objects.count(), 0)

        event = Event.objects.create(
            title='Test Event 2',
            description='This is a test event 2 #tag1 #tag2',
            start_time=timezone.now(),
            end_time=timezone.now(),
            organizer=self.user,
            attendees_allowed=2,
            place='Test Place 2'
        )

        # Create tags
        event.create_tags()

        # Make a list of tag names
        tag_names = [tag.name for tag in event.tags.all()]

        # Check if there are two tags
        self.assertEqual(EventTag.objects.count(), 2)
        
        # Check if tag1 is in the list
        self.assertIn('tag1', tag_names)
    
    def test_create_duplicate_tags(self):
        self.assertEqual(EventTag.objects.count(), 0)

        event = Event.objects.create(
            title='Test Event 2',
            description='This is a test event 2 #tag1 #tag1',
            start_time=timezone.now(),
            end_time=timezone.now(),
            organizer=self.user,
            attendees_allowed=2,
            place='Test Place 2'
        )

        event.create_tags()

        # Check there is only one tag
        self.assertEqual(EventTag.objects.count(), 1)
    
    def test_ordering_by_created_on(self):

        new_event = Event.objects.create(
            title='Test Event 2',
            description='This is a test event 2',
            start_time=timezone.now() - timezone.timedelta(days=1),
            end_time=timezone.now() - timezone.timedelta(days=1),
            organizer=self.user,
            attendees_allowed=10,
            place='Test Place 2'
        )
        
        ordered_events = Event.objects.all()
        
        self.assertEqual(ordered_events[0], new_event)
        self.assertEqual(ordered_events[1], self.event)

class NewsTest(TestCase):

    def setUp(self):
        self.admin_user = User.objects.create_superuser(username='adminuser', email='admin@example.com', password='password')
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client = Client()
        self.news = News.objects.create(
            title='Test News 1',
            body='This is a test news',
            author=self.user,
        )
    
    def test_event_count(self):
        self.assertEqual(News.objects.count(), 1)

        news = News.objects.create(
            title='Test News 2',
            body='This is a test news 2',
            author=self.user,
        )

        self.assertEqual(News.objects.count(), 2)
    
    def test_news_created_correctly(self):

        news = News.objects.create(
            title='Test News 2',
            body='This is a test news 2',
            author=self.user,
        )

        news_from_db = News.objects.get(pk=news.pk)

        self.assertEqual(news_from_db.title, 'Test News 2')
        self.assertEqual(news_from_db.body, 'This is a test news 2')
        self.assertEqual(news_from_db.author, self.user)
    
    def test_create_tags(self):

        news = News.objects.create(
            title='Test News 2',
            body='This is a test news 2 #tag1 #tag2',
            author=self.user,
        )

        news.create_tags()

        self.assertEqual(NewsTag.objects.count(), 2)

        tag_names = [tag.name for tag in news.tags.all()]
        self.assertIn('tag1', tag_names)
        self.assertIn('tag2', tag_names)

    def test_create_duplicate_tags(self):

        news = News.objects.create(
            title='Test News 2',
            body='This is a test news 2 #tag1 #tag1',
            author=self.user,
        )

        news.create_tags()

        self.assertEqual(NewsTag.objects.count(), 1)

    def test_add_like(self):
        self.assertEqual(self.news.likes.count(), 0)

        self.news.likes.add(self.user)

        self.assertIn(self.user, self.news.likes.all())
        self.assertEqual(self.news.likes.count(), 1)
   
    def test_add_dislike(self):
        self.assertEqual(self.news.dislikes.count(), 0)

        self.news.dislikes.add(self.user)

        self.assertIn(self.user, self.news.dislikes.all())
        self.assertEqual(self.news.dislikes.count(), 1)
    
    def test_ordering_by_created_on(self):

        new_news = News.objects.create(
            title='Another News',
            body='Another news body',
            created_on=timezone.now() + timezone.timedelta(days=1),
            author=self.user,
        )
        
        ordered_news = News.objects.all()
        
        self.assertEqual(ordered_news[0], new_news)
        self.assertEqual(ordered_news[1], self.news)

class NewsCommentTest(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(username='adminuser', email='admin@example.com', password='password')
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client = Client()
        self.news = News.objects.create(
            title='Test News 1',
            body='This is a test news',
            author=self.user,
        )  
   
    def test_create_comment(self):

        comment = NewsComment.objects.create(
            comment='This is a test comment',
            author=self.user,
            news=self.news,
        )
        self.assertEqual(comment.comment, 'This is a test comment')
        self.assertEqual(comment.author, self.user)
        self.assertEqual(comment.news, self.news)

    def test_create_tags(self):

        self.assertEqual(NewsTag.objects.count(), 0)

        comment = NewsComment.objects.create(
            comment='This is a test comment with #tag1 #tag2',
            author=self.user,
            news=self.news,
        )
        
        comment.create_tags()

        self.assertEqual(NewsTag.objects.count(), 2)

    def test_create_duplicate_tags(self):

        self.assertEqual(NewsTag.objects.count(), 0)

        comment = NewsComment.objects.create(
            comment='This is a test comment with #tag1 #tag1',
            author=self.user,
            news=self.news,
        )
        
        comment.create_tags()

        self.assertEqual(NewsTag.objects.count(), 1)

    def test_children_property(self):

        parent_comment = NewsComment.objects.create(
            comment='This is a parent comment',
            author=self.user,
            news=self.news,
        )

        child_comment = NewsComment.objects.create(
            comment='This is a child comment',
            author=self.user,
            news=self.news,
            parent=parent_comment
        )

        self.assertIn(child_comment, parent_comment.children)

    def test_is_parent_property(self):

        parent_comment = NewsComment.objects.create(
            comment='This is a parent comment',
            author=self.user,
            news=self.news,
        )

        child_comment = NewsComment.objects.create(
            comment='This is a child comment',
            author=self.user,
            news=self.news,
            parent=parent_comment
        )

        self.assertTrue(parent_comment.is_parent)
        self.assertFalse(child_comment.is_parent)

    def test_likes_dislikes(self):

        comment = NewsComment.objects.create(
            comment='This is a test comment',
            author=self.user,
            news=self.news,
        )

        comment.likes.add(self.user)
        self.assertIn(self.user, comment.likes.all())

        comment.dislikes.add(self.user)
        self.assertIn(self.user, comment.dislikes.all())

        comment.likes.remove(self.user)
        self.assertNotIn(self.user, comment.likes.all())

        comment.dislikes.remove(self.user)
        self.assertNotIn(self.user, comment.dislikes.all())

class PostTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.shared_user = User.objects.create_user(username='shareduser', password='password')

    def test_create_post(self):

        post = Post.objects.create(
            body='This is a test post',
            author=self.user,
            created_on=timezone.now()
        )

        self.assertEqual(post.body, 'This is a test post')
        self.assertEqual(post.author, self.user)

    def test_create_post_with_shared_body(self):

        post = Post.objects.create(
            body='This is a test post',
            shared_body='This is a shared post',
            author=self.user,
            shared_user=self.shared_user,
        )

        self.assertEqual(post.body, 'This is a test post')
        self.assertEqual(post.shared_body, 'This is a shared post')
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.shared_user, self.shared_user)

    def test_create_tags(self):
        
        self.assertEqual(Tag.objects.count(), 0)    

        post = Post.objects.create(
            body='This is a test post with #tag1 #tag2',
            author=self.user,
        )

        post.create_tags()

        tag_names = [tag.name for tag in post.tags.all()]

        self.assertEqual(Tag.objects.count(), 2)
        
        # Check if tag1 is in the list
        self.assertIn('tag1', tag_names)
    
    def test_create_duplicate_tags(self):
        
        self.assertEqual(Tag.objects.count(), 0)    

        post = Post.objects.create(
            body='This is a test post with #tag1 #tag1',
            author=self.user,
        )

        post.create_tags()
        
        tag_names = [tag.name for tag in post.tags.all()]

        self.assertEqual(Tag.objects.count(), 1)
        
        # Check if tag1 is in the list
        self.assertIn('tag1', tag_names)

    def test_likes_dislikes(self):

        post = Post.objects.create(
            body='This is a test post',
            author=self.user,
        )

        post.likes.add(self.user)
        self.assertIn(self.user, post.likes.all())

        post.dislikes.add(self.user)
        self.assertIn(self.user, post.dislikes.all())

        post.likes.remove(self.user)
        self.assertNotIn(self.user, post.likes.all())

        post.dislikes.remove(self.user)
        self.assertNotIn(self.user, post.dislikes.all())

class CommentTest(TestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(username='testuser1', password='password')
        self.user2 = User.objects.create_user(username='testuser2', password='password')

        self.post = Post.objects.create(
            body='This is a test post',
            author=self.user1,
        )

        self.tag = Tag.objects.create(name='testtag')

    def test_create_comment(self):
        comment = Comment.objects.create(
            comment='This is a test comment',
            author=self.user1,
            post=self.post,
            created_on=timezone.now()
        )
        self.assertEqual(comment.comment, 'This is a test comment')
        self.assertEqual(comment.author, self.user1)
        self.assertEqual(comment.post, self.post)

    def test_create_comment_with_tags(self):
        comment = Comment.objects.create(
            comment='This is a test comment with #testtag',
            author=self.user1,
            post=self.post,
            created_on=timezone.now()
        )

        comment.create_tags()
        self.assertTrue(Tag.objects.filter(name='testtag').exists())
        self.assertIn(Tag.objects.get(name='testtag'), comment.tags.all())

    def test_comment_hierarchy(self):
        parent_comment = Comment.objects.create(
            comment='This is a parent comment',
            author=self.user1,
            post=self.post,
            created_on=timezone.now()
        )

        child_comment = Comment.objects.create(
            comment='This is a child comment',
            author=self.user1,
            post=self.post,
            parent=parent_comment,
            created_on=timezone.now()
        )
        self.assertTrue(parent_comment.is_parent)
        self.assertFalse(child_comment.is_parent)
        self.assertIn(child_comment, parent_comment.children)

    def test_likes_dislikes(self):
        comment = Comment.objects.create(
            comment='This is a test comment',
            author=self.user1,
            post=self.post,
            created_on=timezone.now()
        )

        comment.likes.add(self.user1)
        self.assertIn(self.user1, comment.likes.all())

        comment.dislikes.add(self.user2)
        self.assertIn(self.user2, comment.dislikes.all())

        comment.likes.remove(self.user1)
        self.assertNotIn(self.user1, comment.likes.all())

        comment.dislikes.remove(self.user2)
        self.assertNotIn(self.user2, comment.dislikes.all())

class UserProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.user_profile = UserProfile.objects.get(user=self.user)

    def test_user_profile_creation(self):
        self.assertIsInstance(self.user_profile, UserProfile)
        self.assertEqual(self.user_profile.user.username, 'testuser')

    def test_user_profile_default_values(self):
        self.assertEqual(self.user_profile.name, None)
        self.assertEqual(self.user_profile.bio, None)
        self.assertEqual(self.user_profile.birth_date, None)
        self.assertEqual(self.user_profile.location, None)
        self.assertEqual(self.user_profile.picture.name, 'uploads/profile_pictures/default.png')

    def test_user_profile_update(self):
        self.user_profile.name = 'Test User'
        self.user_profile.bio = 'This is a test bio.'
        self.user_profile.birth_date = '2000-01-01'
        self.user_profile.location = 'Test Location'
        self.user_profile.save()

        updated_profile = UserProfile.objects.get(user=self.user)
        self.assertEqual(updated_profile.name, 'Test User')
        self.assertEqual(updated_profile.bio, 'This is a test bio.')
        self.assertEqual(updated_profile.birth_date.strftime('%Y-%m-%d'), '2000-01-01')
        self.assertEqual(updated_profile.location, 'Test Location')

    def test_followers(self):
        follower = User.objects.create_user(username='follower', password='password')
        self.user_profile.followers.add(follower)
        self.assertIn(follower, self.user_profile.followers.all())
        self.assertEqual(self.user_profile.followers.count(), 1)

    def test_followers_removal(self):
        follower = User.objects.create_user(username='follower', password='password')
        self.user_profile.followers.add(follower)
        self.user_profile.followers.remove(follower)
        self.assertNotIn(follower, self.user_profile.followers.all())
        self.assertEqual(self.user_profile.followers.count(), 0)

class NotificationModelTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='password')
        self.user2 = User.objects.create_user(username='user2', password='password')
        self.post = Post.objects.create(author=self.user1, body='Test Post')
        self.comment = Comment.objects.create(author=self.user2, post=self.post, comment='Test Comment')
        self.thread = ThreadModel.objects.create(user=self.user1, receiver=self.user2)

    def test_notification_creation_like(self):
        notification = Notification.objects.create(notification_type=1, to_user=self.user1, from_user=self.user2, post=self.post)
        self.assertIsInstance(notification, Notification)
        self.assertEqual(notification.notification_type, 1)
        self.assertEqual(notification.to_user, self.user1)
        self.assertEqual(notification.from_user, self.user2)
        self.assertEqual(notification.post, self.post)

    def test_notification_creation_comment(self):
        notification = Notification.objects.create(notification_type=2, to_user=self.user1, from_user=self.user2, comment=self.comment)
        self.assertIsInstance(notification, Notification)
        self.assertEqual(notification.notification_type, 2)
        self.assertEqual(notification.to_user, self.user1)
        self.assertEqual(notification.from_user, self.user2)
        self.assertEqual(notification.comment, self.comment)

    def test_notification_creation_follow(self):
        notification = Notification.objects.create(notification_type=3, to_user=self.user1, from_user=self.user2)
        self.assertIsInstance(notification, Notification)
        self.assertEqual(notification.notification_type, 3)
        self.assertEqual(notification.to_user, self.user1)
        self.assertEqual(notification.from_user, self.user2)

    def test_notification_creation_message(self):
        notification = Notification.objects.create(notification_type=4, to_user=self.user1, from_user=self.user2, thread=self.thread)
        self.assertIsInstance(notification, Notification)
        self.assertEqual(notification.notification_type, 4)
        self.assertEqual(notification.to_user, self.user1)
        self.assertEqual(notification.from_user, self.user2)
        self.assertEqual(notification.thread, self.thread)

    def test_notification_user_has_seen_default(self):
        notification = Notification.objects.create(notification_type=1, to_user=self.user1, from_user=self.user2, post=self.post)
        self.assertFalse(notification.user_has_seen)

    def test_notification_date_default(self):
        notification = Notification.objects.create(notification_type=1, to_user=self.user1, from_user=self.user2, post=self.post)
        self.assertIsNotNone(notification.date)

class ThreadModelTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='password')
        self.user2 = User.objects.create_user(username='user2', password='password')

    def test_thread_creation(self):
        thread = ThreadModel.objects.create(user=self.user1, receiver=self.user2)
        self.assertEqual(thread.user, self.user1)
        self.assertEqual(thread.receiver, self.user2)

class MessageModelTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='password')
        self.user2 = User.objects.create_user(username='user2', password='password')
        self.thread = ThreadModel.objects.create(user=self.user1, receiver=self.user2)
        self.event = Event.objects.create(
            title="Test Event",
            description="This is a test event",
            start_time=datetime.datetime(2024, 1, 1, 12, 0),
            end_time=datetime.datetime(2024, 1, 1, 14, 0),
            organizer=self.user1,
            place="Test Place"
        )

    def test_message_creation(self):
        """Test the creation of a MessageModel instance."""
        message = MessageModel.objects.create(
            thread=self.thread,
            sender_user=self.user1,
            receiver_user=self.user2,
            body="Hello, this is a test message",
            event=self.event
        )
        self.assertEqual(message.thread, self.thread)
        self.assertEqual(message.sender_user, self.user1)
        self.assertEqual(message.receiver_user, self.user2)
        self.assertEqual(message.body, "Hello, this is a test message")
        self.assertEqual(message.event, self.event)
        self.assertFalse(message.is_read)
        self.assertEqual(str(message), f"{self.user1} to {self.user2}")

    def test_message_creation_without_event(self):
        message = MessageModel.objects.create(
            thread=self.thread,
            sender_user=self.user1,
            receiver_user=self.user2,
            body="Hello, this is another test message"
        )
        self.assertIsNone(message.event)
