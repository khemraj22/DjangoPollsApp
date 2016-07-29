from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.http import Http404
from django.shortcuts import get_object_or_404
# Create your views here.
from django.template import loader
from django.core.urlresolvers import reverse
import datetime

from .models import Choice, Question
from django.views import generic
from django.utils import timezone
from .forms import QuestionForm, ChoiceForm
from django.shortcuts import redirect

class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        #return Question.objects.order_by('-pub_date')[:5]
        return Question.objects.filter(
            pub_date__lte=timezone.now()
        ).order_by('-pub_date')[:5]

class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'

def index(request):
    latest_question_list = Question.objects.order_by('-pub_date')[:5]
    #output = ', '.join([q.question_text for q in latest_question_list])
    #return HttpResponse(output)
    #----------------
    #template = loader.get_template('polls/index.html')
    context = {
        'latest_question_list' : latest_question_list,
    }
    #return HttpResponse(template.render(context, request))
    #-----------------
    #an alternate way by using render
    return render(request,'polls/index.html', context)

def detail(request, question_id):
    #return HttpResponse("You're looking at question %s." % question_id)
    """
    try:
        question = Question.objects.get(pk=question_id)
    except Question.DoesNotExist:
        raise Http404("Question does not exist")
    return render(request, 'polls/detail.html', {'question': question})
    """
    #--------------------------
    #alternate way
    question = get_object_or_404(Question, pk= question_id)
    return render(request, 'polls/detail.html', {'question': question})


def results(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'polls/results.html', {'question': question})

def vote(request, question_id):
    #return HttpResponse("You're voting on question %s." % question_id)
    question = get_object_or_404(Question, pk= question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        return render(request, 'polls/detail.html', {'question': question, 'error_message': 'you do not select a choice',})
    else:
        selected_choice.votes += 1
        selected_choice.save()
        return HttpResponseRedirect(reverse('polls:results', args = (question.id,)))


def post_new(request):

    if request.method == "POST":
        form = QuestionForm(request.POST)
        form2 = ChoiceForm(request.POST)

        if form.is_valid() or form2.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()

            post.save()
            form2.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = QuestionForm()
        form2 = ChoiceForm()
    return render(request, 'polls/post_edit.html', {'form': form,'form2': form2})

def post_detail(request, pk):

    question = get_object_or_404(Question, pk=pk)
    return render(request, 'polls/post_edit.html', {'question': question})

def post_edit(request, pk):
    post = get_object_or_404(Question, pk=pk)
    if request.method == "POST":
        form = QuestionForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = QuestionForm(instance=post)
    return render(request, 'polls/post_edit.html', {'form': form})

