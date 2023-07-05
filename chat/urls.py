from django.urls import path 
from . import views 
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('', views.lobby),
    path('base', views.IndexView.as_view(), name="index"),
    path('rooms-message', views.RommsChat.as_view(), name="rooms-message"),
    path('register', views.RegisterView.as_view(), name="register"),
    path('login', views.Login.as_view(), name="login"),
    path('logout', views.Logout.as_view(), name="logout"),
    path('room_create', login_required(views.RoomCreateView.as_view()), name="room_create"),
    path('room/<int:pk>/', login_required(views.RoomView.as_view()), name="room_detail"),
    path('rooms', login_required(views.RoomsView.as_view()), name="room_list"),
]