from django.urls import path

from matchingapp import views

urlpatterns = [
    path('', views.index, name='index'),
    path('home/', views.index, name='index'),
    path('signup/', views.signup, name='signup'),
	path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('matched/', views.matched, name='matched'),
    path('profile/', views.profile, name='profile'),
    path('update/', views.update, name='update'),
    path('editprofilerequest/', views.editprofilerequest, name='editprofilerequest'),
    path('editprofile/', views.editprofile, name='editprofile'),
    path('forgotten/', views.forgotten, name='forgotten'),
    path('forgottenpassword/', views.forgottenpassword, name='forgottenpassword'),
    path('deleteaccount/', views.deleteaccount, name='deleteaccount'),
    path('loggedinreturn/', views.loggedinreturn, name='loggedinreturn'),
]
