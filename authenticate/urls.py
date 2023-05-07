from django.urls import path
from . import views

urlpatterns = [
    path('', views.main, name = 'main'),
    path('signin/signup/', views.signup, name = 'signup'),
    path('signup/', views.signup, name = 'signup'),
    path('signin/', views.signin, name = 'signin'),
    path('signout/', views.signout_1, name = 'signout_1'),
    path('activate/<uidb64>/<token>/', views.activate, name = 'activate'),
    path('signin/signout/', views.signout_1, name = 'signout_1'),
    path('activate/<uidb64>/<token>/signout/', views.signout, name = 'signout'),
    path('signin/forgot_password/',views.forgot_password, name='forgot_password'),
    path('change_password_form/<uidb64>/<token>/',views.change_password_form, name='change_password_form')


]