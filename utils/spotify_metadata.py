from app.store import get_spotify_artist_cache, get_spotify_client, get_spotify_track_cache


def _chunked(items, size):
    for i in range(0, len(items), size):
        yield items[i:i + size]


def get_track_metadata(track_ids):
    cache = get_spotify_track_cache()
    unique_ids = [track_id for track_id in dict.fromkeys(track_ids) if track_id]
    missing_ids = [track_id for track_id in unique_ids if track_id not in cache]

    sp = get_spotify_client()
    if sp is not None and missing_ids:
        for chunk in _chunked(missing_ids, 50):
            try:
                response = sp.tracks(chunk)
                infos = response.get("tracks", [])
            except Exception:
                infos = []

            for track_id, info in zip(chunk, infos):
                cache[track_id] = info

    return {track_id: cache.get(track_id) for track_id in unique_ids}


def get_artist_metadata(artist_ids):
    cache = get_spotify_artist_cache()
    unique_ids = [artist_id for artist_id in dict.fromkeys(artist_ids) if artist_id]
    missing_ids = [artist_id for artist_id in unique_ids if artist_id not in cache]

    sp = get_spotify_client()
    if sp is not None and missing_ids:
        for chunk in _chunked(missing_ids, 50):
            try:
                response = sp.artists(chunk)
                infos = response.get("artists", [])
            except Exception:
                infos = []

            for artist_id, info in zip(chunk, infos):
                cache[artist_id] = info

    return {artist_id: cache.get(artist_id) for artist_id in unique_ids}
