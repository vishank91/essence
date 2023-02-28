from django.db import models

class Buyer(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30)
    username = models.CharField(max_length=50)
    email = models.EmailField(max_length=50)
    phone = models.CharField(max_length=15)
    addressline1 = models.CharField(max_length=50)
    addressline2 = models.CharField(max_length=50)
    addressline3 = models.CharField(max_length=50)
    pin = models.CharField(max_length=10)
    city = models.CharField(max_length=30)
    state = models.CharField(max_length=30)
    pic = models.ImageField(upload_to="user")
    otp = models.IntegerField(default=8898898)

    def __str__(self):
        return self.username+"/"+self.name+"/"+self.email

class Maincategory(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20,unique=True)

    def __str__(self):
        return self.name

class Subcategory(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20,unique=True)

    def __str__(self):
        return self.name

class Brand(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20,unique=True)
    pic = models.ImageField(upload_to="brand")

    def __str__(self):
        return self.name


class Product(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    maincategory = models.ForeignKey(Maincategory,on_delete=models.CASCADE)
    subcategory = models.ForeignKey(Subcategory,on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand,on_delete=models.CASCADE)
    color = models.CharField(max_length=20)
    size = models.CharField(max_length=10)
    baseprice = models.IntegerField()
    discount = models.IntegerField()
    finalprice = models.IntegerField()
    stock = models.BooleanField(default=True)
    description = models.TextField()
    pic1 = models.ImageField(upload_to="product")
    pic2 = models.ImageField(upload_to="product")
    pic3 = models.ImageField(upload_to="product",default="",blank=True,null=True)
    pic4 = models.ImageField(upload_to="product",default="",blank=True,null=True)

    def __str__(self):
        return self.name


status = ((0,"Order Placed"),(1,"Not Packed"),(2,"Packed"),(3,"Ready to Dispatch"),(4,"Dispatched"),(5,"Out For Delivery"),(6,"Delivered"),(7,"Cancelled"))
payment = ((0,"Pending"),(1,"Done"))
mode = ((0,"COD"),(1,"Net Banking"))
class Checkout(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(Buyer,on_delete=models.CASCADE)
    orderStatus = models.IntegerField(choices=status,default=0)
    paymentMode = models.IntegerField(choices=mode,default=0)
    paymentStatus = models.IntegerField(choices=payment,default=0)
    rppid = models.CharField(max_length=50,default="",null=True,blank=True)
    totalAmount = models.IntegerField()
    shippingAmount = models.IntegerField()
    finalAmount = models.IntegerField()
    time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)+" "+self.user.username
class CheckoutProducts(models.Model):
    id = models.AutoField(primary_key=True)
    checkout = models.ForeignKey(Checkout,on_delete=models.CASCADE)
    pid = models.IntegerField(default=None)
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=50)
    size = models.CharField(max_length=50)
    price = models.IntegerField()
    qty = models.IntegerField()
    total = models.IntegerField()
    pic = models.CharField(max_length=50)


class Wishlist(models.Model):
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    user = models.ForeignKey(Buyer,on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username+" "+self.product.name

status = ((0,"Active"),(1,"Done"))
class ContactUs(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30)
    email = models.CharField(max_length=50)
    phone = models.CharField(max_length=15)
    subject = models.TextField()
    message = models.TextField()
    status = models.IntegerField(choices=status,default=0)
    date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)+" "+self.name+" "+self.email


