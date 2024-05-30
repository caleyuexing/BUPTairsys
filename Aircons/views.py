from django.shortcuts import render,redirect
from Users.models import Users
from .models import Group
from django.http import HttpResponse
from django.db.models import Q,Subquery, OuterRef
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.files.storage import FileSystemStorage
import os
from django.conf import settings
from Users.models import Users

# Create your views here.
def airconlist(request):
    if request.method == 'GET':
        keyStr = request.GET.get('q')
        if not keyStr:
            keyStr = ''
        ret = request.COOKIES.get('ticket')
        results = Group.objects.order_by('CreadedTime').filter(Q(Aircon_name__icontains=keyStr))
        #排序
        sortby = request.GET.get('sortby', 'id')
        if sortby == 'CreadedTime':
            results = results.order_by('CreadedTime')
        elif sortby == 'group_users_num':
            results = results.order_by('group_users_num')
        elif sortby == 'CreadedTime_back':
            results = results.order_by('-CreadedTime')
        elif sortby == 'group_users_num_back':
            results = results.order_by('-group_users_num')

        paginator = Paginator(results, 6)  # 每页显示 12 条数据
        page = request.GET.get('page')
        try:
            results = paginator.page(page)
        except PageNotAnInteger:
            # 如果 page 参数不是一个整数，显示第一页
            results = paginator.page(1)
        except EmptyPage:
            # 如果 page 参数超过了页数范围，显示最后一页
            results = paginator.page(paginator.num_pages)

        context = {
            'results': results,
            'query': keyStr,
            'sortby': sortby,
        }

        if not Users.objects.filter(u_ticket=ret).exists() or not ret:
            return render(request, 'grouplist.html', {'context':context})
        else:
            userInfo = Users.objects.get(u_ticket=ret)
            return render(request, 'grouplist.html', {'context':context,'userInfo':userInfo})
        
def creatgroup(request):
    if request.method == 'GET':
        ret = request.COOKIES.get('ticket')
        if not Users.objects.filter(u_ticket=ret).exists() or not ret:
            return render(request, 'register.html')
        else:
            userInfo = Users.objects.get(u_ticket=ret)
            return render(request, 'creatgroup.html', {'userInfo':userInfo})
        
    if request.method == 'POST':
        thisid=str(Group.objects.latest('id').id + 1)
        group_name = request.POST['group_name']            
        group_password = request.POST['group_password']
        group_state = request.POST['grouptype']
        group_users_num = request.POST['maxnum']
        group_kp = request.POST['group_kp']
        group_tag = request.POST['group_tag']
        group_headimg = request.FILES.get('group_headimg')
        kp_in=False
        if type(group_kp)==type(1):
            kp = Users.objects.filter(id=group_kp)
        if type(group_kp)==type('1'):
            kp = Users.objects.filter(u_name=group_kp)
        if kp.exists():
            kp = kp.first()
            if kp.user_state != 2 and kp.user_state != 3:
                kp_in=True
                group_kp = kp.id
        if (len(group_name)>30):
            return HttpResponse('<script>alert("团名称不能超过30个字符");setTimeout(function(){history.go(-1);}, 1);</script>')
        if (len(group_password)>20):
            return HttpResponse('<script>alert("密码不能超过20个字符");setTimeout(function(){history.go(-1);}, 1);</script>')
        if ((group_state=='需要密码') and not group_password):
            return HttpResponse('<script>alert("密码团未设置密码");setTimeout(function(){history.go(-1);}, 1);</script>')
        if (not group_kp):
            return HttpResponse('<script>alert("此团未设置KP");setTimeout(function(){history.go(-1);}, 1);</script>')
        if (len(group_tag)>200):
            return HttpResponse('<script>alert("团简介不得超过200个字符");setTimeout(function(){history.go(-1);}, 1);</script>')
        if (len(group_tag)<5):
            return HttpResponse('<script>alert("团简介至少需要5个字符");setTimeout(function(){history.go(-1);}, 1);</script>')
        if not kp_in:
            return HttpResponse('<script>alert("指定的KP不存在或被封禁");setTimeout(function(){history.go(-1);}, 1);</script>')
        if (group_state=='需要密码'):
            group_state=7
        elif (group_state=='公开'):
            group_state=1
        elif (group_state=='仅邀请'):
            group_state=2
        if group_headimg: 
            if (group_headimg.size > 5000000) or not group_headimg.content_type in ['image/jpeg', 'image/png']:
            # 文件大小超过 5MB
                return HttpResponse('<script>alert("头像文件大于5MB或不为png,jpg格式");setTimeout(function(){history.go(-1);}, 1);</script>')
            group_headimg_dir = os.path.join(settings.STATICFILES_DIRS[0], 'img\\groupimg\\'+thisid)
            if not os.path.exists(group_headimg_dir):
                os.mkdir(group_headimg_dir) 
            group_groupmsg_dir = os.path.join(settings.STATICFILES_DIRS[0], 'groupdat\\groupmsg\\'+thisid)
            if not os.path.exists(group_groupmsg_dir):
                os.mkdir(group_groupmsg_dir)
            group_groupuser_dir = os.path.join(settings.STATICFILES_DIRS[0], 'groupdat\\groupuser\\'+thisid)
            if not os.path.exists(group_groupuser_dir):
                os.mkdir(group_groupuser_dir)
            filename = 'group_' + thisid + '_' + group_headimg.name
            fs = FileSystemStorage(location='static/img/groupimg/'+thisid)
            fs.save(filename, group_headimg)
            img_url='img/groupimg/'+thisid+'/'+filename
            if(group_state==7):
                group = Group(group_name=group_name, group_password=group_password, groupe_state=group_state, group_users_max_num=group_users_num, group_tag=group_tag, group_img=img_url, group_kp=group_kp)
                group.save()
                messages.success(request, '成功创建团！')
                return redirect('grouplist')
            group = Group(group_name=group_name, groupe_state=group_state, group_users_max_num=group_users_num, group_tag=group_tag, group_img=img_url, group_kp=group_kp)
            group.save()
            messages.success(request, '成功创建团！')
            return redirect('grouplist')
        if(group_state==7):
            # 创建 Group 实例并保存到数据库中
            group = Group(group_name=group_name, group_password=group_password, groupe_state=group_state, group_users_max_num=group_users_num, group_tag=group_tag, group_kp=group_kp)
            group.save()
            messages.success(request, '成功创建团！')
            return redirect('grouplist')
        group = Group(group_name=group_name,groupe_state=group_state, group_users_max_num=group_users_num, group_tag=group_tag, group_kp=group_kp)
        group.save()
        messages.success(request, '成功创建团！')
        return redirect('grouplist')