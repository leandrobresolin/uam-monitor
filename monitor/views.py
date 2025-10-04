from django.http import HttpResponse

def home(request):
    return HttpResponse("Olá, mundo! Este é meu primeiro app Django.")