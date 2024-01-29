from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.http import HttpResponse

from .models import Profile

# Create your views here.
def index(request):
    return render(request, 'index.html')


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
        
        user = User.objects.create_user(
            username=username, password=password, email=email
        )
        user.save()

        user_model = User.objects.get(username=username)
        user_profile = Profile.objects.create(user=user_model, uid=user_model.id)
        user_profile.save()
        return redirect('signin')

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