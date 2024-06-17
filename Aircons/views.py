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
from django.conf import settings
from Users.models import Users

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
                messages.error(request, '您没有权限访问该页面')


    if request.method == 'POST':
        floor = request.POST.get('floorSelect')
        room = request.POST.get('roomSelect')
        idcard = request.POST.get('inputID')
        name = request.POST.get('inputName')

        if idcard == '' or name == '':
            return HttpResponse('<script>alert("身份证号和用户名不能为空");setTimeout(function(){history.go(-1);}, 1);</script>')
        
        # 创建 Aircon_name 作为唯一标识，可以是楼层和房间号的组合
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
    