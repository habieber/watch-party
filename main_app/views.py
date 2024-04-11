from django.forms import BaseModelForm
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
import requests
from django.http import HttpResponse
from django.http.response import JsonResponse
from .models import Movie, Show
from .forms import MovieReviewForm, ShowReviewForm

TMDB_API_KEY = '52c430a98c74ec9e45c65e972962aa7b'
TMDB_API_TOKEN = 'eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI1MmM0MzBhOThjNzRlYzllNDVjNjVlOTcyOTYyYWE3YiIsInN1YiI6IjY2MGVmYmY0YTg4NTg3MDE3Y2VhMjVlNiIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.eNL5Z05d61tQZ1TXUoccaKXxrm3_Nu5IIrme8q4So8Y'
headers = {
    "accept": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI1MmM0MzBhOThjNzRlYzllNDVjNjVlOTcyOTYyYWE3YiIsInN1YiI6IjY2MGVmYmY0YTg4NTg3MDE3Y2VhMjVlNiIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.eNL5Z05d61tQZ1TXUoccaKXxrm3_Nu5IIrme8q4So8Y"
}

# Create your views here.
def home(request):
   return render(request, 'home.html')

def search(request):
    query = request.GET.get('q')
    print(query)

    if query:

        data = requests.get(f"https://api.themoviedb.org/3/search/{request.GET.get('type')}?query={query}&include_adult=false&language=en-US&page=1", headers=headers)
        print(f'search {data.json()}')
    else:
        return render(request, 'all_media.html', {
           'title': 'Available Media'
        })

    return render(request, 'all_media.html', {
        "data": data.json(),
        "type": request.GET.get("type"),
        "title": f'Results for {query}'
    })

def view_trendings_results(request):
    type = request.GET.get("media_type")
    time_window = request.GET.get("time_window")

    trendings = requests.get(f"https://api.themoviedb.org/3/trending/{type}/{time_window}?api_key={TMDB_API_KEY}&language=en-US")
    return JsonResponse(trendings.json())

def about(request):
   return render(request, 'about.html')

# def shows_index(request):
#    return render(request, 'all_tv_shows.html')

def movies_index(request):
   return render(request, 'all_movies.html')

def party_index(request):
   movies = Movie.objects.all()
   shows = Show.objects.all()
   return render(request, 'party/index.html', {
      'movies': movies,
      'shows': shows
   })

def my_profile(request):
   return render(request, 'my_profile.html')

def save_tv_show(request, tv_id):
   movies = Movie.objects.all()
   shows = Show.objects.all()

   data = requests.get(f"https://api.themoviedb.org/3/tv/{tv_id}?api_key={TMDB_API_KEY}&language=en-US")
   show = data.json()
   m = Show.objects.create(
      title=show['name'], 
      genre=show['genres'][0]['name'], 
      season=show['number_of_seasons'],
      description=show['overview'],
      poster=show['poster_path'],
      progress='Not Started',
      user=request.user
   )
   m.save()

   return render(request, 'party/index.html', {
      'movies': movies,
      'shows': shows,
      'data': data.json(),
      'type': 'tv'
   })

def show_detail(request, show_id):
   show = Show.objects.get(id=show_id)
   review_form = ShowReviewForm()
   return render(request, 'shows/detail.html', {
      'title': f'{show}',
      'show': show,
      'review_form': review_form
   })

class ShowDelete(LoginRequiredMixin, DeleteView):
  model = Show
  success_url = '/media/party'

def save_movie(request, movie_id):
   movies = Movie.objects.all()
   shows = Show.objects.all()

   data = requests.get(f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US")
   movie = data.json()
   print(f'this is {data.json()['title']}')
   m = Movie.objects.create(
      title=movie['title'], 
      genre=movie['genres'][0]['name'], 
      description=movie['overview'], 
      poster=movie['poster_path'],
      progress='Not Started',
      user=request.user
   )
   m.save()

   return render(request, 'party/index.html', {
      'movies': movies,
      'shows': shows,
      'data': data.json(),
      'type': 'movie'
   })

def movie_detail(request, movie_id):
   movie = Movie.objects.get(id=movie_id)
   review_form = MovieReviewForm()
   return render(request, 'movies/detail.html', {
      'title': f'{movie}',
      'movie': movie,
      'review_form': review_form
   })

class MovieDelete(LoginRequiredMixin, DeleteView):
  model = Movie
  success_url = '/media/party'

def add_movie_review(request, movie_id):
   form = MovieReviewForm(request.POST)
   if form.is_valid():
      new_review = form.save(commit=False)
      new_review.movie_id = movie_id
      new_review.save()
   return redirect('movie_detail', movie_id=movie_id)

def add_show_review(request, show_id):
   form = ShowReviewForm(request.POST)
   if form.is_valid():
      new_review = form.save(commit=False)
      new_review.show_id = show_id
      new_review.save()
   return redirect('show_detail', show_id=show_id)

class MovieCreate(CreateView):
    model = Movie

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
    

class ShowCreate(CreateView):
    model = Show

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
    

def signup(request):
  error_message = ''
  if request.method == 'POST':
    # This is how to create a 'user' form object
    # that includes the data from the browser
    form = UserCreationForm(request.POST)
    if form.is_valid():
      # This will add the user to the database
      user = form.save()
      # This is how we log a user in via code
      login(request, user)
      return redirect('/')
    # replace '/' with /index
    else:
      error_message = 'Invalid sign up - try again'
  # A bad POST or a GET request, so render signup.html with an empty form
  form = UserCreationForm()
  context = {'form': form, 'error_message': error_message}
  return render(request, 'registration/signup.html', context)
