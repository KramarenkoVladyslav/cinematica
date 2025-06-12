from .models import WatchlistItem

def watchlist_count(request):
    if request.user.is_authenticated:
        count = WatchlistItem.objects.filter(user=request.user).count()
    else:
        count = 0
    return {'watchlist_count': count}