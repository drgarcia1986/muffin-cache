from .handler import CachedHandler


def cached_view(view, **kwargs):
    return CachedHandler.from_view(
        view, kwargs.get('methods', '*'), view.__name__
    )
