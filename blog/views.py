from django.shortcuts import render ,get_object_or_404
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
from django.core.mail import send_mail
from django.db.models import Count

from .models import *
from .forms import *

from taggit.models import Tag 

# Create your views here.

def post_share(request,post_id):

	post = get_object_or_404(Post,pk = post_id ,status = 'published')

	sent = False
	cd = None
	if request.method == 'POST':
		form = EmailPostForm(request.POST)

		if form.is_valid():

			cd = form.cleaned_data
			post_url = request.build_absolute_uri(post.get_absolute_url())

			subject = '{} ({}) recommends you reading "{}"'.format(cd['name'],cd['email'],post.title)
			message = 'Read "{}" at {}\n\n{}\'s comments: {}'.format(post.title,post_url,cd['name'],cd['comments'])
			send_mail(subject,message,'xiuzhikong@163.com',[cd['to']])
			sent = True


	else:
		form = EmailPostForm()

	return render(request,'blog/post/share.html',{'post':post,'form':form,'sent':sent,'cd':cd})




def post_list(request,tag_slug = None):
	objects_list = Post.published.all()

	tag = None

	if tag_slug:
		tag = get_object_or_404(Tag,slug = tag_slug)
		objects_list = objects_list.filter(tags__in = [tag])
	paginator = Paginator(objects_list,4)
	page = request.GET.get('page')
	try:
		posts = paginator.page(page)

	except PageNotAnInteger:
		posts = paginator.page(1)
		page = 1
	except EmptyPage:
		posts = paginator.page(paginator.num_pages)
		page = paginator.num_pages

	return render(request,'blog/post/list.html',{'page':page,'posts':posts,'tag':tag})

def post_detial(request,year,month,day,post):
	post = get_object_or_404(Post,slug=post,
								status = 'published',
								publish__year = year,
								publish__month = month,
								publish__day = day)
	comments = post.comments.filter(active=True)
	tijao = False
	if request.method == 'POST':
		comment_form = CommentForm(request.POST)
		if comment_form.is_valid():
			new_comment = comment_form.save(commit = False)
			new_comment.post = post
			new_comment.save()
			tijao = True

	else:
		comment_form = CommentForm()

	post_tags_ids = post.tags.values_list('id',flat = True)
	similar_posts = Post.published.filter(tags__in = post_tags_ids).exclude(id = post.id)

	similar_posts = similar_posts.annotate(same_tags = Count('tags')).order_by('-same_tags','-publish')[:4]

	return render(request,'blog/post/detail.html',{'post':post,
													'comments':comments,
													'comment_form':comment_form,
													'tijao':tijao,
													'similar_posts':similar_posts})


