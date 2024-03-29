from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse

from itertools import chain

from .models import Profile, Post, LikePost, Follow

# Create your views here.
@login_required(login_url='signin')
def index(request):
    user_obj = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_obj)
    # user_profile = Profile.objects.get(user=request.user)
    # posts = Post.objects.all().order_by('-created_at')
    
    following_list = []
    feed = []

    user_follows = Follow.objects.filter(follower=request.user.username)
    for follow in user_follows:
        following_list.append(follow.following)

    for username in following_list:
        followed_user_feed = Post.objects.filter(user=username)
        feed.extend(followed_user_feed)

    # Tutorial stated this had to be done before sending to frontend but local testing works without doing so.
    # feed_list = list(chain(*feed))

    return render(
        request,
        'index.html',
        { "user_profile": user_profile, "posts": feed }
    )


@login_required(login_url='signin')
def upload(request):
    if request.method == 'POST':
        user = request.user.username
        image = request.FILES.get('image_upload')
        caption = request.POST['caption']

        new_post = Post.objects.create(user=user, image=image, caption=caption)
        new_post.save()

    return redirect('/')


@login_required(login_url='signin')
def search(request):

    if request.method == 'POST':
        user_object = User.objects.get(username=request.user.username)
        user_profile = Profile.objects.get(user=user_object)
        username_search = request.POST['username']
        username_search_results = User.objects.filter(username__icontains=username_search)
        
        username_search_profile = []
        username_search_profile_list = []
        for user in username_search_results:
            username_search_profile.append(user.id)

        for user_id in username_search_profile:
            search_query_profile = (Profile.objects.get(uid=user_id))
            username_search_profile_list.append(search_query_profile)

        # username_search_profile_list = list(*username_search_profile_list)


        return render(
            request,
            'search.html',
            { 'user_profile': user_profile, 'username_profile_list': username_search_profile_list }
        )

    return redirect('/')


@login_required(login_url='signin')
def like_post(request):
    username = request.user.username
    post_id = request.GET.get('post_id')
    liked_post = Post.objects.get(id=post_id)

    like_filter = LikePost.objects.filter(post_id=post_id, username=username).first()
    
    if like_filter is None:
        new_like = LikePost.objects.create(post_id=post_id, username=username)
        new_like.save()

        liked_post.num_likes += 1
        liked_post.save()

    else:
        like_filter.delete()
        liked_post.num_likes -= 1
        liked_post.save()

    return redirect('/')


@login_required(login_url='signin')
def follow(request):
    if request.method == 'POST':
        current_user = request.user.username
        user_to_follow = request.POST['user_to_follow']

        if Follow.objects.filter(follower=current_user, following=user_to_follow).exists():
            existing_follower = Follow.objects.get(follower=current_user, following=user_to_follow)
            existing_follower.delete()
        else:
            new_follower = Follow.objects.create(follower=current_user, following=user_to_follow)
            new_follower.save()

        return redirect("profile", pk=user_to_follow)
        
    return redirect('/')    


@login_required(login_url='signin')
def profile(request, pk:str):
    user_obj = User.objects.get(username=pk)
    user_profile = Profile.objects.get(user=user_obj)
    user_posts = Post.objects.filter(user=pk).order_by('-created_at')
    num_posts = len(user_posts)
    num_posts_label = "1 post" if num_posts == 1 else f"{num_posts} posts"

    current_user_is_following = Follow.objects.filter(follower=request.user.username, following=pk).exists()
    if current_user_is_following:
        following_button_label = "Unfollow"
    else:
        following_button_label = "Follow"

    num_followers = len(Follow.objects.filter(following=pk))
    followers_label = "1 follower" if num_followers == 1 else f"{num_followers} followers"
    
    num_following = len(Follow.objects.filter(follower=pk))
    following_label = f"{num_following} following"

    context = {
        'user_object': user_obj,
        'user_profile': user_profile,
        'user_posts': user_posts,
        'num_posts_label': num_posts_label,
        'following_button_label': following_button_label,
        'num_followers_label': followers_label,
        'num_following_label': following_label
    }

    if request.method == 'POST':
        if request.FILES.get('profile_img') is None:
            image = user_profile.profile_img
        else:
            image = request.FILES.get('profile_img')
        
        user_profile.profile_img = image
        user_profile.save()
        return redirect('profile', pk=pk)

    return render(request, 'profile.html', context)


@login_required(login_url='signin')
def settings(request):
    user_profile = Profile.objects.get(user=request.user)
    
    if request.method == 'POST':

        bio = request.POST['bio']
        location = request.POST['location']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']

        if request.FILES.get('profile_img') is None:
            image = user_profile.profile_img
        else:
            image = request.FILES.get('profile_img')
        
        user_profile.profile_img = image
        user_profile.bio = bio
        user_profile.location = location
        user_profile.first_name = first_name
        user_profile.last_name = last_name 
        user_profile.save()

        return redirect('settings')

    return render(request, 'settings.html', {'user_profile': user_profile})


def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password != password2:
            messages.info(request, 'Passwords do not match!!')
            return redirect('signup')
        
        if User.objects.filter(email=email).exists():
            messages.info(request, 'Email already exists!!')
            return redirect('signup')
        
        if User.objects.filter(username=username).exists():
            messages.info(request, 'Username is taken :(')
            return redirect('signup')
        

        # Create user & profile
        user = User.objects.create_user(
            username=username, password=password, email=email
        )
        user.save()
        
        # Create profile
        user_model = User.objects.get(username=username)
        user_profile = Profile.objects.create(user=user_model, uid=user_model.id)
        user_profile.save()

        # Login user and redirect them to settings page to update their profile
        user_login = auth.authenticate(username=username, password=password)
        auth.login(request, user_login)
        return redirect('settings')

    return render(request, 'signup.html')


def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)
        
        if user is not None:
            auth.login(request, user)
            return redirect('/')
        
        messages.info(request, 'Invalid credentials!!')
        return redirect('signin')


    return render(request, 'signin.html')


@login_required(login_url='signin')
def signout(request):
    auth.logout(request)
    return redirect('signin')