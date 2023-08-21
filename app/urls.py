from django.urls import path, include, re_path
from .views import *
urlpatterns = [
    path('', index),
    path('api/search', search_view, name='search'),
    path('api/build_model', build_model, name='build'),

    path('api/categories', get_categories, name='get_categories'),
    path('api/addCategory', add_category, name='add_category'),
    path('api/deleteCategory/<str:categoryToDelete>/', delete_category),
    path('api/upload/<str:category>/', upload_images),

]
