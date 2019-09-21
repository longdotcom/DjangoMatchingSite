from django.shortcuts import render
from django.utils import timezone
from django.http import HttpResponse, Http404
from django.template import RequestContext, loader
from matchingapp.models import *
from django.contrib.auth.hashers import make_password
from django.db import IntegrityError
from django.views.decorators.csrf import csrf_exempt
from collections import Counter
from django.core.mail import BadHeaderError, send_mail,EmailMessage
from django.http import JsonResponse
from django.http import QueryDict

from datetime import date
import random, string
import uuid
from django.utils.translation import ugettext
import datetime as D
import sys

appname = 'HobbyLobby'

# logged in decorator implemented as shown in socialnetwork example
def loggedin(view):
    def modview(request):
        if 'username' in request.session:
            username = request.session['username']
            try: user = Member.objects.get(username=username)
            except Member.DoesNotExist: raise Http404('Member not found')
            return view(request, user)
        else:
            return render(request,'matchingapp/index.html',{})
    return modview

def index(request):
    context = { 'appname': appname }
    return render(request,'matchingapp/index.html',context)

def signup(request):
    context = { 'appname': appname }
    return render(request,'matchingapp/signup.html',context)

# @csrf_exempt
def register(request):
    if 'username' in request.POST and 'password' in request.POST and 'gender' in request.POST and 'dob' in request.POST and 'firstname' in request.POST and 'lastname' in request.POST and 'email' in request.POST:
        username = request.POST['username']
        password = request.POST['password']
        gender = request.POST['gender']
        dob = request.POST['dob']
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        email = request.POST['email']
        profiletext = request.POST['profiletext']

        if 'imgfile' in request.FILES:
            image = request.FILES['imgfile']
            print(image)
        else:
            image = 'placeholder.png'

        user = Member(username=username)
        user.set_password(password)
        user.gender = gender
        user.dob = dob
        user.first_name = firstname
        user.last_name = lastname
        user.email = email


        profile = Profile()
        profile.image = image
        profile.text = profiletext
        profile.save()
        user.profile = profile
        user.save()

        # each hobby value in list represnered by db ID passed from form value
        hobbylist = request.POST.getlist('hobby')

        for hobby in hobbylist:
            user.hobby.add(int(hobby))

        user.save()

        # Extra feature of emailing signed up user to confirm their username and password
        send_mail(
            'Welcome to HobbyLobby',
            'You have successfully signed up as; ' + username + ', and your password is; ' + password ,
            'hobbylobbyhobbylobby@gmail.com',
            [email],
            fail_silently=False,
        )
        #except IntegrityError: raise Http404('Username '+u+' already taken: Usernames must be unique')
        context = {
            'appname' : appname,
            'username' : username
        }
        return render(request,'matchingapp/signedup.html',context)

    else:
        return render(request,'matchingapp/allfields.html',{})

# @csrf_exempt
def login(request):
        username = request.POST['username']
        password = request.POST['password']
        try: member = Member.objects.get(username=username)
        except Member.DoesNotExist: return render(request, 'matchingapp/notfound.html', {})
        if member.check_password(password):
            # remember user in session variable
            request.session['username'] = username
            request.session['password'] = password
            context = {
               'appname': appname,
               'username': username,
               'loggedin': True
            }
            response = render(request, 'matchingapp/loggedin.html', context)
            # cookie example from socialnetwork edited to one day expiry
            timeNow = D.datetime.utcnow()
            maxAge = 1 * 24 * 60 * 60  #one year
            deltaDelta = timeNow + D.timedelta(seconds=maxAge)
            dateformat = "%a, %d-%b-%Y %H:%M:%S GMT"
            expire = D.datetime.strftime(deltaDelta, dateformat)
            response.set_cookie('last_login',timeNow,expires=expire)
            return response
        else:
            context = {'username':username}
            return render(request, 'matchingapp/incorrect.html', context)

#logout example similar to as shown in socialnetwork
@loggedin
def logout(request, user):
    request.session.flush()
    context = { 'appname': appname }
    return render(request,'matchingapp/logout.html', context)

@loggedin
def profile(request, user):

    userToView = request.GET['view']

    user = Member.objects.get(username=userToView)

    context = {
        'appname': appname,
        'username': user.username,
        'firstname' : user.first_name,
        'lastname' : user.last_name,
        'email' : user.email,
        'dob': user.dob,
        'gender' : user.gender,
        'profiletext' : user.profile.text,
        'profileimage' :user.profile.image,
        'hobbies' : user.hobby.all(),
        'loggedin': True
    }
    return render(request, 'matchingapp/profile.html', context)

@loggedin
def matched(request, user):
    userName = request.session['username']
    currentUser = Member.objects.get(username=userName)
    matched_list = Member.objects.filter(hobby__in=currentUser.hobby.all()).exclude(username=userName)

    #counter object counts occurances of user and sorts by order of apperances in list
    matched_list = Counter(matched_list)

    print(dict(matched=matched_list))

    return render(request,'matchingapp/matchedusers.html', dict(matched=matched_list),)

# function called via ajax to update table, implemented by gender
# @csrf_exempt
@loggedin
def update(request, user):
    gender = request.POST['gender']
    userName = request.session['username']
    currentUser = Member.objects.get(username=userName)
    if gender == "M":
        gender = "F"
    else:
        gender ="M"

    userName = request.session['username']
    matched_list = Member.objects.filter(hobby__in=currentUser.hobby.all()).exclude(username=userName).exclude(gender=gender)

    matched_list = Counter(matched_list)
    # matched_list = list(matched_list)
    # print(matched_list)
    for key in matched_list.keys():
      if type(key) is not str:
        try:
          matched_list[str(key)] = matched_list[key]
        except:
          try:
            matched_list[repr(key)] = matched_list[key]
          except:
            pass
        del matched_list[key]

    return JsonResponse(matched_list)
    # return HttpResponse(dict(matched=matched_list))


# @csrf_exempt
@loggedin
def editprofilerequest(request, user):
        userName = request.session['username']
        context = {
            'username':userName,
            'loggedin': True,
        }
        return render(request,'matchingapp/editprofile.html',context)


# @csrf_exempt
@loggedin
def editprofile(request, user):

        userName = request.session['username']
        currentUser = Member.objects.get(username=userName)

        if request.POST['firstname']:
            currentUser.first_name = request.POST['firstname']

        if request.POST['lastname']:
            currentUser.last_name = request.POST['lastname']

        if request.POST['email']:
            currentUser.email = request.POST['email']

        if request.POST['profiletext']:
            currentUser.profile.text = request.POST['profiletext']

        if request.POST['password']:
            currentUser.set_password(request.POST['password'])

        if request.FILES.get('imgfile'):
            currentUser.profile.image = request.FILES['imgfile']

        currentUser.profile.save()
        currentUser.save()

        success = "you have successfully updated your profile"

        context = {
            'username' : userName,
            'success' : success,
        }

        return render(request,'matchingapp/loggedin.html',context)


def forgotten(request):
    return render(request, 'matchingapp/forgotten.html')

# extra feature to reset password, sent to users email account
def forgottenpassword(request):
    userName = request.POST['username']
    currentUser = Member.objects.get(username=userName)
    # generates random string of letters and numbers
    password = str(uuid.uuid4())
    currentUser.set_password(password)
    email = currentUser.email
    currentUser.save()

    send_mail(
        'HobbyLobby',
        'Hi, ' + userName + ', your password has been set to; ' + password ,
        'hobbylobbyhobbylobby@gmail.com',
        [email],
        fail_silently=False,
    )

    success = "A new password has been sent to your email address"

    context = {
        'success' : success,
        'email' : email,
    }

    return render(request,'matchingapp/index.html',context)

# extra feature to delete account when logged in
# @csrf_exempt
@loggedin
def deleteaccount(request, user):
    userName = request.session['username']
    user = Member.objects.get(username=userName)
    email = user.email
    user.profile.delete()
    user.delete()
    request.session.flush()

    send_mail(
        'HobbyLobby',
        'Hi, ' + userName + ', your account has been successfully deleted.',
        'hobbylobbyhobbylobby@gmail.com',
        [email],
        fail_silently=False,
    )
    return render(request,'matchingapp/deleted.html',{})

@loggedin
def loggedinreturn(request, user):
        userName = request.session['username']

        context = {
            'username' : userName,
        }

        return render(request,'matchingapp/loggedin.html',context)
