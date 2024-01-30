from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse

from .models import Profile

# Create your views here.
@login_required(login_url='signin')
def index(request):
    return render(request, 'index.html')


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