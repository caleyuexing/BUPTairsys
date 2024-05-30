from django.db import models

# Create your models here.
def default_group_users():
    return 'groupdat/groupuser/{}'.format(Group.objects.latest('id').id + 1)

def default_group_msg():
    return 'groupdat/groupmsg/{}'.format(Group.objects.latest('id').id + 1)

class Group(models.Model):
    Aircon_name = models.CharField(max_length=255)
    CreadedTime = models.DateTimeField(auto_now_add=True)
    Aircon_setting_model = models.CharField(max_length=5,default='0')
    #0制冷，1制热
    Aircon_setting_temp = models.CharField(max_length=5,default='25')
    Aircon_setting_wind = models.CharField(max_length=5,default='2')
    #风速：0关闭，1低风，2中风，3高风
    Aircon_current_model = models.CharField(max_length=5,default='0')
    #0制冷，1制热
    Aircon_current_wind = models.CharField(max_length=5,default='2')
    #风速：0关闭，1低风，2中风，3高风
    room_current_temp = models.CharField(max_length=5,default='25')
    room_img = models.CharField(max_length=255, default='img/groupimg/default.png')

    class Meta:
        db_table = 'Aircon_info'
