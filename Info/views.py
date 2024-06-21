from django.shortcuts import render
from Users.models import Users, Users_possess
from django.http import HttpResponse
from Aircons.models import Group
import csv,os
from datetime import datetime
from django.utils import timezone
from buptAirSys.settings import STATICFILES_DIRS


# Create your views here.
def billInfo(request, Aircon_name):
    if request.method == 'GET':
        ret = request.COOKIES.get('ticket')
        if not Users.objects.filter(u_ticket=ret).exists() or not ret:
            return render(request, 'register.html')
        else:
            usages = []
            userInfo = Users.objects.get(u_ticket=ret)
            if userInfo.user_state == '2' or userInfo.user_state == '0':
                group=Group.objects.get(Aircon_name=Aircon_name)
                create_time = timezone.localtime(group.CreadedTime)
                user = Users_possess.objects.get(Aircon_name=group.Aircon_name)
                create_time_str = create_time.strftime('%Y%m%d%H%M%S')
                filename = f"{group.Aircon_name}_{user.idcard}_{create_time_str}.csv"
                filepath = os.path.join(STATICFILES_DIRS[0], 'groupdat', group.Aircon_name, filename)
                with open(filepath, newline='', encoding='utf-8') as csvfile:
                    reader = csv.reader(csvfile)
                    # 跳过头部
                    next(reader)
                    for row in reader:
                        usage_value = float(row[1])
                        if usage_value == 0.5:
                            wind_speed = '中风'
                        elif usage_value == 0.6:
                            wind_speed = '高风'
                        elif usage_value == 0.4:
                            wind_speed = '低风'
                        usages.append({
                            'timestamp': row[0],
                            'usage': row[1],
                            'cost': row[2],         
                            'wind_speed': wind_speed
                        })
                airconInfo = Group.objects.get(Aircon_name=Aircon_name)
                processInfo = Users_possess.objects.get(Aircon_name=Aircon_name)
                usages.reverse()
                return render(request, 'billInfo.html', {
                        'userInfo':userInfo, 
                        'airconInfo':airconInfo, 
                        'processInfo':processInfo, 
                        'usages': usages,
                    })
                
            elif userInfo.user_state == '1':
                airconInfo = Group.objects.get(Aircon_name=Aircon_name)
                processInfo = Users_possess.objects.get(Aircon_name=Aircon_name)
                isUserProcess = Users_possess.objects.filter(idcard=userInfo.idcard,Aircon_name=Aircon_name).exists()
                if not isUserProcess:
                    return HttpResponse('<script>alert("你不是该房间的客户");setTimeout(function(){history.go(-1);}, 1);</script>')
                else:
                    group=Group.objects.get(Aircon_name=Aircon_name)
                    create_time = timezone.localtime(group.CreadedTime)
                    user = Users_possess.objects.get(Aircon_name=group.Aircon_name)
                    create_time_str = create_time.strftime('%Y%m%d%H%M%S')
                    filename = f"{group.Aircon_name}_{user.idcard}_{create_time_str}.csv"
                    filepath = os.path.join(STATICFILES_DIRS[0], 'groupdat', group.Aircon_name, filename)
                    with open(filepath, newline='', encoding='utf-8') as csvfile:
                        reader = csv.reader(csvfile)
                        # 跳过头部
                        next(reader)
                        for row in reader:
                            usage_value = float(row[1])
                            if usage_value == 0.5:
                                wind_speed = '中风'
                            elif usage_value == 0.6:
                                wind_speed = '高风'
                            elif usage_value == 0.4:
                                wind_speed = '低风'
                            usages.append({
                                'timestamp': row[0],
                                'usage': row[1],
                                'cost': row[2],         
                                'wind_speed': wind_speed
                            })
                    usages.reverse()
                    return render(request, 'billInfo.html', {
                        'userInfo':userInfo, 
                        'airconInfo':airconInfo, 
                        'processInfo':processInfo, 
                        'usages': usages,
                    })
            else:
                return HttpResponse('<script>alert("您没有访问的权限");setTimeout(function(){history.go(-1);}, 1);</script>')
