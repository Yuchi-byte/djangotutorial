from django.http import HttpResponse 

# Create your views here.
def index(request):
    # the client sends a request to the server, and the server responds. 
    return HttpResponse("Hello, world. You're at the polls index.")