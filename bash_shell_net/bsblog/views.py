from django.core.paginator import Paginator, EmptyPage
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.decorators.cache import cache_control, cache_page
from django.http import Http404

from taxonomy import models as taxonomy
from models import Post, Category

from time import strptime

def archive(request, year=None, month=None, category=None):
    post_list = Post.objects.filter(published=True)
    if category is not None:
        post_list = post_list.filter(category__name=category)
    if year is not None:
        post_list = post_list.filter(created_date__year=year)
        if month is not None:
            post_list = post_list.filter(created_date__month=strptime(month,'%b').tm_mon)

    return render_to_response(
        'bsblog/archive.html',
        {'post_list': post_list.order_by('created_date')},
        context_instance=RequestContext(request)
        )


def index(request, page=1, post_limit=None):

    page = int(page)
    if post_limit is not None:
        post_limit = int(post_limit)

    pages = Paginator(Post.objects.filter(published=True).order_by('-created_date'), post_limit)
    try:
        post_list = pages.page(page)
    except EmptyPage:
        raise Http404()
        
    return render_to_response(
        'bsblog/index.html',
        {'post_list': post_list,
         'current_page': page,
         },
        context_instance=RequestContext(request)
        )

def item(request,year,month,day,slug):
    post = get_object_or_404(Post, created_date__year=year,
                             created_date__month=strptime(month, '%b').tm_mon,
                             created_date__day=day, slug=slug)
    
    return render_to_response(
        'bsblog/blog_post.html',
        {'post': post},
        context_instance=RequestContext(request)
        )

