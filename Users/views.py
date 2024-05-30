from django.shortcuts import render,HttpResponse,reverse
import random
import  time,os
from django.db.models import Q
from django.contrib.auth.hashers import make_password,check_password
from django.http import HttpResponse
from .models import Users
import random
import json
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
# Create your views here.


def index(request):
    if request.method == 'GET':
        ret = request.COOKIES.get('ticket')
        if not Users.objects.filter(u_ticket=ret).exists() or not ret:
            return render(request, 'index.html')
        else:
            userInfo = Users.objects.get(u_ticket=ret)
            return render(request,'index.html',{'userInfo':userInfo})
        
@csrf_exempt
def register(request):
    if request.method == 'GET':
        ret = request.COOKIES.get('ticket')
        if Users.objects.filter(u_ticket=ret).exists() and ret:
            return render(request, 'index.html')
        else:
            return render(request, 'register.html')
    if request.method == 'POST':
        # 注册
        data = json.loads(request.body.decode('utf-8'))
        name = data.get('name')
        tel = data.get('tel')
        idcard = data.get('idcard')
        if len(name)>12:
            return HttpResponse(json.dumps({'success': False, 'error': '用户名过长，请在十二个字符之内','errorid':1}), content_type="application/json")
        if True:
            if not Users.objects.filter(tel = tel).exists():
                if not Users.objects.filter(idcard = idcard).exists():
                    password = data.get('password')
                    repassword = data.get('repassword')
                    # 对密码进行加密
                    if(repassword==password):
                        password = make_password(password)
                        Users.objects.create(u_name=name, u_password=password,tel=tel,idcard=idcard)
                        headimg_dir = os.path.join(settings.STATIC_ROOT, 'img', 'headimg', name)
                        os.makedirs(headimg_dir, exist_ok=True)
                        userdat_dir = os.path.join(settings.STATIC_ROOT, 'userdat', name)
                        os.makedirs(userdat_dir, exist_ok=True)
                        return HttpResponse(json.dumps({'success': True}), content_type="application/json")
                    else:
                        return HttpResponse(json.dumps({'success': False, 'error': '两次密码不一致，请重试','errorid':2}), content_type="application/json")
                else:
                    return HttpResponse(json.dumps({'success': False, 'error': '此身份证已注册','errorid':3}), content_type="application/json")
            else:
                return HttpResponse(json.dumps({'success': False, 'error': '此号码已被注册','errorid':4}), content_type="application/json")
        else:
            return HttpResponse(json.dumps({'success': False, 'error': '用户名已存在','errorid':5}), content_type="application/json")
        
@csrf_exempt
def login(request):
    if request.method == 'POST':
        # 登录
        data = json.loads(request.body.decode('utf-8'))
        print(data)
        name = data.get('idcard')
        password = data.get('password')
        if Users.objects.filter(Q(tel=name) | Q(idcard=name)).exists():
            user = Users.objects.get(Q(tel=name) | Q(idcard=name))
            if check_password(password, user.u_password):
                ticket = ''
                for i in range(15):
                    s = 'abcdefghijklmnopqrstuvwxyz'
                    # 获取随机的字符串
                    ticket += random.choice(s)
                now_time = int(time.time())
                ticket = 'TK' + ticket + str(now_time)
                # 绑定令牌到cookie里面
                # 存在服务端
                user.u_ticket = ticket
                user.save() #保存
                return HttpResponse(json.dumps({'success': True,'tkt':ticket}), content_type="application/json")
            else:
                return HttpResponse(json.dumps({'success': False, 'error': 'password error','errorid':1}), content_type="application/json")
        else:
            return HttpResponse(json.dumps({'success': False, 'error': 'have not this user','errorid':2}), content_type="application/json")