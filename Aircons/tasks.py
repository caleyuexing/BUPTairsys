from django_q.tasks import async_task
from .models import Group
from django.conf import settings
from django.utils import timezone
from Users.models import Users_possess
from datetime import datetime,timedelta
from django.db.models import Q
from django_q.models import Schedule
from django.db import transaction
import csv, os, time, random
from buptAirSys.settings import STATICFILES_DIRS

MAX_SERVICE_OBJECTS = 3

def get_default_temperature(aircon_name):

    static_dir = settings.STATICFILES_DIRS[0]
    csv_file_path = os.path.join(static_dir, 'default', 'default_temperature.csv')

    with open(csv_file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['Aircon_name'] == aircon_name:
                return row['room_current_temp']
    return '25'  # 默认温度，如果没有在 CSV 中找到

def check_waiting_groups(group_id):
    group = Group.objects.get(id=group_id)
    sleep_base = int(group.Aircon_name)
    time.sleep((sleep_base%10)*sleep_base/100)
    if not group.is_serviced:
        from django_q.tasks import schedule
        schedule('Aircons.tasks.dispatch_service',group_id,schedule_type='O')

def update_temperatures_and_costs():
    groups = Group.objects.all()
    for group in groups:
        if group.is_serviced:
            if group.room_current_temp <= group.Aircon_setting_temp:
                group.Aircon_current_wind = '0'  # Turn off the aircon
                org_setting_wind = group.Aircon_setting_wind
                group.Aircon_setting_wind = '0'
                group.is_serviced = False  # Mark as not serviced
                group.save()

                new_group = Group.objects.filter(Q(is_serviced=False) & ~Q(Aircon_setting_wind=0)).order_by('-Aircon_setting_wind', '-priority', '-wait_time').first()
                print(new_group)

                next_run_time = timezone.now() + timedelta(seconds=60)
                # Use Django-Q to schedule a task to check the temperature after some time
                from django_q.tasks import schedule
                schedule('Aircons.tasks.check_temperature', group.Aircon_name, org_setting_wind, schedule_type='O', next_run=next_run_time)
                from django_q.tasks import schedule
                schedule('Aircons.tasks.dispatch_service',new_group.id,schedule_type='O')
                continue

            model_effect = 1 if group.Aircon_setting_model == '1' else -1
            wind_effect = {'1': 0.8, '2': 1, '3': 1.2}.get(group.Aircon_current_wind, 1)
            group.room_current_temp += 0.5 * wind_effect * model_effect
            group.save()
            
            cost_per_minute = {1: 1/3, 2: 1/2, 3: 1}[int(group.Aircon_current_wind)]
            cost = cost_per_minute

            current_time = datetime.now()
            create_time = timezone.localtime(group.CreadedTime)
            user = Users_possess.objects.get(Aircon_name=group.Aircon_name)
            current_time_str = current_time.strftime('%Y%m%d%H%M%S')
            create_time_str = create_time.strftime('%Y%m%d%H%M%S')
            filename = f"{group.Aircon_name}_{user.idcard}_{create_time_str}.csv"
            filepath = os.path.join(STATICFILES_DIRS[0], 'groupdat', group.Aircon_name, filename)
            with open(filepath, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([current_time_str, cost, cost * 1])

            group.save()
            
        else:
            initial_temp = float(get_default_temperature(group.Aircon_name))

            if group.room_current_temp < initial_temp:
                group.room_current_temp += 0.5
                if group.room_current_temp > initial_temp:
                    group.room_current_temp = initial_temp

            elif group.room_current_temp > initial_temp:
                group.room_current_temp -= 0.5
                if group.room_current_temp < initial_temp:
                    group.room_current_temp = initial_temp

            group.save()

def check_temperature(group_Aircon_name,org_setting_wind):
    group = Group.objects.get(Aircon_name=group_Aircon_name)
    if group.room_current_temp >= group.Aircon_setting_temp + 1:
        group.Aircon_setting_wind = org_setting_wind
        group.save()
        from django_q.tasks import schedule
        schedule('Aircons.tasks.dispatch_service',group.id,schedule_type='O')
    else:
        next_run_time = timezone.now() + timedelta(seconds=60)
        from django_q.tasks import schedule
        schedule('Aircons.tasks.check_temperature', group.Aircon_name, org_setting_wind, schedule_type='O', next_run=next_run_time)

def ensure_task_scheduled(task_name, func, schedule_type, **kwargs):

    if not Schedule.objects.filter(name=task_name).exists():
        from django_q.tasks import schedule
        schedule(func, name=task_name, schedule_type=schedule_type, **kwargs)

def dispatch_service(group_id):
    group = Group.objects.get(id=group_id)
    sleep_base = int(group.Aircon_name)
    time.sleep((sleep_base%10)*sleep_base/100)
    # 确保定时任务被调度
    ensure_task_scheduled('update_temperatures_and_costs', 'Aircons.tasks.update_temperatures_and_costs', 'I', minutes=1)
    serviced_groups = Group.objects.filter(is_serviced=True).order_by('-wait_time')

    if len(serviced_groups) < MAX_SERVICE_OBJECTS:
        update_wind = group.Aircon_setting_wind
        group.is_serviced = True
        group.wait_time = 0
        group.priority = 0
        group.Aircon_current_wind = update_wind
        group.save()
    else:
        from django_q.tasks import schedule
        schedule('Aircons.tasks.handle_scheduling', group_id, schedule_type='O')

def handle_scheduling(group_id):
    group = Group.objects.get(id=group_id)
    serviced_groups = Group.objects.filter(is_serviced=True).order_by('-wait_time')
    max_serviced_group = max(serviced_groups, key=lambda x: x.Aircon_current_wind)
    if group.Aircon_setting_wind > max_serviced_group.Aircon_current_wind:
        low_wind_groups = [g for g in serviced_groups if g.Aircon_current_wind < group.Aircon_setting_wind]
        if low_wind_groups:
            if len(low_wind_groups) == 1:
                from django_q.tasks import schedule
                schedule('Aircons.tasks.release_and_wait', low_wind_groups[0].id, group.id, schedule_type='O')
            else:
                max_wait_group = max(low_wind_groups, key=lambda x: x.wait_time)
                from django_q.tasks import schedule
                schedule('Aircons.tasks.release_and_wait', max_wait_group.id, group.id, schedule_type='O')
        else:
            min_wind_group = min(serviced_groups, key=lambda x: x.Aircon_current_wind)
            from django_q.tasks import schedule
            schedule('Aircons.tasks.release_and_wait', min_wind_group.id, group.id, schedule_type='O')
    else:
        group.wait_time += 120
        group.priority += 1
        group.save()
        next_run_time = timezone.now() + timedelta(seconds=120)
        from django_q.tasks import schedule
        schedule('Aircons.tasks.check_waiting_groups', group.id, schedule_type='O', next_run=next_run_time)

def release_and_wait(serviced_group, new_group):
    serviced_group.is_serviced = False
    serviced_group.save()
    next_run_time = timezone.now() + timedelta(seconds=60)
    # Use Django-Q to schedule a task for checking after WAIT_TIME seconds
    from django_q.tasks import schedule
    schedule('Aircons.tasks.dispatch_service',new_group.id,schedule_type='O')
    schedule('Aircons.tasks.check_waiting_groups', serviced_group.id, schedule_type='O', next_run=next_run_time)