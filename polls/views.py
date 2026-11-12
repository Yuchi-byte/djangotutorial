from django.db.models import F
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse 
from .models import Question, Choice
from django.views import generic
from django.utils import timezone

class IndexView(generic.ListView):
    template_name = "polls/index.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        return Question.objects.filter(pub_date__lte=timezone.now()).order_by("-pub_date")[:5]

class DetailView(generic.DetailView):
    model = Question
    template_name = "polls/detail.html"
    def get_queryset(self):
        return Question.objects.filter(pub_date__lte=timezone.now())

class ResultsView(generic.DetailView):
    model = Question
    template_name = "polls/results.html"
    
def vote(request, question_id): 
    question = get_object_or_404(Question, pk=question_id)
    try: 
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form. 
        return render(request, "polls/detail.html", 
                      {
                          "question": question, 
                          "error_message": "You didn't select a choice."
                      }
                      )
    else: 
        selected_choice.votes = F("votes") + 1
        selected_choice.save() 
        # Always return an HttpResponseRedirect after successfully dealing with POST data. 
        # This prevents data from being posted twice if a user hits the Back button. 
        # Without redirecting, you are just doing HttpResponse(request, "polls/1/result", context). 
        # This has a history of [GET /polls/1, POST /polls/1/vote]. With redirect, the history is [GET /polls/1, GET /polls/1/results/]
        # So with redirect, no matter how the user goes back and forth and refreshes, they won't be able to vote again unintentionally.
        # This pattern is called Post/Redirect/Get (PRG)
        # A POST shouldn't directly produce a page the user can land on. Instead, a POST should redirect to a GET page. 
        return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))
        # reverse takes the name of a URL pattern and retuns the path. So this returns "/polls/1/results"
        # Recall the path to the results page is: path("<int:question_id>/results/", views.results, name="results"),
        # polls:results is the namespaced URL name. 

# What happens when the user submits a choice, step by step. 
# <form action="/polls/1/vote/" method="post">. Note that 1 is the question.id. 

# The user clicks submit. 
# The broswer has the html, and it looks at every input inside the form and identified that choice=3 is chosen. 
# The browser works out where to send it: current page's server address + relative path in the action. 
# The browser builds the HTTP request by assembling a text message. 
# The browser opens a network connection to the server (my own computer) and sends that text. 
# The server reads the raw text and Django turns it into a Python object called request. 
# After some checks, Django takes the path 'polls/1/vote' and walks through the URL patterns. And the pattern points to views.vote. 
# Django calls vote(request, question_id=1)
# The view looks up question number 1. 
# The view reads the chosen option: selected_choice = question.choice_set.get(pk=request.POST["choice"]). selected_choice is the third choice. 
# The view records the vote: selected_choice.votes = F("votes") + 1
# The view returns a HttpResponseRedirect(reverse("polls:results", args=(question.id))). Basically, the view sends a short response (not a web page). redirecting to polls/1/results
# The browser reads the redict message, and sends a new GET request. GET /polls/1/results/ HTTP/1.1
# Django matches /polls/1/results/ to views.results. 
# The view loads question 1 from database, renders results.html, and sends back a normal response contianing that HTML. Note that request can have methods (POST or GET), but responses don't have methods. 
# the browser displays the new HTML. 
