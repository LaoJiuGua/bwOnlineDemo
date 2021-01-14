import json

from django.contrib.auth.hashers import make_password
# from django.core.paginator import PageNotAnInteger, Paginator
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from  django.views.generic.base import View
from django.contrib.auth.backends import ModelBackend
from pure_pagination import Paginator,PageNotAnInteger

from .models import UserProfile, EmailVerifyRecord
# Q对象用来运算且 或 非
from django.db.models import Q
from .forms import LoginForm, RegisterForm, ForgetPwdForm, ModifyPwdForm, UploadImageForm, UserInfoForm
from .utils.email_send import send_register_email
# from django.views import TemplateView
from ..course.models import Course
from ..organization.models import CourseOrg, Teacher
from ..teacher.models import UserCourse, UserFavorite, UserMessage
from ..utils.mixin_utils import LoginRequiredMixin


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
                    return HttpResponseRedirect(reverse('index'))
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
    def get(self, request,active_code):
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


class UserinfoView(LoginRequiredMixin,View):
    '''用户个人信息'''
    def get(self,request):
        return render(request,'html/usercenter-info.html',{

        })

    def post(self, request):
        user_info_form = UserInfoForm(request.POST, instance=request.user)
        print(request.POST)
        if user_info_form.is_valid():
            user_info_form.save()
            return HttpResponse('{"status":"success"}', content_type='application/json')
        else:
            return HttpResponse(json.dumps(user_info_form.errors), content_type='application/json')

class UploadImageView(LoginRequiredMixin,View):
    '''修改头像'''
    def post(self, request):
        image_form = UploadImageForm(request.POST)
        if image_form.is_valid():
            image = image_form.cleaned_data["image"]
            request.user.image = image
            request.user.save()
            return HttpResponse('{"status":"success"}', content_type='application/json')
        else:
            return HttpResponse('{"status":"fail"}', content_type='application/json')


class UpdatePwdView(View):
    """ 修改密码 """
    def post(self,request):
        modify_form = ModifyPwdForm(request.POST)
        if modify_form.is_valid():
            pwd1 = request.POST.get('password1', '')
            pwd2 = request.POST.get('password2', '')
            if pwd1 != pwd2:
                return HttpResponse('{"status":"fail","msg":"密码不一致"}',content_type="application/json")
            user = request.user
            user.password = make_password(pwd2)
            user.save()

            return HttpResponse('{"status":"success"}',content_type="application/json")
        else:
            return HttpResponse(json.dumps(modify_form.errors), content_type='application/json')


class SendEmailCodeView(LoginRequiredMixin,View):
    """ 发送邮箱验证码 """
    def get(self, request):
        email = request.GET.get("email", "")

        if UserProfile.objects.filter(email=email):
            return HttpResponse('{"email":"邮箱已存在"}', content_type='application/json')

        send_register_email(email, 'update_email')
        return HttpResponse('{"status":"success"}', content_type='application/json')



class MyCourseView(LoginRequiredMixin, View):
    ''' 我的课程 '''
    def get(self,request):
        user_course = UserCourse.objects.filter(user=request.user)
        return render(request, "html/usercenter-mycourse.html", {
            "user_course": user_course
        })


class MyFavOrgView(LoginRequiredMixin, View):
    """ 我收藏的课程机构 """

    def get(self, request):
        org_list = []
        fav_orgs = UserFavorite.objects.filter(user=request.user,fav_type=2)

        for fav_org in fav_orgs:
            org_id = fav_org.fav_id
            org = CourseOrg.objects.get(id=org_id)
            org_list.append(org)
        return render(request, "html/usercenter-fav-org.html", {
            "org_list": org_list
        })


class MyFavTeacherView(LoginRequiredMixin,View):
    ''' 我收藏的授课讲师 '''

    def get(self,request):
        teacher_list = []
        fav_teachers = UserFavorite.objects.filter(user=request.user,fav_type=3)

        for fav_teacher in fav_teachers:
            teacher_id = fav_teacher.fav_id
            teacher = Teacher.objects.get(id=teacher_id)
            teacher_list.append(teacher)
        return render(request, "html/usercenter-fav-teacher.html", {
            "teacher_list": teacher_list
        })


class MyFavCourseView(LoginRequiredMixin,View):
    '''  我收藏的课程 '''
    def get(self,request):
        course_list = []
        fav_courses = UserFavorite.objects.filter(user=request.user,fav_type=1)

        for fav_course in fav_courses:
            course_id = fav_course.fav_id
            course = Course.objects.get(id=course_id)
            course_list.append(course)
        return render(request, "html/usercenter-fav-course.html", {
            "course_list": course_list
        })


class MyMessageView(LoginRequiredMixin,View):
    ''' 我的消息 '''

    def get(self,request):
        all_message = UserMessage.objects.filter(user=request.user.id)

        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1

        p = Paginator(all_message, 4 , request=request)
        messages = p.page(page)
        return render(request, "html/usercenter-message.html", {
            "messages": messages
        })


class LogoutView(View):
    '''用户登出'''
    def get(self,request):
        logout(request)
        from django.urls import reverse
        return HttpResponseRedirect(reverse('index'))


# class LoginUnsafeView(View):
#     def get(self, request):
#         return render(request, "html/login.html", {})
#     def post(self, request):
#         user_name = request.POST.get("username", "")
#         pass_word = request.POST.get("password", "")
#
#         import MySQLdb
#         conn = MySQLdb.connect(host='127.0.0.1', user='root', passwd='123456', db='mxonline', charset='utf8')
#         cursor = conn.cursor()
#         sql_select = "select * from users_userprofile where email='{0}' and password='{1}'".format(user_name, pass_word)
#
#         result = cursor.execute(sql_select)
#         for row in cursor.fetchall():
#             # 查询到用户
#             pass
#         print('test')


from django.shortcuts import render_to_response
def pag_not_found(request):
    # 全局404处理函数
    response = render_to_response('html/404.html', {})
    response.status_code = 404
    return response

def page_error(request):
    # 全局500处理函数
    from django.shortcuts import render_to_response
    response = render_to_response('html/500.html', {})
    response.status_code = 500
    return response