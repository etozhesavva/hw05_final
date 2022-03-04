from django.contrib import admin

from .models import Post, Group, Comment


class PostAdmin(admin.ModelAdmin):
    # Перечисляем поля, которые должны отображаться в админке
    list_display = (
        'pk',
        'text',
        'pub_date',
        'author',
        'group',
    )
    list_editable = ('group',)
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


admin.site.register(Post, PostAdmin)


class GroupAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
    list_display = ('pk', 'title', 'description', 'slug',)
    search_fields = ('title', 'description',)
    list_filter = ('title',)
    empty_value_display = '-пусто-'


admin.site.register(Group, GroupAdmin)


class CommentAdmin(admin.ModelAdmin):
    # Перечисляем поля, которые должны отображаться в админке
    list_display = (
        'text',
        'author',
    )
    list_editable = ('author',)
    search_fields = ('text',)
    list_filter = ('author',)
    empty_value_display = '-пусто-'


admin.site.register(Comment, CommentAdmin)
