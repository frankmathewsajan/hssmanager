from django.shortcuts import render


def home(request):
    return render(request, "hsem/cover/home.html")

def index(request):
    return render(request, "hsem/index.html") if request.user.is_authenticated else home(request)