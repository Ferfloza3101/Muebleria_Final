from django.contrib import admin
from django.db.models import Count
from .models import Blog, Comentario

# inline de comentarios
class ComentarioInline(admin.TabularInline):
    model = Comentario
    extra = 0
    readonly_fields = ('usuario', 'texto', 'fecha')

# admin del blog
class BlogAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'autor', 'categoria', 'fecha_creacion', 'num_likes')
    list_filter = ('categoria', 'fecha_creacion')
    search_fields = ('titulo', 'contenido')
    inlines = [ComentarioInline]
    readonly_fields = ('num_likes',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('autor').annotate(_num_likes=Count('likes', distinct=True))

    def num_likes(self, obj):
        return getattr(obj, '_num_likes', obj.likes.count())
    num_likes.short_description = 'Likes'

admin.site.register(Blog, BlogAdmin)
admin.site.register(Comentario)
