from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.db.models import Q, Count
from django.http import JsonResponse
from .models import Song, Artist, Album, Playlist, Favorite, PlayHistory

def home(request):
    recent_songs = Song.objects.all()[:12]
    popular_songs = Song.objects.order_by('-plays')[:12]
    artists = Artist.objects.all()[:8]
    albums = Album.objects.all()[:8]
    
    context = {
        'recent_songs': recent_songs,
        'popular_songs': popular_songs,
        'artists': artists,
        'albums': albums,
    }
    return render(request, 'music/home.html', context)

def search(request):
    query = request.GET.get('q', '')
    songs = Song.objects.filter(
        Q(title__icontains=query) | Q(artist__name__icontains=query)
    )[:20]
    artists = Artist.objects.filter(name__icontains=query)[:10]
    albums = Album.objects.filter(title__icontains=query)[:10]
    
    context = {
        'query': query,
        'songs': songs,
        'artists': artists,
        'albums': albums,
    }
    return render(request, 'music/search.html', context)

def artist_detail(request, pk):
    artist = get_object_or_404(Artist, pk=pk)
    songs = artist.songs.all()
    albums = artist.albums.all()
    
    context = {
        'artist': artist,
        'songs': songs,
        'albums': albums,
    }
    return render(request, 'music/artist_detail.html', context)

def album_detail(request, pk):
    album = get_object_or_404(Album, pk=pk)
    songs = album.songs.all()
    
    context = {
        'album': album,
        'songs': songs,
    }
    return render(request, 'music/album_detail.html', context)

@login_required
def my_playlists(request):
    playlists = request.user.playlists.all()
    return render(request, 'music/playlists.html', {'playlists': playlists})

@login_required
def playlist_detail(request, pk):
    playlist = get_object_or_404(Playlist, pk=pk)
    if playlist.user != request.user and not playlist.is_public:
        return redirect('home')
    
    return render(request, 'music/playlist_detail.html', {'playlist': playlist})

@login_required
def create_playlist(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        is_public = request.POST.get('is_public') == 'on'
        
        playlist = Playlist.objects.create(
            name=name,
            user=request.user,
            is_public=is_public
        )
        return redirect('playlist_detail', pk=playlist.pk)
    
    return render(request, 'music/create_playlist.html')

@login_required
def add_to_playlist(request, song_pk):
    if request.method == 'POST':
        song = get_object_or_404(Song, pk=song_pk)
        playlist_pk = request.POST.get('playlist_id')
        playlist = get_object_or_404(Playlist, pk=playlist_pk, user=request.user)
        playlist.songs.add(song)
        return JsonResponse({'status': 'success'})
    
    playlists = request.user.playlists.all()
    return render(request, 'music/add_to_playlist.html', {'playlists': playlists})

@login_required
def toggle_favorite(request, song_pk):
    song = get_object_or_404(Song, pk=song_pk)
    favorite, created = Favorite.objects.get_or_create(user=request.user, song=song)
    
    if not created:
        favorite.delete()
        return JsonResponse({'status': 'removed'})
    
    return JsonResponse({'status': 'added'})

@login_required
def favorites(request):
    favorite_songs = Song.objects.filter(favorited_by__user=request.user)
    return render(request, 'music/favorites.html', {'songs': favorite_songs})

@login_required
def play_song(request, song_pk):
    song = get_object_or_404(Song, pk=song_pk)
    song.plays += 1
    song.save()
    
    PlayHistory.objects.create(user=request.user, song=song)
    return JsonResponse({'status': 'success'})

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})