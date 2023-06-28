import json

from django.shortcuts import render
from django.http import HttpResponse
from django.views import View
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import (
    ListView,
    CreateView,
    DetailView,
    DeleteView,
    FormView,
)
from .models import UserApp, Room, Message, RoomLogs
from django.contrib.auth import get_user_model
from . import forms
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.db.models import Q
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder

class IndexView(View):
    def get(self, request):
        print(request.user.username)
        print(request)
        return render(request, 'base.html')

class RommsChat(View):
    def get(self, request):
        print(request.user.username)
        print(request)
        return render(request, 'room/display_chats_room.html')

class RegisterView(FormView):
    template_name = 'register/register.html'
    form_class = forms.RegisterForm
    success_url = 'login'

    def form_valid(self, form):
        print(form.cleaned_data)
        user = form.save()
        print(user)
        print("to jest sztos")
        return super().form_valid(form)

    def form_invalid(self, form):
        print(form.errors)
        return super().form_invalid(form)


class Login(LoginView):
    template_name = 'login/login.html'
    success_url = '/'

    def form_valid(self, form):
        # Perform the login and authentication logic
        self.request.session['username'] = form.get_user().username
        return super().form_valid(form)


class Logout(LogoutView):
    next_page = 'index'


class RoomCreateView(CreateView):
    template_name = 'room/room_create.html'
    form_class = forms.RoomForm
    success_url = '/'

    def form_valid(self, form):
        room = form.save()
        print(room)
        return super().form_valid(
            form)  # equivalet return super(RoomCreate, self).form_valid(form)


class RoomView(DetailView):
    template_name = 'room/room_detail.html'
    model = Room
    context_object_name = 'room'

    def post(self, request, *args, **kwargs):
        try:
            form = forms.RoomLoginBasedModel(request.POST)
            password_input = request.POST.get('password')
            room_log = RoomLogs.objects.filter(room=kwargs.get('pk')).exclude().values('id', 'room_id', 'user_id')
            print(room_log)
            room_log_data = list(room_log.values())
            room_log_json = json.dumps(room_log_data, cls=DjangoJSONEncoder)
            if form.is_valid():
                room = self.get_object()
                if form.check_password(room, password_input):
                    context = {
                        'messages': Message.objects.filter(room=room),
                        'information': "Properly log in",
                        'user_id' : request.user.pk,
                        'room_detail': room_log_json
                    }
                    return render(request, template_name=self.template_name,
                                  context=context)
                else:
                    return HttpResponse("Invalid password")
            else:
                form_errors = form.errors.as_json()
                return HttpResponse(f"Invalid data passed: {form_errors}",
                                    status=400)
        except Exception as e:
            raise Exception(str(e))

    def get(self, request, *args, **kwargs):
        print(request.user)
        print('This is the GET method')
        form = forms.RoomLoginBasedModel()
        return render(request, template_name=self.template_name,
                      context={'form': form})



class RoomsView(ListView):
    template_name = 'room/all_rooms.html'
    model = Room
    context_object_name = 'all_rooms'

    def get_queryset(self):
        return super().get_queryset()


def lobby(request):
    return render(request, 'chat/lobby.html')