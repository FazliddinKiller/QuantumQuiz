from django.urls import path
from .views import *

app_name = 'genQuiz'

urlpatterns = [
    path('', home, name='home'),
    path('login/', login_view, name='login'),
    path('signup/', signup_view, name='signup'),
    path('logout/', logout_view, name='logout'),
    path('genQuiz/', genQuiz, name='genQuiz'),
    path('generate/', generate, name='generate'),
    path('profile/', profile, name='profile'),
]