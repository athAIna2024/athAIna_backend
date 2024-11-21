from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

# pagination useful for progress tracking
class SingleQuestionPagination(PageNumberPagination):
    page_size = 1
    page_size_query_param = 'page_size'
    max_page_size = 1

    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': None,
            },
            'count': self.page.paginator.count,
            'current': self.page.number,
            'total_pages': self.page.paginator.num_pages,
            'results': data
        })