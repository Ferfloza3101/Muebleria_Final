from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.db import models
from django.db.models import Count, Exists, OuterRef
from django.core.paginator import Paginator
from .models import Blog, Comentario

# vistas del blog

def listado_blog(request):
    categoria = request.GET.get('categoria')
    categorias = Blog._meta.get_field('categoria').choices

    blogs_qs = Blog.objects.select_related('autor')
    if categoria:
        blogs_qs = blogs_qs.filter(categoria=categoria)

    blogs_qs = blogs_qs.annotate(
        num_likes=Count('likes', distinct=True),
        num_comentarios=Count('comentarios', distinct=True),
    )

    if request.user.is_authenticated:
        like_m2m = Blog.likes.through
        blogs_qs = blogs_qs.annotate(
            liked_by_user=Exists(
                like_m2m.objects.filter(blog_id=OuterRef('pk'), user_id=request.user.id)
            )
        )
    else:
        blogs_qs = blogs_qs.annotate(liked_by_user=models.Value(False, output_field=models.BooleanField()))

    blogs_qs = blogs_qs.order_by('-num_likes', '-fecha_creacion')

    paginator = Paginator(blogs_qs, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'blog/listado_blog.html', {
        'blogs': page_obj,
        'categorias': categorias,
        'categoria_actual': categoria,
        'mensaje': 'Ideas para ti',
        'page_obj': page_obj,
    })

def detalle_blog(request, blog_id):
    blog = get_object_or_404(
        Blog.objects.select_related('autor').annotate(
            num_likes=Count('likes', distinct=True)
        ),
        id=blog_id
    )
    comentarios = blog.comentarios.select_related('usuario').order_by('-fecha')

    liked_by_user = False
    if request.user.is_authenticated:
        liked_by_user = blog.likes.filter(id=request.user.id).exists()

    if request.method == 'POST' and request.user.is_authenticated:
        texto = request.POST.get('comentario')
        if texto:
            Comentario.objects.create(blog=blog, usuario=request.user, texto=texto)
            return redirect('blog:detalle_blog', blog_id=blog.id)
    return render(request, 'blog/detalle_blog.html', {
        'blog': blog,
        'comentarios': comentarios,
        'mensaje': 'Detalle del blog',
        'liked_by_user': liked_by_user,
    })

@login_required
@require_POST
def like_blog(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id)
    user = request.user
    liked = False
    if blog.likes.filter(id=user.id).exists():
        blog.likes.remove(user)
    else:
        blog.likes.add(user)
        liked = True
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'liked': liked, 'likes': blog.likes.count()})
    return redirect('blog:detalle_blog', blog_id=blog.id)
