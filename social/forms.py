from django import forms
from .models import Post, Comment, MessageModel, Event, News, NewsComment

class EventForm(forms.ModelForm):
    """Form for creating and editing events."""

    title = forms.CharField(max_length=200)
    description = forms.CharField(
        label='Description',
        widget=forms.Textarea(attrs={
            'rows': '3',
            'placeholder': 'Describe your event...'
        })
    )

    image = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'multiple': False
        })
    )
    
    start_time = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))
    end_time = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))
    attendees_allowed = forms.IntegerField(min_value=1)
    place = forms.CharField(max_length=200)

    class Meta:
        model = Event
        fields = ['title', 'description', 'start_time', 'end_time', 'attendees_allowed', 'image', 'place']


class NewsForm(forms.ModelForm):
    """Form for creating and editing news articles."""

    title = forms.CharField(max_length=200)
    
    body = forms.CharField(
        label='Body',
        widget=forms.Textarea(attrs={
            'rows': '3',
            'placeholder': 'Say Something...'
        })
    )

    image = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'multiple': False
        })
    )

    class Meta:
        model = News
        fields = ['title', 'image', 'body']


class ShareNewsForm(forms.Form):
    """Form for sharing news articles."""

    body = forms.CharField(label='', max_length=1000)


class PostForm(forms.ModelForm):
    """Form for creating and editing posts."""

    body = forms.CharField(
        label='',
        widget=forms.Textarea(attrs={
            'rows': '3',
            'placeholder': 'Say Something...'
        })
    )

    image = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'multiple': False
        })
    )

    class Meta:
        model = Post
        fields = ['body']


class NewsCommentForm(forms.ModelForm):
    """Form for adding comments to news articles."""

    comment = forms.CharField(
        label='',
        widget=forms.Textarea(attrs={
            'rows': '3',
            'placeholder': 'Say Something...'
        })
    )

    class Meta:
        model = NewsComment
        fields = ['comment']


class CommentForm(forms.ModelForm):
    """Form for adding comments to posts."""

    comment = forms.CharField(
        label='',
        widget=forms.Textarea(attrs={
            'rows': '3',
            'placeholder': 'Say Something...'
        })
    )

    class Meta:
        model = Comment
        fields = ['comment']


class ThreadForm(forms.Form):
    """Form for initiating a new message thread."""

    username = forms.CharField(label='', max_length=100)


class MessageForm(forms.ModelForm):
    """Form for sending messages."""

    body = forms.CharField(label='', max_length=1000)
    image = forms.ImageField(required=False)

    class Meta:
        model = MessageModel
        fields = ['body', 'image']


class ShareForm(forms.Form):
    """Form for sharing posts."""

    body = forms.CharField(
        label='',
        widget=forms.Textarea(attrs={
            'rows': '3',
            'placeholder': 'Say Something...'
        })
    )


class ExploreForm(forms.Form):
    """Form for exploring content based on tags."""

    query = forms.CharField(
        label='',
        widget=forms.TextInput(attrs={
            'placeholder': 'Explore tags'
        })
    )


class ShareEventForm(forms.Form):
    """Form for sharing events with a specific user."""

    recipient_username = forms.CharField(label='Recipient Username', max_length=150)
