from django.shortcuts import render
from django.http import HttpResponse


# Create your views here.

QUESTIONS = [
    {
        'id': i,
        'title': f'question {i}'
    } for i in range(10)
]

def index(request):

    return render(request, "index.html", {'questions': QUESTIONS})

def question(request, question_id):
    item = QUESTIONS[question_id]
    return render(request, "question.html")