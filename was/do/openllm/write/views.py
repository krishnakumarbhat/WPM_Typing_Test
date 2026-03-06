from django.shortcuts import render
from django.http import HttpResponse
from .models import store
from django.template import loader

def index(request):
    store_list = store.objects.all()
    temp = loader.get_template('words/index.html')
    context = {
        'store_list': store_list,
    }
    return HttpResponse(temp.render(context,request))


def stores(request):
    return HttpResponse('this is store ')
 
 
def detail(request,store_id):
    primek = store.objects.get(pk=store_id)
    context = {
        'primek': primek,
    }
    return HttpResponse(f"this is your id{store_id}")
