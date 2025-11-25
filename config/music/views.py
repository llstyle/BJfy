from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.db.models import Q, Count
from django.db.models.functions import Lower
from django.http import JsonResponse, StreamingHttpResponse, HttpResponse, FileResponse
from .models import Song, Artist, Album, Playlist, Favorite, PlayHistory
from django.views.decorators.http import require_POST
from django.http import HttpResponseForbidden
import os
import mimetypes
import re

def home(request):
    # Новинки по дате релиза альбома (самые свежие релизы)
    recent_songs = Song.objects.select_related('album', 'artist').order_by('-album__release_date')[:3]
    popular_songs = Song.objects.order_by('-plays')[:3]  # 3 самых популярных
    artists = Artist.objects.annotate(song_count=Count('songs')).order_by('-song_count')[:8]  # Популярные артисты
    albums = Album.objects.order_by('-release_date')[:8]  # Новые альбомы
    
    # Рекомендации для авторизованных пользователей
    recommended_songs = []
    recommended_artists = []
    recommended_albums = []
    
    if request.user.is_authenticated:
        favorite_ids = list(Favorite.objects.filter(user=request.user).values_list('song_id', flat=True))
        
        # Получаем топ-3 артистов из истории прослушиваний пользователя
        top_artists = PlayHistory.objects.filter(user=request.user) \
            .values('song__artist') \
            .annotate(play_count=Count('id')) \
            .order_by('-play_count')[:3]
        
        if top_artists:
            artist_ids = [a['song__artist'] for a in top_artists]
            
            # Получаем ID треков, которые пользователь уже слушал
            listened_song_ids = set(PlayHistory.objects.filter(user=request.user).values_list('song_id', flat=True))
            
            # 1. Рекомендуем ТРЕКИ этих артистов, которые пользователь ещё не слушал
            recommended_songs = Song.objects.filter(
                artist_id__in=artist_ids
            ).exclude(
                id__in=listened_song_ids
            ).order_by('-plays')[:6]
            
            # Если рекомендаций мало, добавляем популярные треки
            if len(recommended_songs) < 6:
                additional = Song.objects.filter(
                    artist_id__in=artist_ids
                ).exclude(
                    id__in=list(listened_song_ids) + [s.id for s in recommended_songs]
                ).order_by('-created_at')[:6 - len(recommended_songs)]
                recommended_songs = list(recommended_songs) + list(additional)
            
            # 2. Рекомендуем ИСПОЛНИТЕЛЕЙ (похожих по жанру или популярных)
            # Исключаем артистов, которых пользователь уже слушает
            listened_artist_ids = set(PlayHistory.objects.filter(user=request.user).values_list('song__artist_id', flat=True))
            recommended_artists = Artist.objects.exclude(
                id__in=listened_artist_ids
            ).annotate(
                song_count=Count('songs')
            ).filter(
                song_count__gte=2  # Только артисты с 2+ треками
            ).order_by('-song_count')[:6]
            
            # 3. Рекомендуем АЛЬБОМЫ этих артистов или популярные альбомы
            recommended_albums = Album.objects.filter(
                artist_id__in=artist_ids
            ).exclude(
                id__in=PlayHistory.objects.filter(user=request.user).values_list('song__album_id', flat=True)
            ).order_by('-release_date')[:6]
            
            # Если альбомов мало, добавляем новые популярные альбомы
            if len(recommended_albums) < 6:
                additional_albums = Album.objects.exclude(
                    id__in=[a.id for a in recommended_albums]
                ).order_by('-release_date')[:6 - len(recommended_albums)]
                recommended_albums = list(recommended_albums) + list(additional_albums)
        
        # Если нет истории прослушиваний, используем любимые треки
        if not recommended_songs and favorite_ids:
            # Получаем артистов из любимых треков
            favorite_artists = Song.objects.filter(
                id__in=favorite_ids
            ).values_list('artist_id', flat=True).distinct()
            
            if favorite_artists:
                # Рекомендуем другие треки этих артистов
                recommended_songs = Song.objects.filter(
                    artist_id__in=favorite_artists
                ).exclude(
                    id__in=favorite_ids
                ).order_by('-plays')[:6]
                
                # Рекомендуем других исполнителей
                recommended_artists = Artist.objects.exclude(
                    id__in=favorite_artists
                ).annotate(
                    song_count=Count('songs')
                ).filter(song_count__gte=2).order_by('-song_count')[:6]
                
                # Рекомендуем альбомы
                recommended_albums = Album.objects.filter(
                    artist_id__in=favorite_artists
                ).order_by('-release_date')[:6]
    else:
        favorite_ids = []

    context = {
        'recent_songs': recent_songs,
        'popular_songs': popular_songs,
        'artists': artists,
        'albums': albums,
        'favorite_ids': favorite_ids,
        'recommended_songs': recommended_songs,
        'recommended_artists': recommended_artists,
        'recommended_albums': recommended_albums,
    }
    return render(request, 'music/home.html', context)

def search(request):
    query = request.GET.get('q', '').strip()
    
    # Debug: проверим что приходит
    print(f"DEBUG Search: query='{query}', repr={repr(query)}, len={len(query)}")
    
    if query:
        # Нормализуем query для регистро-независимого поиска кириллицы
        query_lower = query.lower()
        print(f"DEBUG query_lower='{query_lower}'")
        
        # Альтернативный подход: получаем все и фильтруем в Python
        # Это работает лучше для кириллицы в SQLite
        all_songs = Song.objects.select_related('artist', 'album').all()
        songs = [
            s for s in all_songs 
            if query_lower in s.title.lower() or query_lower in s.artist.name.lower()
        ][:20]
        
        all_artists = Artist.objects.all()
        artists = [
            a for a in all_artists
            if query_lower in a.name.lower()
        ][:10]
        
        all_albums = Album.objects.select_related('artist').all()
        albums = [
            a for a in all_albums
            if query_lower in a.title.lower() or query_lower in a.artist.name.lower()
        ][:10]
        
        # Debug results
        print(f"DEBUG Results: songs={len(songs)}, artists={len(artists)}, albums={len(albums)}")
        if albums:
            print(f"DEBUG Albums found: {[a.title for a in albums]}")
    else:
        songs = []
        artists = []
        albums = []
    
    if request.user.is_authenticated:
        favorite_ids = list(Favorite.objects.filter(user=request.user).values_list('song_id', flat=True))
    else:
        favorite_ids = []

    context = {
        'query': query,
        'songs': songs,
        'artists': artists,
        'albums': albums,
        'favorite_ids': favorite_ids,
    }
    return render(request, 'music/search.html', context)

def artist_detail(request, pk):
    artist = get_object_or_404(Artist, pk=pk)
    # Показываем только 10 самых популярных треков артиста
    songs = artist.songs.order_by('-plays')[:10]
    albums = artist.albums.all()
    
    if request.user.is_authenticated:
        favorite_ids = list(Favorite.objects.filter(user=request.user).values_list('song_id', flat=True))
    else:
        favorite_ids = []

    context = {
        'artist': artist,
        'songs': songs,
        'albums': albums,
        'favorite_ids': favorite_ids,
    }
    return render(request, 'music/artist_detail.html', context)

def album_detail(request, pk):
    album = get_object_or_404(Album, pk=pk)
    songs = album.songs.all()
    
    if request.user.is_authenticated:
        favorite_ids = list(Favorite.objects.filter(user=request.user).values_list('song_id', flat=True))
    else:
        favorite_ids = []

    context = {
        'album': album,
        'songs': songs,
        'favorite_ids': favorite_ids,
    }
    return render(request, 'music/album_detail.html', context)

@login_required
def my_playlists(request):
    playlists = request.user.playlists.all()
    return render(request, 'music/playlists.html', {'playlists': playlists})

@login_required
def playlist_detail(request, pk):
    playlist = get_object_or_404(Playlist, pk=pk)
    if playlist.user != request.user:
        return redirect('home')
    if request.user.is_authenticated:
        favorite_ids = list(Favorite.objects.filter(user=request.user).values_list('song_id', flat=True))
    else:
        favorite_ids = []

    return render(request, 'music/playlist_detail.html', {'playlist': playlist, 'favorite_ids': favorite_ids})


@login_required
@require_POST
def remove_song_from_playlist(request, playlist_pk, song_pk):
    playlist = get_object_or_404(Playlist, pk=playlist_pk)
    if playlist.user != request.user:
        return JsonResponse({'status': 'forbidden'}, status=403)
    song = get_object_or_404(Song, pk=song_pk)
    playlist.songs.remove(song)
    return JsonResponse({'status': 'removed'})


@login_required
@require_POST
def upload_playlist_cover(request, pk):
    playlist = get_object_or_404(Playlist, pk=pk)
    if playlist.user != request.user:
        return JsonResponse({'status': 'forbidden'}, status=403)
    cover = request.FILES.get('cover')
    if cover:
        playlist.cover = cover
        playlist.save()
        # Return URL of new cover
        return JsonResponse({'status': 'success', 'cover_url': playlist.cover.url})
    return JsonResponse({'status': 'no_file'}, status=400)


@login_required
def edit_playlist(request, pk):
    playlist = get_object_or_404(Playlist, pk=pk)
    if playlist.user != request.user:
        return redirect('home')

    if request.method == 'POST':
        name = request.POST.get('name')
        cover = request.FILES.get('cover')
        if name:
            playlist.name = name
        if cover:
            playlist.cover = cover
        playlist.save()
        return redirect('playlist_detail', pk=playlist.pk)

    return render(request, 'music/edit_playlist.html', {'playlist': playlist})

@login_required
def create_playlist(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        playlist = Playlist.objects.create(
            name=name,
            user=request.user
        )
        return redirect('playlist_detail', pk=playlist.pk)
    
    return render(request, 'music/create_playlist.html')

@login_required
def add_to_playlist(request, song_pk):
    # Load the song for both GET and POST so the template can show its info
    song = get_object_or_404(Song, pk=song_pk)
    if request.method == 'POST':
        playlist_pk = request.POST.get('playlist_id')
        playlist = get_object_or_404(Playlist, pk=playlist_pk, user=request.user)
        playlist.songs.add(song)
        return JsonResponse({'status': 'success'})

    playlists = request.user.playlists.all()
    return render(request, 'music/add_to_playlist.html', {'playlists': playlists, 'song': song})

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
    # favorites page shows only the user's favorites, so favorite_ids is simply the list of those ids
    favorite_ids = list(favorite_songs.values_list('pk', flat=True))
    return render(request, 'music/favorites.html', {'songs': favorite_songs, 'favorite_ids': favorite_ids})

def play_song(request, song_pk):
    song = get_object_or_404(Song, pk=song_pk)
    song.plays += 1
    song.save()
    
    if request.user.is_authenticated:
        PlayHistory.objects.create(user=request.user, song=song)
    return JsonResponse({'status': 'success'})

def random_song(request):
    """Return a random song from the database as JSON."""
    exclude_id = request.GET.get('exclude', None)
    qs = Song.objects.all()
    if exclude_id:
        qs = qs.exclude(pk=exclude_id)
    song = qs.order_by('?').first()
    if song:
        return JsonResponse({
            'id': song.pk,
            'url': song.get_stream_url(),
            'title': song.title,
            'artist': song.artist.name if song.artist else '',
            'cover': song.get_cover()
        })
    return JsonResponse({'error': 'No songs available'}, status=404)

def stream_audio(request, song_pk):
    """Stream audio file with support for HTTP Range requests (seeking)."""
    song = get_object_or_404(Song, pk=song_pk)
    
    if not song.audio_file:
        return HttpResponse('Audio file not found', status=404)
    
    # Get the file path
    file_path = song.audio_file.path
    file_size = os.path.getsize(file_path)
    
    # Get content type
    content_type, _ = mimetypes.guess_type(file_path)
    if not content_type:
        content_type = 'audio/mpeg'
    
    # Check if this is a range request
    range_header = request.META.get('HTTP_RANGE', '').strip()
    range_match = None
    
    if range_header:
        # Parse range header (e.g., "bytes=0-1023")
        import re
        range_match = re.search(r'bytes=(\d+)-(\d*)', range_header)
    
    if range_match:
        # Handle range request
        start = int(range_match.group(1))
        end = range_match.group(2)
        end = int(end) if end else file_size - 1
        end = min(end, file_size - 1)
        length = end - start + 1
        
        # Open file and seek to start position
        with open(file_path, 'rb') as f:
            f.seek(start)
            data = f.read(length)
        
        response = HttpResponse(data, status=206, content_type=content_type)
        response['Content-Length'] = str(length)
        response['Content-Range'] = f'bytes {start}-{end}/{file_size}'
        response['Accept-Ranges'] = 'bytes'
        return response
    else:
        # Regular request - return full file
        response = FileResponse(open(file_path, 'rb'), content_type=content_type)
        response['Content-Length'] = str(file_size)
        response['Accept-Ranges'] = 'bytes'
        return response


def similar_songs(request, song_id):
    """
    Возвращает похожие треки на основе исполнителя и альбома текущего трека
    """
    try:
        current_song = Song.objects.get(pk=song_id)
    except Song.DoesNotExist:
        return JsonResponse({'error': 'Song not found'}, status=404)
    
    exclude_param = request.GET.get('exclude', '')
    exclude_ids = [int(id_str) for id_str in exclude_param.split(',') if id_str.strip().isdigit()]
    if song_id not in exclude_ids:
        exclude_ids.append(song_id)
    
    # Приоритет 1: Треки из того же альбома
    similar = list(Song.objects.filter(album=current_song.album).exclude(id__in=exclude_ids)[:10])
    
    # Приоритет 2: Треки от того же исполнителя
    if len(similar) < 5:
        artist_songs = list(Song.objects.filter(artist=current_song.artist).exclude(id__in=exclude_ids).order_by('-plays')[:10])
        for song in artist_songs:
            if song not in similar:
                similar.append(song)
            if len(similar) >= 10:
                break
    
    # Приоритет 3: Популярные треки если похожих мало
    if len(similar) < 3:
        popular = list(Song.objects.exclude(id__in=exclude_ids).order_by('-plays')[:5])
        for song in popular:
            if song not in similar:
                similar.append(song)
            if len(similar) >= 10:
                break
    
    if similar:
        import random
        song = random.choice(similar)
        return JsonResponse({
            'id': song.id,
            'title': song.title,
            'artist': song.artist.name,
            'cover': song.get_cover(),
            'stream_url': song.get_stream_url(),
            'duration': song.duration,
        })
    else:
        return JsonResponse({'error': 'No similar songs found'}, status=404)


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