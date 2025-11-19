from django.contrib import admin
from .models import Artist, Album, Song, Playlist, Favorite, PlayHistory

@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']

@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ['title', 'artist', 'release_date']
    list_filter = ['release_date']
    search_fields = ['title', 'artist__name']

@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    list_display = ['title', 'artist', 'album', 'plays', 'created_at']
    list_filter = ['created_at']
    search_fields = ['title', 'artist__name']

@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'user__username']

admin.site.register(Favorite)
admin.site.register(PlayHistory)