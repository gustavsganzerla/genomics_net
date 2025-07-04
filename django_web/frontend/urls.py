from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.upload_genome, name='upload_genome'),
    path('annotate_genome/<str:filename>', views.annotate_genome, name='annotate_genome'),
    path('mutation_analysis/<str:filename>', views.mutation_analysis, name='mutation_analysis'),
    path('download_annotation/<str:job_id>', views.download_annotation, name='download_annotation'),
    path('download_snps/', views.download_snps, name='download_snps')
]
