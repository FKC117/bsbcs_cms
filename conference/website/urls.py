from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('about/', views.about, name='about'),
    path('knowledge-center/', views.knowledge_center, name='knowledge_center'),
    path('member-directory/', views.member_directory, name='member_directory'),
    # Expose events at /events/ and use URL name 'events'
    path('events/', views.events, name='events'),
    path('research-and-publications/', views.research_and_publications, name='research_and_publications'),
    path('webinars/', views.webinars, name='webinars'),
    path('webinars/<int:pk>/', views.webinar_detail, name='webinar_detail'),
    path('favicon.ico', views.favicon),
]