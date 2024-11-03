from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
class StandardPaginationFlashcards(PageNumberPagination):
    page_size = 9
    page_size_query_param = 'page_size'
    max_page_size = 12

    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'results': data
        })

class ReviewModePaginationFlashcard(PageNumberPagination):
    page_size = 1
    page_size_query_param = 'page_size'
    max_page_size = 1
    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'results': data
        })