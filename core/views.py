from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from .models import Room, Topic, Message
from .forms import RoomForm


def login_page(request):
    page = "login"
    
    if request.user.is_authenticated:
        return redirect("home")
    
    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')
        
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, "Invalid Username or Password")
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Invalid Username or Password")
    
    context = {"page": page}
    return render(request, "core/login_register.html", context)


def logout_user(request):
    logout(request)
    return redirect("index")


def register_page(request):
    form = UserCreationForm()
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST) 
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Registration Error")
       
    return render(request, "core/login_register.html", {"form": form})


def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(host__username__icontains=q) |
        Q(description__icontains=q)
        )
    
    topics = Topic.objects.all()
    room_count = rooms.count()
    room_messages = Message.objects.filter(Q(room__name__icontains=q))
    
    context = {"rooms": rooms, "topics": topics, "room_count": room_count, "room_messages": room_messages}
    return render(request, "core/home.html", context)
    

def index(request):
    room_messages = Message.objects.all()
    context = {"room_messages": room_messages}
    return render(request, "core/index.html", context)


def about(request):
    return render(request, "core/about.html")

def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all()
    participants = room.participants.all()
    
    if request.method == "POST":
        message = Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get("body")
        )
        room.participants.add(request.user)
        return redirect("room", pk=room.id)
    
    context = {"room": room, "room_messages": room_messages, "participants": participants}
    return render(request, "core/room.html", context)


def user_profile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {"user": user, "rooms": rooms, "room_messages": room_messages, "topics": topics}
    return render(request, "core/profile.html", context)


@login_required(login_url="login")
def create_room(request):
    form = RoomForm()
    
    if request.method == "POST":
        form = RoomForm(request.POST, request.FILES)
        if form.is_valid():
            room = form.save(commit=False)
            room.host = request.user
            room.save()
            room.participants.add(request.user)
            return redirect("home")
    
    context = {"form": form}
    return render(request, "core/room_form.html", context)


@login_required(login_url="login")
def update_room(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    
    if request.method == "POST":
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect("home")
    
    context = {"form": form}
    return render(request, "core/room_form.html", context)
    

@login_required(login_url="login")
def delete_room(request, pk):
    room = Room.objects.get(id=pk)
    if request.method == "POST":
        room.delete()
        return redirect("home")
        
    return render(request, "core/delete.html", {"obj":room})


@login_required(login_url="login")
def delete_message(request, pk):
    message = Message.objects.get(id=pk)
    
    if request.method == "POST":
        message.delete()
        return redirect("home")
        
    return render(request, "core/delete.html", {"obj": message})