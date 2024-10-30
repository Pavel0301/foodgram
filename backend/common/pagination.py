from rest_framework.pagination import PageNumberPagination


class CustomPaginator(PageNumberPagination):
    """Пагинатор для получения 6 элементов на странице."""

    page_size = 6
    page_size_query_param = 'limit'
