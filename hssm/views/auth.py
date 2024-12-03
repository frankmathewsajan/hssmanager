from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as user_login, logout as user_logout


def login(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            user_login(request, user)
            print(user)
            return redirect('index')
        else:
            return render(request, "hssm/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "hssm/login.html")


def logout(request):
    user_logout(request)
    return redirect('index')
