from django.shortcuts import render
from fruitshop import models
# Create your views here.


def index(request):
    procucts = models.Product.objects.all()
    return render(request, 'fruitsshop/index.html', context={"products": procucts})
