from django.shortcuts import render,HttpResponseRedirect
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.mail import send_mail
from essence.settings import RAZORPAY_API_KEY,RAZORPAY_API_SECRET_KEY
import razorpay

from random import randint

from .models import *
def homePage(Request):
    data = Product.objects.all()
    data = data[::-1]
    data = data[0:10]
    brand = Brand.objects.all()
    subcategory = Subcategory.objects.all()
    maincategory = Maincategory.objects.all()
    return render(Request,"index.html",{'data':data,'brand':brand,'subcategory':subcategory,'maincategory':maincategory})

@login_required(login_url="/login/")
def checkoutPage(Request):
    user = User.objects.get(username=Request.user.username)
    if(user.is_superuser):
        return HttpResponseRedirect("/admin/")
    else:
        buyer = Buyer.objects.get(username=Request.user.username)
    total = Request.session.get("total",0)
    if(total==0):
        return HttpResponseRedirect("/cart/")
    brand = Brand.objects.all()
    subcategory = Subcategory.objects.all()
    maincategory = Maincategory.objects.all()
    return render(Request,"checkout.html",{'data':buyer,'maincategory':maincategory,'subcategory':subcategory,'brand':brand})

client = razorpay.Client(auth=(RAZORPAY_API_KEY,RAZORPAY_API_SECRET_KEY))
@login_required(login_url="/login/")
def placeOrderPage(Request):
    user = User.objects.get(username=Request.user.username)
    if(user.is_superuser):
        return HttpResponseRedirect("/admin/")
    else:
        total = Request.session.get("total",0)
        if(total):
            shipping = Request.session.get("shipping",0)
            final = Request.session.get("final",0)
            
            buyer = Buyer.objects.get(username=Request.user.username)
            checkout = Checkout()
            checkout.user = buyer
            checkout.totalAmount = total
            checkout.shippingAmount = shipping
            checkout.finalAmount = final
            checkout.save()

            cart = Request.session.get("cart")
            for key,value in cart.items():
                checkoutProduct = CheckoutProducts()
                checkoutProduct.checkout = checkout
                checkoutProduct.pid = int(key)
                checkoutProduct.name = value['name']
                checkoutProduct.color = value['color']
                checkoutProduct.size = value['size']
                checkoutProduct.price = value['price']
                checkoutProduct.qty = value['qty']
                checkoutProduct.total = value['total']
                checkoutProduct.pic = value['pic']
                checkoutProduct.save()
            Request.session['cart']={}
            Request.session['total']=0
            Request.session['shipping']=0
            Request.session['final']=0
            Request.session['cartCount']=0

            mode = Request.POST.get("mode")
            if(mode=="COD"):
                return HttpResponseRedirect("/confirmation")
            else:
                orderAmount = checkout.finalAmount*100
                orderCurrency = "INR"
                paymentOrder = client.order.create(dict(amount=orderAmount,currency=orderCurrency,payment_capture=1))
                paymentId = paymentOrder['id']
                checkout.paymentMode="Net Banking"
                checkout.save()
                return render(Request,"pay.html",{
                    "amount":orderAmount,
                    "api_key":RAZORPAY_API_KEY,
                    "order_id":paymentId,
                    "User":buyer
                })
        else:
            return HttpResponseRedirect("/cart/")


@login_required(login_url='/login/')
def paymentSuccess(request,rppid,rpoid,rpsid):
    buyer = Buyer.objects.get(username=request.user)
    check = Checkout.objects.filter(buyer=buyer)
    check=check[::-1]
    check=check[0]
    check.rppid=rppid
    check.paymentStatus=1
    check.save()
    return HttpResponseRedirect('/confirmation/')


@login_required(login_url="/login/")
def confirmationPage(Request):
    username=Request.user.username
    if(username):
        try:
            buyer = Buyer.objects.get(username=username)
            subject = 'Order Has Been Placed- Team Essence'
            message = "Thank to Shop With US!!! Your Order Has Been Placed!!! Now You Can Track Your Order in Profile Section"
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [buyer.email, ]
            send_mail( subject, message, email_from, recipient_list )
            brand = Brand.objects.all()
            subcategory = Subcategory.objects.all()
            maincategory = Maincategory.objects.all()
            return render(Request,"confirmation.html",{'maincategory':maincategory,'subcategory':subcategory,'brand':brand})
        except: 
            return HttpResponseRedirect("/shop/All/All/All")
    else:
        return HttpResponseRedirect("/shop/All/All/All")


def contactPage(Request):
    if(Request.method=="POST"):
        c = ContactUs()
        c.name = Request.POST.get("name")
        c.email = Request.POST.get("email")
        c.phone = Request.POST.get("phone")
        c.subject = Request.POST.get("subject")
        c.message = Request.POST.get("message")
        c.save()
        messages.success(Request,"Thanks to Share Your Query With Us. Our Team Will Contact You Soon!!!")
    brand = Brand.objects.all()
    subcategory = Subcategory.objects.all()
    maincategory = Maincategory.objects.all()
    return render(Request,"contact.html",{'brand':brand,'maincategory':maincategory,'subcategory':subcategory})

def shopPage(Request,mc,sc,br):
    if(mc=="All" and sc=="All" and br=="All"):
        data = Product.objects.all()
    elif(mc!="All" and sc=="All" and br=="All"):
        data = Product.objects.filter(maincategory=Maincategory.objects.get(name=mc))
    elif(mc=="All" and sc!="All" and br=="All"):
        data = Product.objects.filter(subcategory=Subcategory.objects.get(name=sc))
    elif(mc=="All" and sc=="All" and br!="All"):
        data = Product.objects.filter(brand=Brand.objects.get(name=br))
    elif(mc!="All" and sc!="All" and br=="All"):
        data = Product.objects.filter(maincategory=Maincategory.objects.get(name=mc),subcategory=Subcategory.objects.get(name=sc))
    elif(mc!="All" and sc=="All" and br!="All"):
        data = Product.objects.filter(maincategory=Maincategory.objects.get(name=mc),brand=Brand.objects.get(name=br))
    elif(mc=="All" and sc!="All" and br!="All"):
        data = Product.objects.filter(brand=Brand.objects.get(name=br),subcategory=Subcategory.objects.get(name=sc))
    else:
        data = Product.objects.filter(maincategory=Maincategory.objects.get(name=mc),brand=Brand.objects.get(name=br),subcategory=Subcategory.objects.get(name=sc))
    count = len(data)
    data = data[::-1]
    maincategory = Maincategory.objects.all()
    subcategory = Subcategory.objects.all()
    brand = Brand.objects.all()
    return render(Request,"shop.html",{'data':data,'maincategory':maincategory,'subcategory':subcategory,'brand':brand,'mc':mc,'sc':sc,'br':br,'count':count})

def priceFilterPage(Request,mc,sc,br):
    if(Request.method=="POST"):
        min = Request.POST.get("min")
        max = Request.POST.get("max")
        if(mc=="All" and sc=="All" and br=="All"):
            data = Product.objects.filter(finalprice__gte=min,finalprice__lte=max)
        elif(mc!="All" and sc=="All" and br=="All"):
            data = Product.objects.filter(finalprice__gte=min,finalprice__lte=max,maincategory=Maincategory.objects.get(name=mc))
        elif(mc=="All" and sc!="All" and br=="All"):
            data = Product.objects.filter(finalprice__gte=min,finalprice__lte=max,subcategory=Subcategory.objects.get(name=sc))
        elif(mc=="All" and sc=="All" and br!="All"):
            data = Product.objects.filter(finalprice__gte=min,finalprice__lte=max,brand=Brand.objects.get(name=br))
        elif(mc!="All" and sc!="All" and br=="All"):
            data = Product.objects.filter(finalprice__gte=min,finalprice__lte=max,maincategory=Maincategory.objects.get(name=mc),subcategory=Subcategory.objects.get(name=sc))
        elif(mc!="All" and sc=="All" and br!="All"):
            data = Product.objects.filter(finalprice__gte=min,finalprice__lte=max,maincategory=Maincategory.objects.get(name=mc),brand=Brand.objects.get(name=br))
        elif(mc=="All" and sc!="All" and br!="All"):
            data = Product.objects.filter(finalprice__gte=min,finalprice__lte=max,brand=Brand.objects.get(name=br),subcategory=Subcategory.objects.get(name=sc))
        else:
            data = Product.objects.filter(finalprice__gte=min,finalprice__lte=max,maincategory=Maincategory.objects.get(name=mc),brand=Brand.objects.get(name=br),subcategory=Subcategory.objects.get(name=sc))
        # data = Product.objects.filter(finalprice__gte=min,finalprice__lte=max)
        count = len(data)
        data = data[::-1]
        maincategory = Maincategory.objects.all()
        subcategory = Subcategory.objects.all()
        brand = Brand.objects.all()
        return render(Request,"shop.html",{'data':data,'maincategory':maincategory,'subcategory':subcategory,'brand':brand,'mc':mc,'sc':sc,'br':br,'count':count})
    else:
        return HttpResponseRedirect("/shop/All/All/All")

def sortFilterPage(Request,mc,sc,br):
    if(Request.method=="POST"):
        sort = Request.POST.get("sort")
        if(sort=="Newest"):
            sort="id"
        elif(sort=="LTOH"):
            sort="-finalprice"
        else:
            sort="finalprice"
        if(mc=="All" and sc=="All" and br=="All"):
            data = Product.objects.all().order_by(sort)
        elif(mc!="All" and sc=="All" and br=="All"):
            data = Product.objects.filter(maincategory=Maincategory.objects.get(name=mc)).order_by(sort)
        elif(mc=="All" and sc!="All" and br=="All"):
            data = Product.objects.filter(subcategory=Subcategory.objects.get(name=sc)).order_by(sort)
        elif(mc=="All" and sc=="All" and br!="All"):
            data = Product.objects.filter(brand=Brand.objects.get(name=br)).order_by(sort)
        elif(mc!="All" and sc!="All" and br=="All"):
            data = Product.objects.filter(maincategory=Maincategory.objects.get(name=mc),subcategory=Subcategory.objects.get(name=sc)).order_by(sort)
        elif(mc!="All" and sc=="All" and br!="All"):
            data = Product.objects.filter(maincategory=Maincategory.objects.get(name=mc),brand=Brand.objects.get(name=br)).order_by(sort)
        elif(mc=="All" and sc!="All" and br!="All"):
            data = Product.objects.filter(brand=Brand.objects.get(name=br),subcategory=Subcategory.objects.get(name=sc)).order_by(sort)
        else:
            data = Product.objects.filter(maincategory=Maincategory.objects.get(name=mc),brand=Brand.objects.get(name=br),subcategory=Subcategory.objects.get(name=sc)).order_by(sort)
        # data = Product.objects.filter(finalprice__gte=min,finalprice__lte=max)
        count = len(data)
        data = data[::-1]
        maincategory = Maincategory.objects.all()
        subcategory = Subcategory.objects.all()
        brand = Brand.objects.all()
        return render(Request,"shop.html",{'data':data,'maincategory':maincategory,'subcategory':subcategory,'brand':brand,'mc':mc,'sc':sc,'br':br,'count':count})
    else:
        return HttpResponseRedirect("/shop/All/All/All")

def searchPage(Request):
    if(Request.method=="POST"):
        search = Request.POST.get("search")
        data = Product.objects.filter(Q(name__icontains=search)|Q(color__icontains=search)|Q(size__icontains=search)|Q(description__icontains=search))
        maincategory = Maincategory.objects.all()
        subcategory = Subcategory.objects.all()
        brand = Brand.objects.all()
        count = len(data)
        return render(Request,"shop.html",{'data':data,'maincategory':maincategory,'subcategory':subcategory,'brand':brand,'mc':'All','sc':'All','br':'All','count':count})
    else:
        return HttpResponseRedirect("/shop/All/All/All")

def singleProductPage(Request,num):
    data = Product.objects.get(id=num)
    brand = Brand.objects.all()
    subcategory = Subcategory.objects.all()
    maincategory = Maincategory.objects.all()
    return render(Request,"single-product.html",{'data':data,'maincategory':maincategory,'subcategory':subcategory,'brand':brand})


def loginPage(Request):
    if(Request.method=='POST'):
        username = Request.POST.get("username")
        password = Request.POST.get("password")
        user = authenticate(username=username,password=password)
        if(user is not None):
            login(Request,user)
            if(user.is_superuser):
                return HttpResponseRedirect("/admin")
            else:
                return HttpResponseRedirect("/profile")
        else:
            messages.error(Request,"Invalid Username or Password!!!!")
    brand = Brand.objects.all()
    subcategory = Subcategory.objects.all()
    maincategory = Maincategory.objects.all()
    return render(Request,"login.html",{'maincategory':maincategory,'subcategory':subcategory,'brand':brand})

def signupPage(Request):
    if(Request.method=="POST"):
        name = Request.POST.get("name")
        username = Request.POST.get("username")
        email = Request.POST.get("email")
        phone = Request.POST.get("phone")
        password = Request.POST.get("password")
        cpassword = Request.POST.get("cpassword")
        if(password==cpassword):
            try:
                user = User(username=username)
                user.set_password(password)
                user.save()
                buyer = Buyer()
                buyer.name = name
                buyer.username = username
                buyer.email = email
                buyer.phone = phone
                buyer.password = password
                buyer.save()
                subject = 'Account is Created- Team Essence'
                message = "Thanks to Create an Account With US!!! Now You can buy our latest and awesome products"
                email_from = settings.EMAIL_HOST_USER
                recipient_list = [buyer.email, ]
                send_mail( subject, message, email_from, recipient_list )
                return HttpResponseRedirect("/login")
            except:
                messages.error(Request,"User Name Already Exist!!!")                
        else:
            messages.error(Request,"Password and Confirm Password Doesn't Matched!!!")
    brand = Brand.objects.all()
    subcategory = Subcategory.objects.all()
    maincategory = Maincategory.objects.all()
    return render(Request,"signup.html",{'maincategory':maincategory,'subcategory':subcategory,'brand':brand})

def logoutPage(Request):
    logout(Request)
    return HttpResponseRedirect("/login/")

@login_required(login_url="/login/")
def profilePage(Request):
    user = User.objects.get(username=Request.user.username)
    if(user.is_superuser):
        return HttpResponseRedirect("/admin/")
    else:
        buyer = Buyer.objects.get(username=Request.user.username)
        wishlist = Wishlist.objects.filter(user=buyer)
        orders = []
        checkouts = Checkout.objects.filter(user=buyer)
        for item in checkouts:
            cp = CheckoutProducts.objects.filter(checkout=item)
            data = {
                'checkout':item,
                'checkoutProduct':cp
            }
            orders.append(data)
        brand = Brand.objects.all()
        subcategory = Subcategory.objects.all()
        maincategory = Maincategory.objects.all()
        return render(Request,"profile.html",{'data':buyer,'wishlist':wishlist,'orders':orders,'maincategory':maincategory,'subcategory':subcategory,'brand':brand})


@login_required(login_url="/login/")
def updateProfilePage(Request):
    user = User.objects.get(username=Request.user.username)
    if(user.is_superuser):
        return HttpResponseRedirect("/admin/")
    else:
        buyer = Buyer.objects.get(username=Request.user.username)
        if(Request.method=="POST"):
            buyer.name = Request.POST.get("name")
            buyer.email = Request.POST.get("email")
            buyer.phone = Request.POST.get("phone")
            buyer.addressline1 = Request.POST.get("addressline1")
            buyer.addressline2 = Request.POST.get("addressline2")
            buyer.addressline3 = Request.POST.get("addressline3")
            buyer.pin = Request.POST.get("pin")
            buyer.city = Request.POST.get("city")
            buyer.state = Request.POST.get("state")
            if(Request.FILES.get("pic")):
                buyer.pic = Request.FILES.get("pic")
            buyer.save()
            return HttpResponseRedirect("/profile/")
    brand = Brand.objects.all()
    subcategory = Subcategory.objects.all()
    maincategory = Maincategory.objects.all()
    return render(Request,"update-profile.html",{'data':buyer,'maincategory':maincategory,'subcategory':subcategory,'brand':brand})

def addToCartPage(Request,num):
    p = Product.objects.get(id=num)
    cart = Request.session.get("cart",None)
    cartCount = Request.session.get("cartCount",0)
    if(cart):
        if(str(p.id) in cart):
            item = cart[str(p.id)]
            item['qty']=item['qty']+1
            item['total']=item['total']+p.finalprice
            cart[str(p.id)]=item
        else:
            cart.setdefault(str(p.id),{'name':p.name,'color':p.color,'size':p.size,'price':p.finalprice,'qty':1,'total':p.finalprice,'pic':p.pic1.url})
    else:
        cart = {str(p.id):{'name':p.name,'color':p.color,'size':p.size,'price':p.finalprice,'qty':1,'total':p.finalprice,'pic':p.pic1.url}}
    Request.session['cart']=cart
    total = 0
    for value in cart.values():
        total = total+value['total']
    if(total<1000 and total>0):
        shipping = 150
    else:
        shipping = 0
    Request.session['total']=total
    Request.session['shipping']=shipping
    Request.session['final']=total+shipping
    Request.session['cartCount']=cartCount+1
    return HttpResponseRedirect("/cart/")

def cartPage(Request):
    cart = Request.session.get('cart',None)
    items = []
    if(cart):
        for key,value in cart.items():
            value.setdefault('id',key)
            items.append(value)
    total = Request.session.get('total',0)
    shipping = Request.session.get('shipping',0)
    final = Request.session.get('final',0)
    brand = Brand.objects.all()
    subcategory = Subcategory.objects.all()
    maincategory = Maincategory.objects.all()
    return render(Request,"cart.html",{'cart':items,'total':total,'shipping':shipping,'final':final,'maincategory':maincategory,'subcategory':subcategory,'brand':brand})

def deleteCartPage(Request,id):
    cart = Request.session.get("cart",None)
    cartCount = 0
    if(cart and id in cart):
        del cart[id]
        Request.session['cart']=cart

        total = 0
        for value in cart.values():
            total = total+value['total']
            cartCount = cartCount+value['qty']
        if(total<1000 and total>0):
            shipping = 150
        else:
            shipping = 0
        Request.session['total']=total
        Request.session['shipping']=shipping
        Request.session['final']=total+shipping
        Request.session['cartCount']=cartCount
    return HttpResponseRedirect("/cart/")


def updateCartPage(Request,id,op):
    cart = Request.session.get("cart",None)
    cartCount = Request.session.get("cartCount",0)
    if(cart and id in cart):
        item = cart[id]
        if(op=="dec" and item['qty']==1):
            pass
        elif(op=="dec"):
            item['qty']=item['qty']-1
            item['total']=item['total']-item['price'] 
            cartCount=cartCount-1 
        else:
            item['qty']=item['qty']+1
            item['total']=item['total']+item['price']
            cartCount=cartCount+1
        cart[id]=item 
        Request.session['cart']=cart
        Request.session['cartCount']=cartCount
        total = 0
        for value in cart.values():
            total = total+value['total']
        if(total<1000 and total>0):
            shipping = 150
        else:
            shipping = 0
        Request.session['total']=total
        Request.session['shipping']=shipping
        Request.session['final']=total+shipping
        
    return HttpResponseRedirect("/cart/")

@login_required(login_url='/login/')
def addToWishlistPage(Request,num):
    user = User.objects.get(username=Request.user.username)
    if(user.is_superuser):
        return HttpResponseRedirect("/admin/")
    else:
        buyer = Buyer.objects.get(username=Request.user.username)
        product = Product.objects.get(id=num)
        try:
            wishlist = Wishlist.objects.get(user=buyer,product=product)
        except:
            wish = Wishlist()
            wish.user = buyer
            wish.product = product
            wish.save()
        return HttpResponseRedirect("/profile/")

@login_required(login_url='/login/')
def deleteWishlistPage(Request,num):
    user = User.objects.get(username=Request.user.username)
    if(user.is_superuser):
        return HttpResponseRedirect("/admin/")
    else:
        buyer = Buyer.objects.get(username=Request.user.username)
        try:
            wishlist = Wishlist.objects.get(user=buyer,id=num)
            wishlist.delete()
        except:
            pass
        return HttpResponseRedirect("/profile/")

def forgetPasswordPage1(Request):
    if(Request.method=="POST"):
        username = Request.POST.get("username")
        try:
            user = User.objects.get(username=username)
            if(user.is_superuser):
                return HttpResponseRedirect("/admin/")
            else:
                Request.session['resetuser'] = username
                num = randint(100000,999999)
                buyer = Buyer.objects.get(username=username)
                buyer.otp = num
                buyer.save() 
                subject = 'OTP for Password Reset- Team Essence'
                message = "OTP for Password Reset is "+str(num)+"\nNever Share Your OTP With Anyone"
                email_from = settings.EMAIL_HOST_USER
                recipient_list = [buyer.email, ]
                send_mail( subject, message, email_from, recipient_list )
                return HttpResponseRedirect("/forget-2/")
        except:
            messages.error(Request,"Invalid Username")
    brand = Brand.objects.all()
    subcategory = Subcategory.objects.all()
    maincategory = Maincategory.objects.all()
    return render(Request,"forget-1.html",{'maincategory':maincategory,'subcategory':subcategory,'brand':brand})

def forgetPasswordPage2(Request):
    username = Request.session.get("resetuser",None)
    if(Request.method=="POST" and username):
        otp = Request.POST.get("otp")
        try:
            buyer = Buyer.objects.get(username=username)
            if(buyer.otp == int(otp)):
                Request.session['otp']=otp
                return HttpResponseRedirect("/forget-3/")
            else:
                messages.error(Request,"Invalid OTP")                
        except:
            messages.error(Request,"Invalid Username")
    brand = Brand.objects.all()
    subcategory = Subcategory.objects.all()
    maincategory = Maincategory.objects.all()
    return render(Request,"forget-2.html",{'maincategory':maincategory,'subcategory':subcategory,'brand':brand})

def forgetPasswordPage3(Request):
    otp = Request.session.get("otp",None)
    if(otp):
        if(Request.method=="POST"):
            resetUser = Request.session.get("resetuser",None)
            if(resetUser and otp):
                buyer = Buyer.objects.get(username=resetUser)
                if(int(otp)==buyer.otp):
                    password = Request.POST.get("password")
                    cpassword = Request.POST.get("cpassword")
                    if(password!=cpassword):
                        messages.error(Request,"Password and Confirm Password Doesn't Matched!!!!")
                    else:
                        user = User.objects.get(username=resetUser)
                        user.set_password(password)
                        user.save()
                        subject = 'Password Reset SuccessFully- Team Essence'
                        message = "Your Password Has Been Reset Successfully Now you can login to Your Account"
                        email_from = settings.EMAIL_HOST_USER
                        recipient_list = [buyer.email, ]
                        send_mail( subject, message, email_from, recipient_list )
                        del Request.session['resetuser']
                        del Request.session['otp']
                        return HttpResponseRedirect("/login/")
                else:
                    messages.error(Request,"Un-Authorised!!!")                
            else:
                messages.error(Request,"Un-Authorised!!!")
                brand = Brand.objects.all()
                subcategory = Subcategory.objects.all()
                maincategory = Maincategory.objects.all()
                return render(Request,"forget-3.html",{'maincategory':maincategory,'subcategory':subcategory,'brand':brand})
    else:
        return HttpResponseRedirect("/forget-1/")