from django.shortcuts import render,redirect
from Users.models import Users,Users_possess
from .models import Group
from django.http import HttpResponse
from django.db.models import Q,Subquery, OuterRef
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.files.storage import FileSystemStorage
import os
import csv
from django.utils import timezone
from django.conf import settings
from Users.models import Users

# 设置默认的查询时间间隔(s)
DEFAULT_SETTING_TIME_INTERVAL = 10

# Create your views here.
def airconlist(request):
    if request.method == 'GET':
        keyStr = request.GET.get('q', '')
        ret = request.COOKIES.get('ticket')

        if not Users.objects.filter(u_ticket=ret).exists() or not ret:
            return render(request, 'register.html')

        user = Users.objects.filter(u_ticket=ret).first()
        user_state = user.user_state

        if user_state == '1':
            idcard = user.idcard
            aircon_names = Users_possess.objects.filter(idcard=idcard).values_list('Aircon_name', flat=True)
            results = Group.objects.filter(Aircon_name__in=aircon_names)
        else:
            results = Group.objects.all()

        if keyStr:
            results = results.filter(Aircon_name__icontains=keyStr)

        # 排序
        sortby = request.GET.get('sortby', 'Aircon_name')
        if sortby == 'room_id':
            results = results.order_by('Aircon_name')
        elif sortby == 'room_id_back':
            results = results.order_by('-Aircon_name')
        elif sortby == 'room_current_temp':
            results = results.order_by('room_current_temp')
        elif sortby == '-room_current_temp':
            results = results.order_by('-room_current_temp')
        else:
            results = results.order_by('id')

        # 分页
        paginator = Paginator(results, 6)  # 每页显示 6 条数据
        page = request.GET.get('page')
        try:
            results = paginator.page(page)
        except PageNotAnInteger:
            results = paginator.page(1)
        except EmptyPage:
            results = paginator.page(paginator.num_pages)

        context = {
            'results': results,
            'query': keyStr,
            'sortby': sortby,
        }

        userInfo = Users.objects.get(u_ticket=ret)
        return render(request, 'airconlist.html', {'context': context, 'userInfo': userInfo})

def get_default_temperature(aircon_name):

    static_dir = settings.STATICFILES_DIRS[0]
    csv_file_path = os.path.join(static_dir, 'default', 'default_temperature.csv')

    with open(csv_file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['Aircon_name'] == aircon_name:
                return row['room_current_temp']
    return '25'  # 默认温度，如果没有在 CSV 中找到
        
def creatOrder(request):
    if request.method == 'GET':
        ret = request.COOKIES.get('ticket')
        if not Users.objects.filter(u_ticket=ret).exists() or not ret:
            return render(request, 'register.html')
        else:
            userInfo = Users.objects.get(u_ticket=ret)
            if userInfo.user_state == '2' or userInfo.user_state == '0':
                return render(request, 'creatOrder.html', {'userInfo':userInfo})
            else:
                return HttpResponse('<script>alert("您没有权限访问该页面");setTimeout(function(){history.go(-1);}, 1);</script>')


    if request.method == 'POST':
        floor = request.POST.get('floorSelect')
        room = request.POST.get('roomSelect')
        idcard = request.POST.get('inputID')
        name = request.POST.get('inputName')

        if idcard == '' or name == '':
            return HttpResponse('<script>alert("身份证号和用户名不能为空");setTimeout(function(){history.go(-1);}, 1);</script>')
        
        # 创建 Aircon_name 作为唯一标识
        aircon_name = f"{room}"

        # 检查身份证号是否存在
        try:
            user = Users.objects.get(idcard=idcard)
        except Users.DoesNotExist:
            return HttpResponse('<script>alert("该身份证用户不存在，请让用户注册");setTimeout(function(){history.go(-1);}, 1);</script>')

        # 检查身份证号和用户名是否匹配
        if user.u_name != name:
            return HttpResponse('<script>alert("该身份证与用户姓名不匹配");setTimeout(function(){history.go(-1);}, 1);</script>')

        # 检查 Aircon_name 是否已经存在
        if Group.objects.filter(Aircon_name=aircon_name).exists():
            return HttpResponse('<script>alert("房间已经在使用");setTimeout(function(){history.go(-1);}, 1);</script>')
        
        # 获取默认温度
        room_current_temp = get_default_temperature(aircon_name)

        # 创建新的 Group 实例
        Group.objects.create(
            Aircon_name=aircon_name,
            room_current_temp=room_current_temp
        )

        # 创建新的 Users_possess 实例
        Users_possess.objects.create(
            idcard=idcard,
            Aircon_name=aircon_name
        )

        # 重定向到某个页面，比如房间列表页面
        return HttpResponse('<script>alert("创建成功");setTimeout(function(){history.go(-1);}, 1);</script>')

def changesetting(request, Aircon_name):
    if request.method == 'GET':
        ret = request.COOKIES.get('ticket')
        if not Users.objects.filter(u_ticket=ret).exists() or not ret:
            return render(request, 'register.html')
        else:
            userInfo = Users.objects.get(u_ticket=ret)
            airconInfo = Group.objects.get(Aircon_name=Aircon_name)
            processInfo = Users_possess.objects.get(Aircon_name=Aircon_name)
            if userInfo.user_state == '1':
                isUserProcess = Users_possess.objects.filter(idcard=userInfo.idcard,Aircon_name=Aircon_name).exists()
                if isUserProcess:
                    return render(request, 'changesetting.html', {'userInfo':userInfo, 'airconInfo':airconInfo, 'processInfo':processInfo})
                else:
                    return HttpResponse('<script>alert("你不是该房间的客户");setTimeout(function(){history.go(-1);}, 1);</script>')
            elif(userInfo.user_state == '4'):
                return HttpResponse('<script>alert("您没有访问的权限");setTimeout(function(){history.go(-1);}, 1);</script>')
            else:
                return render(request, 'changesetting.html', {'userInfo':userInfo, 'airconInfo':airconInfo, 'processInfo':processInfo})
    
    if request.method == 'POST':
        #获取Group的pre_setting_date
        pre_setting_date = Group.objects.get(Aircon_name=Aircon_name).pre_setting_date
        if pre_setting_date:
            current_time = timezone.now()
            interval_time=(current_time - pre_setting_date).seconds
            if (current_time - pre_setting_date).seconds < DEFAULT_SETTING_TIME_INTERVAL:
                return HttpResponse('<script>alert("修改过于频繁，请' + 
                                    str(DEFAULT_SETTING_TIME_INTERVAL-interval_time) +
                                    's后再试");setTimeout(function(){history.go(-1);}, 1);</script>')
        New_Aircon_setting_model = request.POST.get('modeButton')
        New_Aircon_setting_wind = request.POST.get('speedButton')
        New_Aircon_setting_temp = request.POST.get('temperatureButton')
        Aircon_switch = request.POST.get('powerButton')

        print(New_Aircon_setting_model, New_Aircon_setting_wind, New_Aircon_setting_temp, Aircon_switch)

        if New_Aircon_setting_model == '制冷':
            New_Aircon_setting_model = 0
        else:
            New_Aircon_setting_model = 1

        if New_Aircon_setting_wind == '低风':
            New_Aircon_setting_wind = 1
        elif New_Aircon_setting_wind == '中风':
            New_Aircon_setting_wind = 2
        elif New_Aircon_setting_wind == '高风':
            New_Aircon_setting_wind = 3

        if Aircon_switch == '关机':
            New_Aircon_setting_wind = 0            

        # 更新 Group 表中的数据
        Group.objects.filter(Aircon_name=Aircon_name).update(
            Aircon_setting_model=New_Aircon_setting_model,
            Aircon_setting_wind=New_Aircon_setting_wind,
            Aircon_setting_temp=New_Aircon_setting_temp,
            pre_setting_date=timezone.now()
        )

        return HttpResponse('<script>alert("修改成功");setTimeout(function(){history.go(-1);}, 1);</script>')