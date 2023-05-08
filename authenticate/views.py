from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from LoginPage import settings
from django.core.mail import send_mail, EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes,force_str
from . tokens import generate_token 


def main(request):
    logout(request)
    return render(request, "main.html")

def signup(request):

    if request.method=="POST":

        uname = request.POST['uname']
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        c_pass = request.POST['c_pass']

        # Required Conditions

        if User.objects.filter(username=uname):
            messages.error(request, "Username already taken.")
            return redirect('signup')
        
        if User.objects.filter(email=email):
            messages.error(request, "Email already Registered.")
            return redirect('signup')

        if len(uname)>8:
            messages.error(request, "Username must be under 8 characters.")
            return redirect('signup')

        if pass1 != c_pass:
            messages.error(request, "Password didn't match")
            return redirect('signup')

        if not uname.isalnum():
            messages.error(request, "Username must be Alpha-Numerice")
            return redirect('signup')

        myuser = User.objects.create_user(username=uname,email=email,password=pass1)
        myuser.first_name = fname
        myuser.last_name = lname
        myuser.email = email
        myuser.password = pass1
        myuser.is_active = False
        myuser.save()
        messages.success(request, "Your Account has been Successfully Created.\n We've sent you a confirmation email, please confirm your email in order to activate your account.")


        # Welcome email

        subject = "Welcome to AIEngine - User Login!!"
        message = "Hello "+ myuser.first_name + "!! \n" + "Welcome to AIEngine!! \n Thank you for visiting our website and SignUp. \n  We have also sent you a confirmation email, please confirm your email address in order to activate your account. \n Thanking You \n Deepak kumar "
        from_email = settings.EMAIL_HOST_USER
        to_list = [myuser.email]
        send_mail(subject, message, from_email, to_list, fail_silently=False)

        # Confirmation Email

        current_site = get_current_site(request)
        email_subject = "Confirm your email @ AIEngine - User Login!!"
        message2 = render_to_string('email.html' ,{
            'name': myuser.first_name,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(myuser.pk)),
            'token':generate_token.make_token(myuser)

        })
        email = EmailMessage(
            email_subject,
            message2,
            settings.EMAIL_HOST_USER,
            [myuser.email],
        )
        email.fail_silently = False
        email.send()


        return redirect("main")
    
    return render(request, "signup.html")

def signin(request):

    if request.method=='POST':
        uname = request.POST['uname']
        pass1 = request.POST['pass1']

        user = authenticate(username=uname, password=pass1)

        if user is not None:
            login(request, user)
            fname = user.first_name

            return render(request, 'main.html', {'fname':fname})

        elif user is None:
            messages.error(request, "Invalid Inputs!!", {'x':"msg1"})
            return redirect('signin')

    return render(request, "signin.html")

def signout(request, uidb64, token):
    logout(request)
    messages.success(request, 'Logged Out Successfully!!')
    return redirect('main')

def signout_1(request):
    logout(request)
    messages.success(request, 'Logged Out Successfully!!')
    return redirect('main')


def activate(request, uidb64, token):

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except (TypeError,ValueError,OverflowError,User.DoesNotExist):
        myuser = None


    if myuser is not None and generate_token.check_token(myuser, token):
        myuser.is_active = True
        myuser.save()

        login(request, myuser)
        fname = myuser.first_name
        print(fname)

        messages.success(request, "Your Account has been activated!!")
        return render(request, 'main.html', {'fname':fname})
    else:
        return render(request, 'activation_failed.html')
    

def forgot_password(request):
    if request.method=='POST':
        mymail = request.POST['email']

        try:
            if User.objects.filter(email=mymail).first():

                user = User.objects.get(email=mymail)
                print(user.pk)

                current_site = get_current_site(request)
                email_subject = "@ AIEngine - Password Reset!!"
                message2 = render_to_string('passwordresetmail.html' ,{
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token':generate_token.make_token(user)

                })
                Email = EmailMessage(
                    email_subject,
                    message2,
                    settings.EMAIL_HOST_USER,
                    [mymail],
                )
                Email.fail_silently = False
                Email.send()

                messages.success(request, 'link sent successfully!!')
                return redirect("forgot_password")
            
            else:
                messages.error(request, 'Email not registered')
                return redirect("forgot_password")

        except Exception as e:
            print(e)
            
    return render(request, 'forgot_password.html')


def change_password_form(request, uidb64, token):
    if request.method=='POST':

        pass1 = request.POST['pass1']
        c_pass = request.POST['c_pass']

        if pass1 != c_pass:
            messages.error(request, "Password didn't match")
            return render(request, 'change_password_form.html')
        elif pass1 == c_pass:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
            user.set_password(pass1)
            user.save()

            messages.success(request, "Password reset succesfully")
            return render(request, 'signin.html')


    return render(request, 'change_password_form.html', {'token':token, 'uid':uidb64})

