from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Artist(models.Model):
    name = models.CharField(max_length=200)
    bio = models.TextField(blank=True)
    image = models.ImageField(upload_to='artists/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class Album(models.Model):
    title = models.CharField(max_length=200)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='albums')
    cover = models.ImageField(upload_to='albums/', blank=True, null=True)
    release_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.artist.name}"

    class Meta:
        ordering = ['-release_date']

class Song(models.Model):
    title = models.CharField(max_length=200)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='songs')
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name='songs', null=True, blank=True)
    audio_file = models.FileField(upload_to='songs/')
    cover = models.ImageField(upload_to='songs/covers/', blank=True, null=True)
    duration = models.DurationField()
    plays = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.artist.name}"
    def get_cover(self):
        """Возвращает обложку трека или альбома"""
        if self.cover:
            return self.cover.url
        elif self.album and self.album.cover:
            return self.album.cover.url
        return '/static/placeholder.png'
    class Meta:
        ordering = ['-created_at']

class Playlist(models.Model):
    name = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='playlists')
    songs = models.ManyToManyField(Song, related_name='playlists', blank=True)
    cover = models.ImageField(upload_to='playlists/', blank=True, null=True)
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.user.username}"

    class Meta:
        ordering = ['-created_at']

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'song']
        ordering = ['-created_at']

class PlayHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='play_history')
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    played_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-played_at']
