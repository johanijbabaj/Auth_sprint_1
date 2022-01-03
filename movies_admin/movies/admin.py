from django.contrib import admin
from .models import Filmwork, Genre, Person, FilmworkPerson, FilmworkGenre


class FilmworkPersonInline(admin.TabularInline):
    model = FilmworkPerson
    extra = 0


class FilmworkGenreInline(admin.TabularInline):
    model = FilmworkGenre
    extra = 0


@admin.register(Filmwork)
class FilmworkAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'creation_date', 'rating')
    list_filter = ('type',)
    search_fields = ('title',)
    fields = ('title', 'type', 'description', 'creation_date', 'certificate', 'file_path', 'rating')
    inlines = [
        FilmworkPersonInline,
        FilmworkGenreInline
    ]


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)
    fields = ('name', 'description')


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'birth_date')
    search_fields = ('full_name',)
    fields = ('full_name', 'birth_date')
