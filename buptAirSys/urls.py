"""
URL configuration for buptAirSys project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from Users.views import index,register,login
from Aircons.views import airconlist,creatOrder,changesetting,stopOrder,changeCenter
from Info.views import billInfo
from django.views.generic.base import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',index,name='index'),
    path('register/',register,name='register'),
    path('airconlist/',airconlist,name='airconlist'),
    path('login/',login,name='login'),
    path('creatOrder/',creatOrder,name='creatOrder'),
    path('changeCenter/',changeCenter,name='changeCenter'),
    path('changesetting/<int:Aircon_name>', changesetting, name='changesetting'),
    path('stopOrder/<int:Aircon_name>', stopOrder, name='stopOrder'),
    path('billInfo/<int:Aircon_name>', billInfo, name='billInfo'),
    path('favicon.ico', RedirectView.as_view(url='/static/img/favicon.ico', permanent=True)),
]
