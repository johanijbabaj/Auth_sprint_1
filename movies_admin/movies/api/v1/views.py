from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Q
from django.http import JsonResponse
from django.views.generic.list import BaseListView
from django.views.generic.detail import BaseDetailView

from movies.models import Filmwork, PersonRole


class MoviesApiMixin:
    model = Filmwork
    http_method_names = ['get']

    def get_queryset(self):
        qs = Filmwork.objects.prefetch_related(
            'genres', 'persons'
        ).values(
            'id', 'title', 'description', 'creation_date', 'rating', 'type'
        ).annotate(
            genres=ArrayAgg('genres__name', distinct=True),
            actors=self._aggregate_person(role=PersonRole.ACTOR),
            directors=self._aggregate_person(role=PersonRole.DIRECTOR),
            writers=self._aggregate_person(role=PersonRole.WRITER)
        )
        return qs

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context)

    def _aggregate_person(self, role):
        return ArrayAgg('persons__full_name', distinct=True, filter=Q(filmworkperson__role=role))


class MoviesListApi(MoviesApiMixin, BaseListView):

    paginate_by = 50

    def get_context_data(self, *, object_list=None, **kwargs):
        qs = self.get_queryset()
        paginator, page, queryset, is_paginated = self.paginate_queryset(
            qs,
            self.paginate_by
        )
        context = {
            "count": paginator.count,
            "total_pages": paginator.num_pages,
            "prev": page.previous_page_number() if page.has_previous() else None,
            "next": page.next_page_number() if page.has_next() else None,
            'results': list(page),
        }
        return context


class MoviesDetailApi(MoviesApiMixin, BaseDetailView):

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)['object']
