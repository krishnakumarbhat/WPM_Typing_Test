from . import views
from django.urls import path,include

app_name = ' write '

urlpatterns = [

    path('',views.index ,name = 'index'),
    path('<int:store_id>/',views.detail , name= "detail"),
    path('stores/' , views.stores ,name='stores'),
]
