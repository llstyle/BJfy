from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import datetime

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
    duration = models.DurationField(blank=True, null=True)
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
    
    def get_stream_url(self):
        """Возвращает URL для стриминга с поддержкой Range requests"""
        from django.urls import reverse
        return reverse('stream_audio', kwargs={'song_pk': self.pk})
    
    def get_duration_display(self):
        """Форматирует длительность в читаемый вид (3:45 или 1:23:45)"""
        if not self.duration:
            return "0:00"
        
        total_seconds = int(self.duration.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes}:{seconds:02d}"

    def save(self, *args, **kwargs):
        # First save to ensure file is stored and has a filesystem path
        is_new = self.pk is None
        super().save(*args, **kwargs)
        # If duration not set, try to calculate from audio file
        if not self.duration and self.audio_file:
            try:
                from mutagen import File as MutagenFile
                audio = MutagenFile(self.audio_file.path)
                length = getattr(getattr(audio, 'info', None), 'length', None)
                if length:
                    self.duration = datetime.timedelta(seconds=int(length))
                    # avoid recursion depth; update only the duration field
                    super(Song, self).save(update_fields=['duration'])
            except Exception:
                # silently ignore if mutagen fails; admin can edit later
                pass
    class Meta:
        ordering = ['-created_at']

class Playlist(models.Model):
    name = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='playlists')
    songs = models.ManyToManyField(Song, related_name='playlists', blank=True)
    cover = models.ImageField(upload_to='playlists/', blank=True, null=True)
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
