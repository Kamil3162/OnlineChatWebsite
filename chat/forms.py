from django.contrib.auth.forms import UserCreationForm
from django import forms
from . import models
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password, check_password
class RegisterForm(forms.ModelForm):
    class Meta:
        model = models.UserApp
        fields = ['nickname', 'username', 'surname', 'password', 'email_address']

    def save(self, commit=True):
        print("wywołanie metody save na formie")
        user = super().save(commit=False)
        password = self.cleaned_data['password']
        user.set_password(password)
        if commit:
            user.save()
        return user

class LoginForm(forms.Form):
    email_address = forms.EmailField()
    password = forms.CharField(max_length=200)

    def __init__(self, request=None, *args, **kwargs):
        '''
            Constructor is obligated during executing LoginView if we will not
            initialize a construcor we have a fail __init__ beacuse during executing
            to form is passed argument request
        '''
        self.request = request
        super().__init__(*args, **kwargs)
        self.fields['email_address'].widget.attrs['name'] = 'email_address'
        self.fields['password'].widget.attrs['name'] = 'password'

    def clean(self):
        """
            Funkcja is ivnokking on evey field and check data validation if
            something is wrong function raise exception, return cleaned_data
        """
        cleaned_data = super().clean()  # we invoke this to check data valid
        email_address = self.request.POST.get('email_address')
        password = self.request.POST.get('password')
        print(self.fields)
        print(self.request.POST)
        print("czyszczenie danych ")
        if email_address and password:
            print("sprawdzamy dane")
            user = authenticate(username=email_address, password=password)
            print(user)
            if user is None or not user.is_active:
                raise forms.ValidationError('Invalid email address or password')
        return cleaned_data

    def login_user(self):
        data = self.cleaned_data
        print("proba zalogowania")
        try:
            user = authenticate(username=data.get('email_address'),
                                password=data.get('password'))
            login(self.request, user)
            print("zalogowano uzytkownika")
        except Exception as e:
            print("something is wrong with login:{}".format(str(e)))
            raise forms.ValidationError("An error occurred during login.")


class RoomForm(forms.ModelForm):
    class Meta:
        model = models.Room
        fields = ['name', 'password']

    def save(self, commit=True):
        room = super().save(commit=False)       # creating new instance of room
        password = self.cleaned_data['password']
        hashed = make_password(password)
        room.password = hashed
        if commit:
            room.save()
        return room


class RoomLogin(forms.Form):
    password = forms.CharField(max_length=200)

    def __init__(self, request=None, *args, **kwargs):
        super(RoomLogin, self).__init__(*args, **kwargs)
        self.request = request
        self.fields['password'].widget.attrs.update({'autofocus': 'autofocus'})

    def check_password(self, object_model):
        password_input = self.cleaned_data.get('password')
        password_proper = object_model.password
        password_compare = check_password(password_proper, password_input)
        if password_compare:
            return True
        return False

class RoomLoginBasedModel(forms.ModelForm):
    class Meta:
        model = models.Room
        fields = ['password']

    def check_password(self, object_model, password):
        password_input = password
        password_proper = object_model.password
        password_compare = check_password(password_input, password_proper)
        if password_compare:
            return True
        return False