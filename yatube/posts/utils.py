from django.core.paginator import Paginator

NUMBER_POSTS_ON_PAGE = 10


def get_page(request, post_list,):

    paginator = Paginator(post_list, NUMBER_POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
