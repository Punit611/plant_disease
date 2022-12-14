from tkinter.tix import IMAGE
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import EmailMessage, send_mail
from plant_disease import settings
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth import authenticate, login, logout
from . token_gen import generate_token


from django.core.files.storage import FileSystemStorage
from keras.models import load_model
from keras.preprocessing.image import ImageDataGenerator 
# import tensorflow as tf
import json
import numpy as np
from tensorflow import Graph
from keras.utils import load_img, img_to_array 


model =load_model('./model/model1.h5')

IMAGE_SIZE = 256
BATCH_SIZE = 32

with open('./model/classes.json','r') as f:
    labelInfo=f.read()

labelInfo=json.loads(labelInfo)

# Create your views here.
def home(request):
    return render(request, "authentication/newindex.html")

def signup(request):
    if request.method == "POST":
        username = request.POST['username']
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']
        
        if User.objects.filter(username=username):
            messages.error(request, "Username already exist! Please try some other username.")
            return redirect('home')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email Already Registered!!")
            return redirect('home')
        
        if len(username)>20:
            messages.error(request, "Username must be under 20 charcters!!")
            return redirect('home')
        
        if pass1 != pass2:
            messages.error(request, "Passwords didn't matched!!")
            return redirect('home')
        
        if not username.isalnum():
            messages.error(request, "Username must be Alpha-Numeric!!")
            return redirect('home')
        
        myuser = User.objects.create_user(username, email, pass1)
        myuser.first_name = fname
        myuser.last_name = lname
        # myuser.is_active = False
        myuser.is_active = False
        myuser.save()
        messages.success(request, "Your Account has been created succesfully!! Please check your email to confirm your email address in order to activate your account. (Do check Your Spam also)")
        
        # Welcome Email
        subject = "Welcome to plant Disease Webapp Login!!"
        message = "Hello " + myuser.first_name + "!! \n" + "Welcome to Plant Disease Webapp Login!! \nThank you for visiting our website\n. We have also sent you a confirmation email, please confirm your email address. \n\nThanking You\nGaurav Yadav"        
        from_email = settings.EMAIL_HOST_USER
        to_list = [myuser.email]
        send_mail(subject, message, from_email, to_list, fail_silently=True)
        
        # Email Address Confirmation Email
        current_site = get_current_site(request)
        email_subject = "Confirm your Email @ Plant Disease Detector Webapp!!"
        message2 = render_to_string('email_confirmation.html',{
            
            'name': myuser.first_name,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(myuser.pk)),
            'token': generate_token.make_token(myuser)
        })
        email = EmailMessage(
        email_subject,
        message2,
        settings.EMAIL_HOST_USER,
        [myuser.email],
        )
        email.fail_silently = True
        email.send()
        
        return redirect('signin')
        
        
    return render(request, "authentication/newsignup.html")


def activate(request,uidb64,token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except (TypeError,ValueError,OverflowError,User.DoesNotExist):
        myuser = None

    if myuser is not None and generate_token.check_token(myuser,token):
        myuser.is_active = True
        # user.profile.signup_confirmation = True
        myuser.save()
        login(request,myuser)
        messages.success(request, "Your Account has been activated!!")
        return redirect('signin')
    else:
        return render(request,'activation_failed.html')


def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        pass1 = request.POST['pass1']
        
        user = authenticate(username=username, password=pass1)
        
        if user is not None:
            login(request, user)
            fname = user.first_name
            # messages.success(request, "Logged In Sucessfully!!")
            return render(request, "authentication/newindex.html",{"fname":fname})
        else:
            messages.error(request, "Bad Credentials!!")
            return redirect('home')
    
    return render(request, "authentication/newsignin.html")


def signout(request):
    logout(request)
    messages.success(request, "Logged Out Successfully!!")
    return redirect('home')


def scan(req):

    return render(req,"authentication/scan.html")

def done(req):

    print(req.POST.dict())
    # image=req.GET.dict()['image']
    # print(image,"\n\n")
    fileObj=req.FILES['filePath']
    print(fileObj)
    fs=FileSystemStorage()
    filePathName=fs.save(fileObj.name,fileObj)
    filePathName="."+fs.url(filePathName)
    
    # filePathName='../media/Healthy/Corn_Health (6).jpg'
    print(filePathName)

    
    x = load_img(
    filePathName,
    target_size = (IMAGE_SIZE,IMAGE_SIZE)
    )
    print(filePathName)
    x=img_to_array(x)
    x=x/255
    x=x.reshape(1,IMAGE_SIZE,IMAGE_SIZE,3)

    # print(test)
    Y_pred = model.predict(x)
    
    y_pred = np.argmax(Y_pred, axis=1)
    print(Y_pred, y_pred)
    
    label=labelInfo[str(y_pred[0])]
    context={'filePath':filePathName,"label":label}
    return render(req,"authentication/done.html",context)

def preview(request):

    return render(request,"authentication/preview.html")