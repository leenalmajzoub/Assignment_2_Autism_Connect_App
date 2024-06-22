from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Event(models.Model):
	"""Model representing an event."""

	title = models.CharField(max_length=200, default="title")
	description = models.TextField(blank=True)
	start_time = models.DateTimeField(default=timezone.now)
	end_time = models.DateTimeField(default=timezone.now)
	organizer = models.ForeignKey(User, on_delete=models.CASCADE)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	attendees_allowed = models.IntegerField(default=5)
	attendees = models.ManyToManyField(User, related_name='event_attendees', blank=True)
	image = models.ImageField(upload_to='uploads/event_photos', default='uploads/event_photos/event.jpg')
	created_on = models.DateTimeField(default=timezone.now)
	tags = models.ManyToManyField('EventTag', blank=True)
	place = models.CharField(max_length=200, default="place")
    
	def __str__(self):
		"""Returns the title of the event when the object is called"""
		return self.title
    
	def number_of_attendees(self):
		"""Returns the number of attendees for the event."""
		return self.attendees.count()

	def can_join(self):
		"""Checks if more attendees can join the event."""
		return self.number_of_attendees() < self.attendees_allowed

	def create_tags(self):
		"""Creates and adds tags to the event based on the description."""
		for word in self.description.split():
			if word.startswith('#'):
				tag_name = word[1:]
				tag, created = EventTag.objects.get_or_create(name=tag_name)
				self.tags.add(tag)

	class Meta:
		ordering = ['start_time']

class EventTag(models.Model):
	"""Model representing a tag for events."""

	name = models.CharField(max_length=255)
    
	def __str__(self):
		"""Returns the name of the tag when the object is called"""
		return self.name

class News(models.Model):
	"""Model representing a news article."""

	title = models.TextField(blank=True, null=True)
	body = models.TextField(blank=True, null=True)
	image = models.ImageField(upload_to='uploads/news_photos', default='uploads/news_photos/news.png')
	created_on = models.DateTimeField(default=timezone.now)
	author = models.ForeignKey(User, on_delete=models.CASCADE)
	likes = models.ManyToManyField(User, blank=True, related_name='news_likes')
	dislikes = models.ManyToManyField(User, blank=True, related_name='news_dislikes')
	tags = models.ManyToManyField('NewsTag', blank=True)

	def __str__(self):
		"""Returns the title of the news when the object is called"""
		return self.title
     
	def create_tags(self):
		"""Creates and adds tags to the news article based on the body."""
		
		for word in self.body.split():
			if word.startswith('#'):
				tag_name = word[1:]
				tag, created = NewsTag.objects.get_or_create(name=tag_name)
				self.tags.add(tag)

	class Meta:
		ordering = ['-created_on']

class NewsTag(models.Model):
	"""Model representing a tag for news articles."""

	name = models.CharField(max_length=255)

	def __str__(self):
		"""Returns the name of the tag when the object is called"""
		return self.name

class NewsComment(models.Model):
	"""Model representing a comment on a news article."""

	comment = models.TextField()
	created_on = models.DateTimeField(default=timezone.now)
	author = models.ForeignKey(User, on_delete=models.CASCADE)
	news = models.ForeignKey('News', on_delete=models.CASCADE)
	likes = models.ManyToManyField(User, blank=True, related_name='newscomment_likes')
	dislikes = models.ManyToManyField(User, blank=True, related_name='newscomment_dislikes')
	parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='+')
	tags = models.ManyToManyField('NewsTag', blank=True)

	def __str__(self):
		"""Returns the first 20 charachters of the comment when the object is called"""
		return self.comment[:20]
	
	class Meta:
		ordering = ['-created_on']

	def create_tags(self):
		"""Creates and adds tags to the comment based on the comment text."""
		
		for word in self.comment.split():
			if word.startswith('#'):
				tag_name = word[1:]
				tag, created = NewsTag.objects.get_or_create(name=tag_name)
				self.tags.add(tag)

	@property
	def children(self):
		"""Returns the child comments of this comment."""
		
		return NewsComment.objects.filter(parent=self).order_by('-created_on').all()

	@property
	def is_parent(self):
		"""Checks if this comment is a parent comment."""
		
		return self.parent is None

class Post(models.Model):
	"""Model representing a post."""

	shared_body = models.TextField(blank=True, null=True)
	body = models.TextField()
	image = models.ManyToManyField('Image', blank=True)
	created_on = models.DateTimeField(default=timezone.now)
	shared_on = models.DateTimeField(blank=True, null=True)
	author = models.ForeignKey(User, on_delete=models.CASCADE)
	shared_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='+')
	likes = models.ManyToManyField(User, blank=True, related_name='likes')
	dislikes = models.ManyToManyField(User, blank=True, related_name='dislikes')
	tags = models.ManyToManyField('Tag', blank=True)

	def __str__(self):
		"""Returns the first 20 characters of the body of the post when the object is called"""
		return self.body[:20]

	def create_tags(self):
		"""Creates and adds tags to the post based on the body."""
		
		for word in self.body.split():
			if word.startswith('#'):
				tag_name = word[1:]
				tag, created = Tag.objects.get_or_create(name=tag_name)
				self.tags.add(tag)
		
		if self.shared_body:
			for word in self.shared_body.split():
				if word.startswith('#'):
					tag_name = word[1:]
					tag, created = Tag.objects.get_or_create(name=tag_name)
					self.tags.add(tag)

	class Meta:
		ordering = ['-created_on', '-shared_on']

class Comment(models.Model):
	"""Model representing a comment on a post."""

	comment = models.TextField()
	created_on = models.DateTimeField(default=timezone.now)
	author = models.ForeignKey(User, on_delete=models.CASCADE)
	post = models.ForeignKey('Post', on_delete=models.CASCADE)
	likes = models.ManyToManyField(User, blank=True, related_name='comment_likes')
	dislikes = models.ManyToManyField(User, blank=True, related_name='comment_dislikes')
	parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='+')
	tags = models.ManyToManyField('Tag', blank=True)

	def __str__(self):
		"""Returns the first 20 characters of the comment when the object is called"""
		return self.comment[:20]

	def create_tags(self):
		"""Creates and adds tags to the comment based on the comment text."""
		
		for word in self.comment.split():
			if word.startswith('#'):
				tag_name = word[1:]
				tag, created = Tag.objects.get_or_create(name=tag_name)
				self.tags.add(tag)

	@property
	def children(self):
		"""Returns the child comments of this comment."""
		
		return Comment.objects.filter(parent=self).order_by('-created_on').all()

	@property
	def is_parent(self):
		"""Checks if this comment is a parent comment."""
		
		return self.parent is None

class UserProfile(models.Model):
	"""Model representing a user's profile."""

	user = models.OneToOneField(User, primary_key=True, verbose_name='user', related_name='profile', on_delete=models.CASCADE)
	name = models.CharField(max_length=30, blank=True, null=True)
	bio = models.TextField(max_length=500, blank=True, null=True)
	birth_date = models.DateField(null=True, blank=True)
	location = models.CharField(max_length=100, blank=True, null=True)
	picture = models.ImageField(upload_to='uploads/profile_pictures', default='uploads/profile_pictures/default.png', blank=True)
	followers = models.ManyToManyField(User, blank=True, related_name='followers')
	
	def __str__(self):
		"""Returns the user of the userprofile when the object is called"""
		return self.user.username
    
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Creates a user profile when a new user is created."""
    
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Saves the user profile when the user is saved."""
    
    instance.profile.save()

class Notification(models.Model):
	"""Model representing a notification."""

	# 1 = Like, 2 = Comment, 3 = Follow, 4 = DM
	notification_type = models.IntegerField()
	to_user = models.ForeignKey(User, related_name='notification_to', on_delete=models.CASCADE, null=True)
	from_user = models.ForeignKey(User, related_name='notification_from', on_delete=models.CASCADE, null=True)
	post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='post_notification', blank=True, null=True)
	comment = models.ForeignKey('Comment', on_delete=models.CASCADE, related_name='comment_notification', blank=True, null=True)
	thread = models.ForeignKey('ThreadModel', on_delete=models.CASCADE, related_name='thread_notification', blank=True, null=True)
	date = models.DateTimeField(default=timezone.now)
	user_has_seen = models.BooleanField(default=False)

	def __str__(self):
		if self.notification_type == 1:
			return f"{self.from_user} liked {self.to_user} post"
		elif self.notification_type == 2:
			return f"{self.from_user} commented {self.to_user} post"
		elif self.notification_type == 3:
			return f"{self.from_user} followed {self.to_user}"
		elif self.notification_type == 4:
			return f"{self.from_user} messaged {self.to_user}"

class ThreadModel(models.Model):
	"""Model representing a message thread."""

	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='threads')
	receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_threads')

	def __str__(self):
		return f"{self.user} to {self.receiver}"	

class MessageModel(models.Model):
	"""Model representing a message."""

	thread = models.ForeignKey(ThreadModel, related_name='messages', on_delete=models.CASCADE, blank=True, null=True)
	sender_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
	receiver_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
	body = models.CharField(max_length=1000, blank=True, null=True)
	image = models.ImageField(upload_to='uploads/message_photos', blank=True, null=True)
	date = models.DateTimeField(default=timezone.now)
	is_read = models.BooleanField(default=False)
	event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='event_message', blank=True, null=True)

	def __str__(self):
		return f"{self.sender_user} to {self.receiver_user}"	

class Image(models.Model):
    """Model representing an image."""
    
    image = models.ImageField(upload_to='uploads/post_photos', blank=True, null=True)

class Tag(models.Model):
	"""Model representing a tag."""

	name = models.CharField(max_length=255)

	def __str__(self):
		return self.name
