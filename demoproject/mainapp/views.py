# mainapp/views.py
from django.shortcuts import get_object_or_404, redirect, render

from .forms import TestImageForm
from .models import TestImage


def index(request):
    if request.method == "POST":
        form = TestImageForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("index")
    else:
        form = TestImageForm()
    images = TestImage.objects.all()
    return render(request, "mainapp/index.html", {"form": form, "images": images})


def edit_image(request, pk):
    image = get_object_or_404(TestImage, pk=pk)
    if request.method == "POST":
        form = TestImageForm(request.POST, request.FILES, instance=image)
        if form.is_valid():
            form.save()
            return redirect("index")
    else:
        form = TestImageForm(instance=image)
    return render(request, "mainapp/edit_image.html", {"form": form, "image": image})
