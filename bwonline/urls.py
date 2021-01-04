"""bwonline URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# from django.contrib import admin
from django.urls import path,include,re_path
import xadmin
from django.views.generic import TemplateView
from django.views.static import serve
from django.conf.urls.static import static
from django.conf import settings

from apps.users.views import LoginView, \
       RegisterView, \
       AvrivaUserView, \
       ForgetPwdView, \
       ResetView, \
       ModifyPwdView

from apps.organization.views import OrgView

urlpatterns = [
       path('adminx/', xadmin.site.urls),
       path('', TemplateView.as_view(template_name='html/index.html'), name='index'),
       path('login/', LoginView.as_view(), name='login'),
       path('register/', RegisterView.as_view(), name='register'),
       path('captcha/',include('captcha.urls')),
       re_path('active/(?P<active_code>.*)/',AvrivaUserView.as_view(),name='user_active'),
       path('forget/',ForgetPwdView.as_view(),name='forget_pwd'),
       re_path('reset/(?P<active_code>.*)/', ResetView.as_view(), name='reset_pwd'),
       path('modify_pwd/', ModifyPwdView.as_view(), name='modify_pwd'),

       path("org/", include('apps.organization.urls', namespace="org")),
       # 处理图片显示的url,使用Django自带serve,传入参数告诉它去哪个路径找，我们有配置好的路径MEDIAROOT
       re_path(r'^media/(?P<path>.*)',serve,{'document_root':settings.MEDIA_ROOT}),
       path("course/", include('apps.course.urls', namespace="course")),
]


urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
