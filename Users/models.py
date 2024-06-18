from django.db import models


class Users(models.Model):
    u_name = models.CharField(max_length=12)
    u_password = models.CharField(max_length=255)
    u_ticket = models.CharField(max_length=30, null=True)
    headimg = models.TextField(max_length=255, default='img/headimg/default.jpg')
    user_dat = models.CharField(max_length=255, default='userdat/')
    registerTime = models.DateTimeField(auto_now_add=True)
    tel = models.CharField(max_length=16,default='null')
    idcard = models.CharField(max_length=255,default='null')
    user_state = models.CharField(max_length=5,default='1',)
    #0Root，1客户，2前台，3空调管理员,4经理
    user_tel_state = models.CharField(max_length=1,default='0')
    #0未验证手机，1已验证手机
    user_email_state = models.CharField(max_length=1,default='0')
    #0未验证邮箱，1已验证邮箱

    class Meta:
        db_table = 'Users_info'

    def __str__(self):
        return self.u_name

    def save(self, *args, **kwargs):
        self.user_dat = 'userdat/{}'.format(self.u_name)
        super().save(*args, **kwargs)

class Users_possess(models.Model):
    idcard = models.CharField(max_length=255,default='null')
    Aircon_name = models.CharField(max_length=255)
    opentime = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Users_possess'