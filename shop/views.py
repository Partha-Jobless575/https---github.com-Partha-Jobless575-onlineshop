
from django.shortcuts import render
from .models import Product,Contact,OrderUpdate,Orders
from math import ceil
import json
from django.http import HttpResponse 

# index control function.
def index(request): 
   allProducts = []
   catproducts = Product.objects.values('category', 'id')
   category = {item['category'] for item in catproducts}
   for c in category:
      prod = Product.objects.filter(category=c)
      n = len(prod)
      Slides = n // 4 + ceil((n / 4) - (n // 4))
      allProducts.append([prod, range(1, Slides), Slides])
   params = {'allProds':allProducts}
   return render(request, 'shop/index.html', params)
   

#about conntrol function.
def about(request):
   return render(request, 'shop/about.html')


#contact control function.
def contact(request):  
   if request.method=="POST":
      name = request.POST.get('name', '')
      email = request.POST.get('email', '')
      phone = request.POST.get('phone', '')
      desc = request.POST.get('desc', '')
      contact = Contact(name=name, email=email, phone=phone, desc=desc)
      contact.save()
   return render(request, 'shop/contact.html') 


#checkout controll function.
def checkout(request): 
   id=0 
   thank=False
   if request.method=="POST":
      items_json = request.POST.get('itemsJson', '')
      name = request.POST.get('name', '')
      amount = request.POST.get('amount', '')
      email = request.POST.get('email', '')
      address = request.POST.get('address1', '') + " " + request.POST.get('address2', '')
      city = request.POST.get('city', '')
      state = request.POST.get('state', '')
      zip_code = request.POST.get('zip_code', '')
      phone = request.POST.get('phone', '')
      order = Orders(items_json=items_json, name=name, email=email, address=address, city=city,
                       state=state, zip_code=zip_code, phone=phone, amount=amount)
      order.save()
      update = OrderUpdate(order_id=order.order_id, update_desc="The order has been placed")
      update.save() 
      thank=True
      id = order.order_id
   return render(request, 'shop/checkout.html', {'thank':thank,'id': id})


# search control function.


def searchMatch(query, item):
   '''return true only if query matches the item'''
   if query in item.desc.lower() or query in item.product_name.lower() or query in item.category.lower():
      return True
   else:
      return False
 
def search(request):
   query = request.GET.get('search')
   allProducts = []
   catprods = Product.objects.values('category', 'id')
   cats = {item['category'] for item in catprods}
   for cat in cats:
      prodtemp = Product.objects.filter(category=cat)
      prod = [item for item in prodtemp if searchMatch(query, item)]

      n = len(prod)
      Slides = n // 4 + ceil((n / 4) - (n // 4))
      if len(prod) != 0:
         allProducts.append([prod, range(1, Slides), Slides])
   params = {'allProds': allProducts, "msg": ""}
   if len(allProducts) == 0 or len(query)<4:
      params = {'msg': "Please make sure to enter relevant search query"}
   return render(request, 'shop/search.html', params)  



#tracker control function


def tracker(request): 
   if request.method=="POST":
      orderId = request.POST.get('orderId', '')
      email = request.POST.get('email', '')
      try:
         order = Orders.objects.filter(order_id=orderId, email=email)
         if len(order)>0:
            update = OrderUpdate.objects.filter(order_id=orderId)
            updates = []
            for item in update:
               updates.append({'text': item.update_desc, 'time': item.timestamp})
               response = json.dumps({"status":"success", "updates": updates, "itemsJson": order[0].items_json}, default=str)
            return HttpResponse(response)
         else:
            return HttpResponse('{"status":"noitem"}')
      except Exception as e:
          HttpResponse('{"status":"error"}')

   return render(request, 'shop/tracker.html')

