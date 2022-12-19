from django.shortcuts import render
from fruitshop import models
from users.models import Message
# Create your views here.


def index(request):
    procucts = models.Product.objects.all()
    messages = Message.objects.all()[0:40][::-1]
    account = models.PersonalAccount.objects.first()
    print(len(messages))
    return render(request, 'fruitsshop/index.html', context={"products": procucts,
                                                             "messages": messages,
                                                             "account": account})
