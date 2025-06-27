from django.shortcuts import render, redirect
from . import forms, models
from django.http import JsonResponse

def post_list_view(request):
    posts = models.Post.objects.all()

    return render(request, 'posts/post-list.html', {'posts': posts})

def create_post_view(request):
    if request.method == 'POST':
        form = forms.CreatePostForm(request.POST, request.FILES)

        if form.is_valid():
            description = form.cleaned_data['description']
            media = form.cleaned_data['media']
            author = request.user

            post = models.Post.objects.create(description=description,
                                              media=media,
                                              author=author)
            
            post.save()

            return redirect('post-list')
    else:
        form = forms.CreatePostForm()

    return render(request, 'posts/create-form.html', {'form': form})

def edit_post_form(request, pk):
    try: post = models.Post.objects.get(pk=pk)
    except: return redirect('post-list')

    if request.user != post.author: return redirect('post-list')

    if request.method == 'POST':
        form = forms.EditPostForm(request.POST)

        if form.is_valid():  
            description = form.cleaned_data['description']
            media = form.cleaned_data['media']

            if description: post.description = description
            if media: post.media = media

            post.save()

            return redirect('post-list')
    else:
        form = forms.EditPostForm(initial={'description': post.description})

    return render(request, 'posts/edit-form.html', {'form': form}) 

def delete_post_view(request, pk):
    try: post = models.Post.objects.get(pk=pk)
    except: return redirect('post-list')

    if request.user != post.author: return redirect('post-list')
    
    if request.method == 'POST':
        post.delete()
        
        return redirect('post-list')
    else:
        return render(request, 'posts/delete-post-form.html')
    

def create_comment_view(request, pk):
    if request.method == 'POST':
        form = forms.CreateCommentForm(request.POST, request.FILES)

        if form.is_valid():
            content = form.cleaned_data['content']
            media = form.cleaned_data['media']
            author = request.user
            try: post = models.Post.objects.get(pk=pk)
            except: return redirect('post-list')

            comment = models.Post.objects.create(content=content, 
                                                 media=media, 
                                                 author=author, 
                                                 post=post)
            
            comment.save()

            return redirect('post-list')
    else:
        form = forms.CreateCommentForm()

    return render(request, 'posts/create-form.html', {'form': form})

def edit_comment_form(request, pk):
    try: comment = models.Comment.objects.get(pk=pk)
    except: return redirect('post-list')

    if request.user != comment.author: return redirect('post-list')

    if request.method == 'POST':
        form = forms.EditCommentForm(request.POST)

        if form.is_valid():  
            content = form.cleaned_data['content']
            media = form.cleaned_data['media']

            if content: comment.content = content
            if media: comment.media = media

            comment.save()

            return redirect('post-list')
    else:
        form = forms.EditPostForm(initial={'description': comment.content})

    return render(request, 'posts/edit-form.html', {'form': form}) 

def delete_comment_view(request, pk):
    try: comment = models.Comment.objects.get(pk=pk)
    except: return redirect('post-list')

    if request.user != comment.author: return redirect('post-list')
    
    if request.method == 'POST':
        comment.delete()
        
        return redirect('post-list')
    else:
        return render(request, 'posts/delete-comment-form.html')

def ajax_comments_list_view(request, pk):
    try: post = models.Post.objects.get(pk=pk)
    except: return redirect('post-list')

    comments = post.comments.all()

    return JsonResponse(comments)
