from django.contrib.auth.hashers import make_password
from django.shortcuts import render
from django.contrib.auth import authenticate,login
from  django.views.generic.base import View
from django.contrib.auth.backends import ModelBackend
from .models import UserProfile, EmailVerifyRecord
# Q对象用来运算且 或 非
from django.db.models import Q
from .forms import LoginForm, RegisterForm, ForgetPwdForm, ModifyPwdForm
from .utils.email_send import send_register_email
# from django.views import TemplateView


class CustomBackend(ModelBackend):
    ''' 更改基本的Modelbackend  使得邮箱和用户名都可以登录'''
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = UserProfile.objects.get(Q(username=username)|Q(email=username))
            if user.check_password(password):
                return user
        except Exception as e:
            return None


class LoginView(View):
    def get(self,request):
        return render(request,'html/login.html')

    def post(self,request):
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            user_name = request.POST.get('username', None)
            pass_word = request.POST.get('password', None)
            # 验证前端传过来的POST参数
            user = authenticate(username=user_name, password=pass_word)

            if user is not None:
                if user.is_active:
                    # 只有注册激活才能登录
                    login(request, user)
                    return render(request, 'html/index.html')
                else:
                    return render(request, 'html/login.html', {'msg': '用户名或密码错误', 'login_form': login_form})
            else:
                return render(request, 'html/login.html', {'msg': '用户名或密码错误', 'login_form': login_form})
        else:
            return render(request, 'html/login.html', {'login_form': login_form})
        

class AvrivaUserView(View):
    def get(self,request,active_code):
        all_record = EmailVerifyRecord.objects.filter(code = active_code)

        if all_record:
            for recode in all_record:

                email = recode.email
                user = UserProfile.objects.get(email=email)
                user.is_active = True
                user.save()
        else:
            return render(request,'html/active_fail.html')
        return render(request,'html/login.html')


class RegisterView(View):
    """用户注册"""
    def get(self,request):
        register_form = RegisterForm()
        return render(request,'html/register.html',{'register_form':register_form})
    
    def post(self,request):
        register_form = RegisterForm(request.POST)
        if register_form.is_valid():
            user_name = request.POST.get('email',None)
            
            if UserProfile.objects.filter(email=user_name):
                return render(request,'html/register.html',{'register_form':register_form,'msg':'用户名已存在'})

            pass_word = request.POST.get('password',None)

            # 实例化user_profile对象
            user_profile = UserProfile.objects.create(
                username = user_name,
                email = user_name,
                is_active = False,
                password = make_password(pass_word)
            )
            user_profile.save()
            send_register_email(user_name, 'register')
            return render(request, 'html/login.html')
        else:
            return render(request, 'html/register.html',{'register_form':register_form})


class ForgetPwdView(View):
    """找回密码"""
    def get(self,request):
        forget_form = ForgetPwdForm()
        return render(request,'html/forgetpwd.html',{'forget_form': forget_form})

    def post(self, request):
        forget_form = ForgetPwdForm(request.POST)
        if forget_form.is_valid():
            email = request.POST.get('email',None)
            print(email)
            send_register_email(email,'forget')
            return render(request, 'html/send_success.html')
        else:
            return render(request, 'html/forgetpwd.html', {'forget_form': forget_form})


class ResetView(View):
    def get(self,request,active_code):
        all_recprds = EmailVerifyRecord.objects.filter(code=active_code)
        if all_recprds:
            for record in all_recprds:
                email = record.email
                return render(request,'html/password_reset.html',{'email':email})
        else:
            return render(request,'html/active_fail.html')
        return render(request,'html/login.html')


class ModifyPwdView(View):
    def post(self,request):
        modify_form = ModifyPwdForm(request.POST)
        if modify_form.is_valid():
            pwd1 = request.POST.get('password1','')
            pwd2 = request.POST.get('password2','')
            email = request.POST.get("email",'')
            if pwd1 != pwd2:
                return render(request,'html/password_reset.html',{'email':email, "msg":"密码不一致！"})
            user = UserProfile.objects.get(email=email)
            user.password=make_password(pwd2)
            user.save()

            return render(request,'html/login.html')
        else:
            email = request.POST.get('email','')
            return render(request,'html/password_reset.html',{'email':email, "modify_form":modify_form})

