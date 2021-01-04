import xadmin
from .models import Banner,EmailVerifyRecord
# Register your models here.

class EmailVerifyRecordAdmin:

    model_icon = "fa fa-mobile"
    list_display = ['code', 'email', 'send_type', 'send_time']
    search_fields = ['code', 'email', 'send_type']
    list_filter = ['code', 'email', 'send_type', 'send_time']


xadmin.site.register(EmailVerifyRecord,EmailVerifyRecordAdmin)


class BannerAdmin:
    model_icon = "fa fa-window-restore"
    list_display = ['title', 'image', 'url', 'index', 'add_time']
    search_fields = ['title', 'image', 'url', 'index']
    list_filter = ['title', 'image', 'url', 'index', 'add_time']


xadmin.site.register(Banner, BannerAdmin)
