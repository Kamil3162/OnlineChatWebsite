import json
import time
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
from django.db.models import Q, F, OuterRef,Subquery
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from functools import wraps
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
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

    def spam_limit(function):
        @wraps(function)
        def wrapper(self, request, *args, **kwargs):
            RATE_LIMIT_DURATION = 60
            MAX_MESSAGE_AMOUNT = 20
            # we get ip of user
            ip_address = request.META.get("REMOTE_ADDR")
            current_time = time.time()
            print("to jest wykjonywanie wrappera")
            last_submission_time, message_count = self.get_rate_limit_data(ip_address)
            print(last_submission_time, message_count)
            elapsed_time = current_time - last_submission_time

            if elapsed_time > RATE_LIMIT_DURATION or message_count > MAX_MESSAGE_AMOUNT:
                return HttpResponse("Rate limit is exceedd", status=429)

            if elapsed_time >= RATE_LIMIT_DURATION:
                rate_limit_data = (current_time, 1)
            else:
                rate_limit_data = (last_submission_time, message_count + 1)

            self.update_limit_data(ip_address, rate_limit_data)

            return function(self, request, *args, **kwargs)

        return wrapper

    def get_rate_limit_data(self, user_ip):
        # request.META.get(REMOTE_ADDR)
        cache_key = f'rate_limit_{user_ip}'
        print("set cache")
        print(cache_key)
        rate_limit_data = cache.get(cache_key)
        if rate_limit_data is None:
            return (time.time(), 0)
        return rate_limit_data

    def update_limit_data(self, user_ip, rate_limit_data):
        try:
            cache_key = f'rate_limit_{user_ip}'
            print("update cachce")
            print(cache_key)
            cache.set(cache_key, rate_limit_data, 60)
        except Exception as e:
            print(str(e))
            raise e("Something going bad")

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
                        'room_detail': room_log_json,
                        'proper_password': True
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

        context = {
            'form': forms.RoomLoginBasedModel(),
            'proper_password':False
        }
        return render(request, template_name=self.template_name,
                      context=context)
class RoomsView(ListView):
    template_name = 'room/all_rooms.html'
    model = Room
    context_object_name = 'all_rooms'
    paginate_by = 4

    def get_queryset(self):
        '''
        Returns:
            SELECT room.*, (SELECT message_content
                FROM message
                WHERE message.room_id = room.id
                ORDER BY RANDOM()
                LIMIT 1) AS random_message
                FROM room;
            Zwraca po jednej wiadomosci do kazdego room .
            Wiadomosc jest losowa
        '''
        queryset = super().get_queryset()
        random_message_subquery = Message.objects.filter(
            room=OuterRef('pk')).order_by('?')[:1]
        queryset = queryset.annotate(random_message=Subquery(
            random_message_subquery.values('message_content')))
        return queryset

    def get_context_data(self, **kwargs):
        context = super(RoomsView, self).get_context_data(**kwargs)
        context['rooms'] = self.get_queryset()
        paginator = Paginator(context['rooms'], self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['page_obj'] = page_obj
        return context

def lobby(request):
    return render(request, 'chat/lobby.html')