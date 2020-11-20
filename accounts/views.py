from django.shortcuts import render,redirect
from django.forms import inlineformset_factory
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required


from .models import *
from .forms import OrderForm,CreateUserForm,CustomerForm
from .filters import OrderFilter
from .decorators import unauthenticated_user,allowed_user,admin_only

@unauthenticated_user
def registerUser(request):
    form=CreateUserForm()
    if request.method=='POST':
        form=CreateUserForm(request.POST)
        if form.is_valid():
            user=form.save()
            username=form.cleaned_data.get('username')
            #adding user as customer not admin
            
            messages.success(request,'Account has been created for '+username)
            return redirect('login')
    context={'form':form}
    return render(request,'accounts/register.html',context)

@unauthenticated_user
def loginUser(request):
    if request.method=='POST':
        username=request.POST.get('username')
        password=request.POST.get('password')
        
        user=authenticate(request,username=username,password=password)
        if user is not None:
            login(request,user)
            return redirect('home')
        else:
            messages.info(request,'<Username/Password is incorrec')
            
    context={}
    return render(request,'accounts/login.html',context)

def logoutUser(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
@admin_only
def home(request):
    orders=Order.objects.all()
    customer=Customer.objects.all()
    total_orders=orders.count()
    delivered=orders.filter(status='Delivered').count()
    pending=orders.filter(status='Pending').count()
    
    context={'orders':orders,'customers':customer,'delivered':delivered,'pending':pending,
             'total_orders':total_orders}
    return render(request,'accounts/dashboard.html',context)

@login_required(login_url='login')
@allowed_user(allowed_roles=['customer'])
def userPage(request):
    orders=request.user.customer.order_set.all()
    total_orders=orders.count()
    delivered=orders.filter(status='Delivered').count()
    pending=orders.filter(status='Pending').count()
    context={'orders':orders,'delivered':delivered,'pending':pending,
             'total_orders':total_orders}
    return render(request,'accounts/user.html',context)

@login_required(login_url='login')
@allowed_user(allowed_roles=['customer'])
def accountSettings(request):
    customer=request.user.customer
    form=CustomerForm(instance=customer)
    if request.method=='POST':
        form=CustomerForm(request.POST, request.FILES,instance=customer)
        if form.is_valid():
            form.save()
    
    context={'form':form}
    return render(request,'accounts/account_settings.html',context)

@login_required(login_url='login')
@allowed_user(allowed_roles=['admin'])
def products(request):
    products=Product.objects.all()
    return render(request,'accounts/products.html',{'products':products})

@login_required(login_url='login')
@allowed_user(allowed_roles=['admin'])
def customers(request,pk_test):
    customer=Customer.objects.get(id=pk_test)
    orders=customer.order_set.all()
    total_orders=customer.order_set.all().count()
    
    myFilter=OrderFilter(request.GET,queryset=orders)
    orders=myFilter.qs
    
    context={'customer':customer,'orders':orders,'total_orders':total_orders,
             'myFilter':myFilter}
    return render(request,'accounts/customers.html',context)

@login_required(login_url='login')
@allowed_user(allowed_roles=['admin'])
def createOrder(request,pk):
    OrderFormSet=inlineformset_factory(Customer,Order,fields=('product','status'),extra=5)
    customer=Customer.objects.get(id=pk)
    #for single order
    #form=OrderForm(initial={'customer':customer})
    #for Multiple orders
    formset=OrderFormSet(queryset=Order.objects.none(),instance=customer)
    if request.method=='POST':
        #for single order
        #form=OrderForm(request.POST)
        #for multiple orders
        formset=OrderFormSet(request.POST,instance=customer)
        if formset.is_valid():
            formset.save()
            return redirect('/')
    
    context={'formset':formset}
    return render(request,'accounts/order.html',context)

@login_required(login_url='login')
@allowed_user(allowed_roles=['admin'])
def updateOrder(request,pk):
    order=Order.objects.get(id=pk)
    
    form=OrderForm(instance=order)
    if request.method=='POST':
        form=OrderForm(request.POST,instance=order)
        if form.is_valid():
            form.save()
            return redirect('/')
    
    context={'form':form}
    return render(request,'accounts/order.html',context)

@login_required(login_url='login')  
@allowed_user(allowed_roles=['admin'])  
def deleteOrder(request,pk):
    order=Order.objects.get(id=pk)
    if request.method=='POST':
        order.delete()
        return redirect('/')
    context={'order':order}
    return render(request,'accounts/delete.html',context)    
    