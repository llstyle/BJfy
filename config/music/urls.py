from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search, name='search'),
    path('artist/<int:pk>/', views.artist_detail, name='artist_detail'),
    path('album/<int:pk>/', views.album_detail, name='album_detail'),
    path('playlists/', views.my_playlists, name='my_playlists'),
    path('playlist/<int:pk>/', views.playlist_detail, name='playlist_detail'),
    path('playlist/create/', views.create_playlist, name='create_playlist'),
    path('song/<int:song_pk>/add-to-playlist/', views.add_to_playlist, name='add_to_playlist'),
    path('song/<int:song_pk>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('song/<int:song_pk>/play/', views.play_song, name='play_song'),
    path('song/<int:song_pk>/stream/', views.stream_audio, name='stream_audio'),
    path('playlist/<int:playlist_pk>/remove-song/<int:song_pk>/', views.remove_song_from_playlist, name='remove_song_from_playlist'),
    path('playlist/<int:pk>/upload-cover/', views.upload_playlist_cover, name='upload_playlist_cover'),
    path('favorites/', views.favorites, name='favorites'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    path('playlist/<int:pk>/edit/', views.edit_playlist, name='edit_playlist'),
    path('api/random-song/', views.random_song, name='random_song'),
    path('api/similar-songs/<int:song_id>/', views.similar_songs, name='similar_songs'),
]