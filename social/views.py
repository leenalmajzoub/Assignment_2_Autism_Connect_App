from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from itertools import chain
from django.utils import timezone
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.views import View
from .models import Post, Comment, UserProfile, Notification, ThreadModel, MessageModel, Image, Tag, Event, News, NewsComment, NewsTag, EventTag
from .forms import PostForm, CommentForm, ThreadForm, MessageForm, ShareForm, ExploreForm, EventForm, NewsForm, ShareNewsForm, NewsCommentForm, ShareEventForm
from django.views.generic.edit import UpdateView, DeleteView

# Events Related
class EventListView(LoginRequiredMixin, View):
    '''List all events'''

    def get(self, request, *args, **kwargs):
        events = Event.objects.all()  # Get all events from the database
        form = EventForm()  # Initialize an empty event form
        share_form = ShareForm()  # Initialize an empty share form

        context = {
            'event_list': events,
            'shareform': share_form,
            'form': form,
        }

        # Render the event list template with the context
        return render(request, 'social/event_list.html', context)

class EventDetailView(LoginRequiredMixin, View):
    '''Show event details and handle sharing the event'''

    def get(self, request, pk, *args, **kwargs):
        event = get_object_or_404(Event, pk=pk)  # Get event by primary key or return 404
        share_form = ShareEventForm()  # Initialize an empty share event form
        context = {
            'event': event,
            'share_form': share_form
        }

        # Render the event detail template with the context
        return render(request, 'social/event_detail.html', context)

    def post(self, request, pk, *args, **kwargs):
        share_form = ShareEventForm(request.POST)  # Populate form with POST data
        
        if share_form.is_valid():
            recipient_username = share_form.cleaned_data['recipient_username']
            try:
                recipient = User.objects.get(username=recipient_username)  # Get user by username
                messages.success(request, f"Event shared with {recipient_username} successfully.")
            except User.DoesNotExist:
                messages.error(request, f"User '{recipient_username}' not found.")
        
        # Redirect to the event detail page
        return redirect('event-detail', pk=pk)

class ShareEventView(LoginRequiredMixin, View):
    '''Sharing an event from a POST'''

    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)  # Get event by primary key or return 404
        share_form = ShareEventForm(request.POST)  # Populate form with POST data
        
        if share_form.is_valid():
            recipient_username = share_form.cleaned_data['recipient_username']
            try:
                recipient = User.objects.get(username=recipient_username)  # Get user by username
                
                # Create or get thread between users
                thread, created = ThreadModel.objects.get_or_create(
                    user=request.user,
                    receiver=recipient
                )
                
                # Create an event message in the thread
                event_message = MessageModel.objects.create(
                    thread=thread,
                    sender_user=request.user,
                    receiver_user=recipient,
                    event=event
                )
                
                messages.success(request, f"Event shared with {recipient_username} successfully.")
            except User.DoesNotExist:
                messages.error(request, f"User '{recipient_username}' not found.")
        else:
            # Handle ShareEventForm errors
            for field, errors in share_form.errors.items():
                for error in errors:
                    messages.error(request, f"Error in {field}: {error}")
        
        # Redirect to the event detail page
        return redirect('event-detail', pk=pk)

class JoinEvent(LoginRequiredMixin, View):
    '''Joining an event'''

    def post(self, request, pk, *args, **kwargs):
        event = Event.objects.get(pk=pk)  # Get event by primary key

        not_joined = True

        for attendee in event.attendees.all():
            if attendee == request.user:
                not_joined = False
                break

        # Add user to event attendees if not already joined and space is available
        if not_joined and event.number_of_attendees() < event.attendees_allowed:
            event.attendees.add(request.user)

        # Redirect to the next page specified in POST data or root
        next = request.POST.get('next', '/')
        return HttpResponseRedirect(next)

class UnjoinEvent(LoginRequiredMixin, UserPassesTestMixin, View):
    '''Unjoining an event'''

    def post(self, request, pk, *args, **kwargs):
        event = Event.objects.get(pk=pk)  # Get event by primary key

        joined = False

        for attendee in event.attendees.all():
            if attendee == request.user:
                joined = True
                break

        # Remove user from event attendees if they had joined
        if joined:
            event.attendees.remove(request.user)

        # Redirect to the next page specified in POST data or root
        next = request.POST.get('next', '/')
        return HttpResponseRedirect(next)
    
    def test_func(self):
        event = get_object_or_404(Event, pk=self.kwargs['pk'])
        return self.request.user in event.attendees.all()

class ListAttendees(LoginRequiredMixin, View):
    '''List all attendees of an event'''
    def get(self, request, pk, *args, **kwargs):
        event = Event.objects.get(pk=pk)  # Get event by primary key
        attendees = event.attendees.all()  # Get all attendees of the event

        context = {
            'event': event,
            'attendees': attendees,
        }

        # Render the attendees list template with the context
        return render(request, 'social/attendees_list.html', context)

class RemoveAttendee(LoginRequiredMixin, View):
    '''Remove an attendee from an event'''

    def post(self, request, pk, *args, **kwargs):
        event = Event.objects.get(pk=pk)  # Get event by primary key
        attendee_pk = request.POST.get('attendee_pk')  # Get attendee primary key from POST data
        
        # Remove the attendee from the event
        event.attendees.remove(attendee_pk)

        # Redirect to the next page specified in POST data or root
        next = request.POST.get('next', '/')
        return HttpResponseRedirect(next)

class EventEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    '''Edit event'''

    model = Event
    fields = ['title', 'description', 'start_time', 'end_time', 'attendees_allowed', 'image', 'place']
    template_name = 'social/event_edit.html'

    def get_success_url(self):
        pk = self.kwargs['pk']
        # Redirect to the event detail page after successful update
        return reverse_lazy('event-detail', kwargs={'pk': pk})

    def test_func(self):
        event = self.get_object()
        # Ensure that the current user is the organizer of the event
        return self.request.user == event.organizer

class EventDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    '''Delete an event'''

    model = Event
    template_name = 'social/event_delete.html'
    success_url = reverse_lazy('post-list')  # Redirect to post list page after successful deletion

    def test_func(self):
        event = self.get_object()
        # Ensure that the current user is the organizer of the event
        return self.request.user == event.organizer

# News Related
class NewsListView(LoginRequiredMixin, View):
    """List all news items."""
    
    def get(self, request, *args, **kwargs):
        logged_in_user = request.user
        news = News.objects.all()

        context = {
            'news_list': news,
        }

        return render(request, 'social/news_list.html', context)

class NewsDetailView(LoginRequiredMixin, View):
    """Display the details of a news item."""
    
    def get(self, request, pk, *args, **kwargs):
        news = get_object_or_404(News, pk=pk)
        form = NewsCommentForm()

        comments = NewsComment.objects.filter(news=news)

        context = {
            'news': news,
            'form': form,
            'comments': comments,
        }

        return render(request, 'social/news_detail.html', context)
    
    def post(self, request, pk, *args, **kwargs):
        """
        Handle POST request to add a comment to the news item.
        
        Args:
            request: The HTTP request object.
            pk: Primary key of the news item.
            *args: Additional arguments.
            **kwargs: Additional keyword arguments.
        
        Returns:
            HttpResponse: Rendered template with updated news details and comments.
        """
        news = News.objects.get(pk=pk)
        form = NewsCommentForm(request.POST)

        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.author = request.user
            new_comment.news = news
            new_comment.save()

            new_comment.create_tags()

        comments = NewsComment.objects.filter(news=news)

        context = {
            'news': news,
            'form': form,
            'comments': comments,
        }

        return render(request, 'social/news_detail.html', context)

class NewsEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Edit an existing news item."""

    model = News
    fields = ['title', 'body']
    template_name = 'social/news_edit.html'

    def get_success_url(self):
        pk = self.kwargs['pk']
        return reverse_lazy('news-detail', kwargs={'pk': pk})

    def test_func(self):
        news = self.get_object()
        return self.request.user == news.author

class NewsDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete an existing news item."""

    model = News
    template_name = 'social/news_delete.html'
    success_url = reverse_lazy('post-list')

    def test_func(self):
        
        news = self.get_object()
        return self.request.user == news.author

class NewsCommentReplyView(LoginRequiredMixin, View):
    """Reply to news comments."""
    
    def post(self, request, news_pk, pk, *args, **kwargs):
        
        news = News.objects.get(pk=news_pk)
        parent_comment = NewsComment.objects.get(pk=pk)
        form = NewsCommentForm(request.POST)

        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.author = request.user
            new_comment.news = news
            new_comment.parent = parent_comment
            new_comment.save()

        return redirect('news-detail', pk=news_pk)

class NewsCommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete a news comment."""

    model = NewsComment
    template_name = 'social/newscomment_delete.html'

    def get_success_url(self):
        
        pk = self.kwargs['news_pk']
        return reverse_lazy('news-detail', kwargs={'pk': pk})

    def test_func(self):
        
        news = self.get_object()
        return self.request.user == news.author

class AddNewsCommentLike(LoginRequiredMixin, View):
    """Add or remove a like on a news comment."""
    
    def post(self, request, pk, *args, **kwargs):
        
        comment = NewsComment.objects.get(pk=pk)

        is_dislike = False

        for dislike in comment.dislikes.all():
            if dislike == request.user:
                is_dislike = True
                break

        if is_dislike:
            comment.dislikes.remove(request.user)

        is_like = False

        for like in comment.likes.all():
            if like == request.user:
                is_like = True
                break

        if not is_like:
            comment.likes.add(request.user)

        if is_like:
            comment.likes.remove(request.user)

        next = request.POST.get('next', '/')
        return HttpResponseRedirect(next)

class AddNewsCommentDislike(LoginRequiredMixin, View):
    """Add or remove a dislike on a news comment."""
    
    def post(self, request, pk, *args, **kwargs):
        
        comment = NewsComment.objects.get(pk=pk)

        is_like = False

        for like in comment.likes.all():
            if like == request.user:
                is_like = True
                break

        if is_like:
            comment.likes.remove(request.user)

        is_dislike = False

        for dislike in comment.dislikes.all():
            if dislike == request.user:
                is_dislike = True
                break

        if not is_dislike:
            comment.dislikes.add(request.user)

        if is_dislike:
            comment.dislikes.remove(request.user)

        next = request.POST.get('next', '/')
        return HttpResponseRedirect(next)

# Post Related
class PostListView(LoginRequiredMixin, View):
    """
    Display a list of posts, events, and news for the logged-in user. 
    Create new posts, events, and news through POST requests.
    """

    def get(self, request, *args, **kwargs):
        
        logged_in_user = request.user
        posts = Post.objects.filter(author__profile__followers__in=[logged_in_user.id])
        events = Event.objects.all()
        postform = PostForm()
        share_form = ShareForm()
        eventform = EventForm()
        news = News.objects.all()
        share_news_form = ShareNewsForm()
        newsform = NewsForm()

        context = {
            'event_list': events,
            'post_list': posts,
            'shareform': share_form,
            'eventform': eventform,
            'postform': postform,
            'news_list': news,
            'share_news_form': share_news_form,
            'newsform': newsform,
        }

        return render(request, 'social/post_list.html', context)

    def post(self, request, *args, **kwargs):
        
        logged_in_user = request.user
        posts = Post.objects.filter(author__profile__followers__in=[logged_in_user.id])
        events = Event.objects.filter(organizer=logged_in_user.id)
        postform = PostForm()
        eventform = EventForm()
        files = request.FILES.getlist('image')
        share_form = ShareForm()  # Assuming ShareForm is defined somewhere
        news = News.objects.all()
        newsform = NewsForm()

        if request.method == 'POST':
            if request.POST.get('form_type') == 'post':
                postform = PostForm(request.POST, request.FILES)
                if postform.is_valid():
                    new_post = postform.save(commit=False)
                    new_post.author = request.user
                    new_post.save()
                    new_post.create_tags()
                    for f in files:
                        img = Image(image=f)
                        img.save()
                        new_post.image.add(img)

            elif request.POST.get('form_type') == 'event':
                eventform = EventForm(request.POST, request.FILES)
                if eventform.is_valid():
                    new_event = eventform.save(commit=False)
                    new_event.organizer = request.user
                    new_event.save()
                    new_event.create_tags()
                    for f in files:
                        img = Image(image=f)
                        img.save()
                        new_event.image.add(img)

            elif request.POST.get('form_type') == 'news':
                newsform = NewsForm(request.POST, request.FILES)
                if newsform.is_valid():
                    new_news = newsform.save(commit=False)
                    new_news.author = request.user
                    new_news.save()
                    new_news.create_tags()
                    for f in files:
                        img = Image(image=f)
                        img.save()
                        new_news.image.add(img)

        context = {
            'post_list': posts,
            'event_list': events,
            'postform': postform,
            'eventform': eventform,
            'shareform': share_form,
            'news_list': news,
            'newsform': newsform,
        }
        return render(request, 'social/post_list.html', context)

class PostDetailView(LoginRequiredMixin, View):
    """
    Display the details of a post and handle comments.
    Adding comments through POST requests.
    """

    def get(self, request, pk, *args, **kwargs):
        
        post = Post.objects.get(pk=pk)
        form = CommentForm()
        comments = Comment.objects.filter(post=post)

        context = {
            'post': post,
            'form': form,
            'comments': comments,
        }

        return render(request, 'social/post_detail.html', context)

    def post(self, request, pk, *args, **kwargs):
        
        post = Post.objects.get(pk=pk)
        form = CommentForm(request.POST)

        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.author = request.user
            new_comment.post = post
            new_comment.save()

            new_comment.create_tags()

        comments = Comment.objects.filter(post=post)

        notification = Notification.objects.create(notification_type=2, from_user=request.user, to_user=post.author, post=post)

        context = {
            'post': post,
            'form': form,
            'comments': comments,
        }

        return render(request, 'social/post_detail.html', context)

class CommentReplyView(LoginRequiredMixin, View):
    """Reply to comments on a post."""

    def post(self, request, post_pk, pk, *args, **kwargs):
        
        post = Post.objects.get(pk=post_pk)
        parent_comment = Comment.objects.get(pk=pk)
        form = CommentForm(request.POST)

        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.author = request.user
            new_comment.post = post
            new_comment.parent = parent_comment
            new_comment.save()

        notification = Notification.objects.create(notification_type=2, from_user=request.user, to_user=parent_comment.author, comment=new_comment)

        return redirect('post-detail', pk=post_pk)

class PostEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Edit an existing post."""

    model = Post
    fields = ['body']
    template_name = 'social/post_edit.html'

    def get_success_url(self):
        
        pk = self.kwargs['pk']
        return reverse_lazy('post-detail', kwargs={'pk': pk})

    def test_func(self):
       
        post = self.get_object()
        return self.request.user == post.author

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete an existing post."""

    model = Post
    template_name = 'social/post_delete.html'
    success_url = reverse_lazy('post-list')

    def test_func(self):
        
        post = self.get_object()
        return self.request.user == post.author

class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete an existing comment."""

    model = Comment
    template_name = 'social/comment_delete.html'

    def get_success_url(self):
        
        pk = self.kwargs['post_pk']
        return reverse_lazy('post-detail', kwargs={'pk': pk})

    def test_func(self):
       
        post = self.get_object()
        return self.request.user == post.author

class AddLike(LoginRequiredMixin, View):
    """Add or remove a like on a post"""

    def post(self, request, pk, *args, **kwargs):
       
        post = Post.objects.get(pk=pk)

        is_dislike = False

        for dislike in post.dislikes.all():
            if dislike == request.user:
                is_dislike = True
                break

        if is_dislike:
            post.dislikes.remove(request.user)

        is_like = False

        for like in post.likes.all():
            if like == request.user:
                is_like = True
                break

        if not is_like:
            post.likes.add(request.user)
            notification = Notification.objects.create(notification_type=1, from_user=request.user, to_user=post.author, post=post)

        if is_like:
            post.likes.remove(request.user)

        next = request.POST.get('next', '/')
        return HttpResponseRedirect(next)

class AddDislike(LoginRequiredMixin, View):
    """Add or remove a dislike on a post."""

    def post(self, request, pk, *args, **kwargs):
        
        post = Post.objects.get(pk=pk)

        is_like = False

        for like in post.likes.all():
            if like == request.user:
                is_like = True
                break

        if is_like:
            post.likes.remove(request.user)

        is_dislike = False

        for dislike in post.dislikes.all():
            if dislike == request.user:
                is_dislike = True
                break

        if not is_dislike:
            post.dislikes.add(request.user)

        if is_dislike:
            post.dislikes.remove(request.user)

        next = request.POST.get('next', '/')
        return HttpResponseRedirect(next)

class AddCommentLike(LoginRequiredMixin, View):
    """Add or remove a like on a comment."""

    def post(self, request, pk, *args, **kwargs):

        comment = Comment.objects.get(pk=pk)

        is_dislike = False

        for dislike in comment.dislikes.all():
            if dislike == request.user:
                is_dislike = True
                break

        if is_dislike:
            comment.dislikes.remove(request.user)

        is_like = False

        for like in comment.likes.all():
            if like == request.user:
                is_like = True
                break

        if not is_like:
            comment.likes.add(request.user)
            notification = Notification.objects.create(notification_type=1, from_user=request.user, to_user=comment.author, comment=comment)

        if is_like:
            comment.likes.remove(request.user)

        next = request.POST.get('next', '/')
        return HttpResponseRedirect(next)

class AddCommentDislike(LoginRequiredMixin, View):
    """Add or remove a dislike on a comment."""

    def post(self, request, pk, *args, **kwargs):
        
        comment = Comment.objects.get(pk=pk)

        is_like = False

        for like in comment.likes.all():
            if like == request.user:
                is_like = True
                break

        if is_like:
            comment.likes.remove(request.user)

        is_dislike = False

        for dislike in comment.dislikes.all():
            if dislike == request.user:
                is_dislike = True
                break

        if not is_dislike:
            comment.dislikes.add(request.user)

        if is_dislike:
            comment.dislikes.remove(request.user)

        next = request.POST.get('next', '/')
        return HttpResponseRedirect(next)

class SharedPostView(LoginRequiredMixin, View):
    """Share a post."""

    def post(self, request, pk, *args, **kwargs):
       
        original_post = Post.objects.get(pk=pk)
        form = ShareForm(request.POST)

        if form.is_valid():
            new_post = Post(
                shared_body=self.request.POST.get('body'),
                body=original_post.body,
                author=original_post.author,
                created_on=original_post.created_on,
                shared_user=request.user,
                shared_on=timezone.now(),
            )
            new_post.save()

            for img in original_post.image.all():
                new_post.image.add(img)

            new_post.save()

        return redirect('post-list')

class Explore(LoginRequiredMixin, View):
    """Explore posts, news, and events based on tags."""

    def get(self, request, *args, **kwargs):
        
        explore_form = ExploreForm()
        query = self.request.GET.get('query')
        active_form = self.request.GET.get('active_form', 'post')
        post_tag = Tag.objects.filter(name=query).first()
        news_tag = NewsTag.objects.filter(name=query).first()
        event_tag = EventTag.objects.filter(name=query).first()

        if post_tag:
            posts = Post.objects.filter(tags__in=[post_tag])
        else:
            posts = Post.objects.all()

        if news_tag:
            news = News.objects.filter(tags__in=[news_tag])
        else:
            news = News.objects.all()

        if event_tag:
            events = Event.objects.filter(tags__in=[event_tag])
        else:
            events = Event.objects.all()

        context = {
            'post_tag': post_tag,
            'posts': posts,
            'explore_form': explore_form,
            'news_tag': news_tag,
            'news': news,
            'event_tag': event_tag,
            'events': events,
            'active_form': active_form
        }

        return render(request, 'social/explore.html', context)

    def post(self, request, *args, **kwargs):
        
        if request.method == 'POST':
            form_type = request.POST.get('form_type')
            explore_form = ExploreForm(request.POST)
            if explore_form.is_valid():
                query = explore_form.cleaned_data['query']
                return redirect(f'/social/explore?query={query}&active_form={form_type}')
        return redirect('/social/explore')

# Profile Related
class ProfileView(LoginRequiredMixin, View):
    """Display a user's profile."""

    def get(self, request, pk, *args, **kwargs):
        profile = UserProfile.objects.get(pk=pk)
        user = profile.user
        posts = Post.objects.filter(author=user)

        followers = profile.followers.all()

        is_following = any(follower == request.user for follower in followers)
        number_of_followers = len(followers)

        context = {
            'user': user,
            'profile': profile,
            'posts': posts,
            'number_of_followers': number_of_followers,
            'is_following': is_following,
        }

        return render(request, 'social/profile.html', context)

class ProfileEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Edit a user's profile."""

    model = UserProfile
    fields = ['name', 'bio', 'birth_date', 'location', 'picture']
    template_name = 'social/profile_edit.html'

    def get_success_url(self):
        pk = self.kwargs['pk']
        return reverse_lazy('profile', kwargs={'pk': pk})

    def test_func(self):
        profile = self.get_object()
        return self.request.user == profile.user

class AddFollower(LoginRequiredMixin, View):
    """Add a follower to a user's profile."""

    def post(self, request, pk, *args, **kwargs):
        profile = UserProfile.objects.get(pk=pk)
        profile.followers.add(request.user)

        notification = Notification.objects.create(notification_type=3, from_user=request.user, to_user=profile.user)

        return redirect('profile', pk=profile.pk)

class RemoveFollower(LoginRequiredMixin, View):
    """Remove a follower from a user's profile."""

    def post(self, request, pk, *args, **kwargs):
        profile = UserProfile.objects.get(pk=pk)
        profile.followers.remove(request.user)

        return redirect('profile', pk=profile.pk)

class UserSearch(LoginRequiredMixin, View):
    """Search for users by username."""

    def get(self, request, *args, **kwargs):
        query = self.request.GET.get('query')
        profile_list = UserProfile.objects.filter(
            Q(user__username__icontains=query)
        )

        context = {
            'profile_list': profile_list,
        }

        return render(request, 'social/search.html', context)

class ListFollowers(LoginRequiredMixin, View):
    """List all followers of a user's profile."""

    def get(self, request, pk, *args, **kwargs):
        profile = UserProfile.objects.get(pk=pk)
        followers = profile.followers.all()

        context = {
            'profile': profile,
            'followers': followers,
        }

        return render(request, 'social/followers_list.html', context)

# Notifcations Related
class PostNotification(LoginRequiredMixin, View):
    """Marks a notification as seen and redirects to the post detail view."""

    def get(self, request, notification_pk, post_pk, *args, **kwargs):
        notification = Notification.objects.get(pk=notification_pk)
        post = Post.objects.get(pk=post_pk)

        notification.user_has_seen = True
        notification.save()

        return redirect('post-detail', pk=post_pk)

class FollowNotification(LoginRequiredMixin, View):
    """Marks a notification as seen and redirects to the profile view."""

    def get(self, request, notification_pk, profile_pk, *args, **kwargs):
        notification = Notification.objects.get(pk=notification_pk)
        profile = UserProfile.objects.get(pk=profile_pk)

        notification.user_has_seen = True
        notification.save()

        return redirect('profile', pk=profile_pk)

class ThreadNotification(LoginRequiredMixin, View):
    """Marks a notification as seen and redirects to the thread view."""

    def get(self, request, notification_pk, object_pk, *args, **kwargs):
        notification = Notification.objects.get(pk=notification_pk)
        thread = ThreadModel.objects.get(pk=object_pk)

        notification.user_has_seen = True
        notification.save()

        return redirect('thread', pk=object_pk)

class RemoveNotification(LoginRequiredMixin, View):
    """Marks a notification as seen and responds with success."""

    def delete(self, request, notification_pk, *args, **kwargs):
        notification = Notification.objects.get(pk=notification_pk)

        notification.user_has_seen = True
        notification.save()

        return HttpResponse('Success', content_type='text/plain')

# Messages Related
class ListThreads(LoginRequiredMixin, View):
    """List all threads involving the logged-in user."""

    def get(self, request, *args, **kwargs):
        threads = ThreadModel.objects.filter(Q(user=request.user) | Q(receiver=request.user))

        context = {
            'threads': threads
        }

        return render(request, 'social/inbox.html', context)

class CreateThread(LoginRequiredMixin, View):
    """Create a new thread between the logged-in user and another user."""

    def get(self, request, *args, **kwargs):
        form = ThreadForm()
        context = {'form': form}
        return render(request, 'social/create_thread.html', context)

    def post(self, request, *args, **kwargs):
        form = ThreadForm(request.POST)
        username = request.POST.get('username')

        receiver = get_object_or_404(User, username=username)

        if ThreadModel.objects.filter(Q(user=request.user, receiver=receiver) | Q(user=receiver, receiver=request.user)).exists():
            thread = ThreadModel.objects.filter(Q(user=request.user, receiver=receiver) | Q(user=receiver, receiver=request.user)).first()
            return redirect('thread', pk=thread.pk)

        if form.is_valid():
            event_id = request.POST.get('event_id')
            event = Event.objects.get(id=event_id) if event_id else None
            thread = ThreadModel.objects.create(user=request.user, receiver=receiver)
            if event:
                thread.events.add(event)
            thread.save()

            # Send notification
            Notification.objects.create(
                notification_type=4,
                from_user=request.user,
                to_user=receiver,
                thread=thread
            )

            return redirect('thread', pk=thread.pk)

        return redirect('create-thread')

class ThreadView(LoginRequiredMixin, View):
    """Display a specific thread and its messages."""

    def get(self, request, pk, *args, **kwargs):
        form = MessageForm()
        thread = ThreadModel.objects.get(pk=pk)
        
        message_list = MessageModel.objects.filter(thread=thread)
        
        context = {
            'thread': thread,
            'form': form,
            'message_list': message_list
        }

        return render(request, 'social/thread.html', context)

class CreateMessage(LoginRequiredMixin, View):
    """Create a new message in a specific thread."""
    
    def post(self, request, pk, *args, **kwargs):
        form = MessageForm(request.POST, request.FILES)
        thread = get_object_or_404(ThreadModel, pk=pk)

        # Determine the receiver
        if thread.receiver == request.user:
            receiver = thread.user
        else:
            receiver = thread.receiver

        if form.is_valid():
            message = form.save(commit=False)
            message.thread = thread
            message.sender_user = request.user
            message.receiver_user = receiver
            message.save()

            event_id = request.POST.get('event_id')
            event = Event.objects.get(id=event_id) if event_id else None

            if event:
                thread.events.add(event)
                thread.save()

            # Send notification
            Notification.objects.create(
                notification_type=4,
                from_user=request.user,
                to_user=receiver,
                thread=thread,
            )

        return redirect('thread', pk=pk)