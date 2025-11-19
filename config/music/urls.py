from django.urls import path
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
    path('favorites/', views.favorites, name='favorites'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', lambda r: logout(r) or redirect('home'), name='logout'),
]