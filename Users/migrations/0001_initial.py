# Generated by Django 4.2.2 on 2024-05-28 10:33

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Users',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('u_name', models.CharField(max_length=12)),
                ('u_password', models.CharField(max_length=255)),
                ('u_ticket', models.CharField(max_length=30, null=True)),
                ('headimg', models.TextField(default='img/headimg/default.jpg', max_length=255)),
                ('user_dat', models.CharField(default='userdat/', max_length=255)),
                ('registerTime', models.DateTimeField(auto_now_add=True)),
                ('tel', models.CharField(default='null', max_length=16)),
                ('email', models.CharField(default='null', max_length=255)),
                ('user_state', models.CharField(default='1', max_length=5)),
                ('user_tel_state', models.CharField(default='0', max_length=1)),
                ('user_email_state', models.CharField(default='0', max_length=1)),
            ],
            options={
                'db_table': 'Users_info',
            },
        ),
    ]
