from .models import Wishlist

def wishlist_menu_context(request):
    if request.user.is_authenticated:
        wishlist, _ = Wishlist.objects.get_or_create(usuario=request.user)
        return {'wishlist_menu': wishlist}
    return {'wishlist_menu': None} 