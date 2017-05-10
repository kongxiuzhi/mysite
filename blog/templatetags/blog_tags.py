from django import template
from django.db.models import Count
from django.utils.safestring import mark_safe

from ..models import Post

import markdown


'''
•	 simple_tag : Processes the data and returns a string
•	 inclusion_tag : Processes the data and returns a rendered template
•	 assignment_tag : Processes the data and sets a variable in the context
'''

#custom tags

register = template.Library()



@register.simple_tag
def total_posts():
	return Post.published.count()

@register.inclusion_tag('blog/post/latest_posts.html')
def show_latest_posts(count =5):
	latest_posts = Post.published.order_by('-publish')[:count]
	return {'latest_posts':latest_posts}

@register.assignment_tag
def get_most_commented_posts(count = 5):
	return Post.published.annotate(total_comments = Count('comments')).order_by('-total_comments')[:count]

#custom tags

#custom filter

@register.filter(name = 'markdown')
def markdown_format(text):
	return mark_safe(markdown.markdown(text))

#custom filter	