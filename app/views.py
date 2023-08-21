from django.views.generic import TemplateView
import os
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from rest_framework.decorators import api_view
from django.http import JsonResponse
from .utils import *
import csv
from pathlib import Path
from django.shortcuts import render

uploaded_images = []

def index(request):
    return render(request, 'index.html')

@api_view(['POST'])
def build_model(request):
    global uploaded_images
    category = request.data.get('category')
    img_features = {}
    model_path = os.path.join(settings.BASE_DIR, 'models', category+".pkl")

    if os.path.exists(model_path):
        with open(model_path, 'rb') as f:
            img_features = pickle.load(f)
    
    for img_path in uploaded_images:
        img = process_image(img_path)
        features = extract_features(model, img)
        rel_path = str(Path(img_path).relative_to(settings.BASE_DIR))
        img_features[rel_path] = features
            # Load existing model if it exists


    with open(model_path, 'wb') as f:
        pickle.dump(img_features, f)

    merged_model_file = os.path.join(settings.BASE_DIR, 'models', "All.pkl")
    all_features = {}
    if os.path.exists(merged_model_file):
        with open(merged_model_file, 'rb') as f:
            all_features = pickle.load(f)
    else:
        all_features = {}


    all_features.update(img_features)
    with open(merged_model_file, 'wb') as f:
        pickle.dump(all_features, f) 

    return JsonResponse({"message": "success"})

@api_view(['POST'])
def search_view(request):
    # The data from the POST request are in request.data
    category = request.data.get('category')
    image = request.FILES.get('image')  # Get the uploaded image
    path = os.path.join(settings.MEDIA_ROOT, 'uploads', image.name)
    default_storage.save(path, ContentFile(image.read()))
    try:
        similar_images = fnSearch(category+".pkl", path)
        # Convert float scores to strings
        similar_images_serializable = [(img, str(score)) for img, score in similar_images]

        response_data = {
            "similar_images": similar_images_serializable
        }
        print(response_data)
        return JsonResponse(response_data)
    except:
        return JsonResponse({"message": "Failed"})

@api_view()
def get_categories(request):
    print("Hello")

    if request.method == 'GET':
        print("Hello")
        categories = []
        with open('categories.csv', 'r') as f:
            print(2)
            reader = csv.reader(f)
            for row in reader:
                categories.append(row[0])  # assuming each row has one category
        print(categories)
    return JsonResponse(categories, safe=False)
    
@api_view(['POST'])
def upload_images(request, category):
    global uploaded_images
    uploaded_images = []
    upload_files = request.FILES.getlist('files')
    for upload_file in upload_files:
        path = os.path.join(settings.MEDIA_ROOT, 'ImageSearch', 'train_datasets', category, upload_file.name)
        os.makedirs(os.path.dirname(path), exist_ok=True)  # Create parent directories if they don't exist
                # If file with same name already exists, delete it
        if default_storage.exists(path):
            default_storage.delete(path)
        default_storage.save(path, ContentFile(upload_file.read()))
        uploaded_images.append(path)
    
    return JsonResponse({"status": "success", "data": "Files uploaded successfully"})

@api_view(['POST'])
def add_category(request):
    new_category = request.data.get('category')
    print(new_category)
    with open('categories.csv', 'a') as f:  # Open file in binary mode
        writer = csv.writer(f, lineterminator='\n')  # Specify lineterminator
        writer.writerow([new_category])
    return JsonResponse({'status': 'success'}, status=200)

@api_view(['DELETE'])
def delete_category(request, categoryToDelete):
    with open('categories.csv', 'r') as file:
        rows = list(csv.reader(file))

    # Remove the item from the in-memory data structure
    updated_rows = [row for row in rows if row != [categoryToDelete]]

    # Rewrite the modified data back to the CSV file, excluding empty lines
    with open('categories.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(updated_rows)
    return JsonResponse({'status': 'success'}, status=200)
