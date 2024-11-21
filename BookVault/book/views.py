from django.shortcuts import render

# Create your views here.
def genre(request):
    return render(request, 'client/index.html')