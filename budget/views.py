from django.shortcuts import render,redirect

from django.views.generic import View

from budget.models import Transaction

from django import forms

from django.contrib.auth.models import User

from django.contrib.auth import authenticate,login,logout

from django.utils import timezone

from django.db.models import Sum

from django.utils.decorators import method_decorator

from django.contrib import messages

from django.views.decorators.cache import never_cache

# Create your views here.


# decorator


def sigin_required(fn):

    def wrapper(request,*args,**kwargs):

        if not request.user.is_authenticated:
            messages.error(request,"invalid session") 
            return redirect("signin")
        else:
            return fn(request,*args,**kwargs)
    return wrapper

decs=[sigin_required,never_cache]

class TransactionForm(forms.ModelForm):

    class Meta:
        model=Transaction
        exclude=("created_date","user_object")
        # fields="__all__"
        # fields=["field1","field"2,....]
        widgets={
            "title":forms.TextInput(attrs={"class":"form-control"}),
            "amount":forms.NumberInput(attrs={"class":"form-control"}),
            "type":forms.Select(attrs={"class":"form-control form-select"}),
            "category":forms.Select(attrs={"class":"form-control form-select"})
        }


# transaction list
        
# url:- localhost:8000/tarnsactions/all/
# method get
        
@method_decorator(decs,name="dispatch")
class TransactionListView(View):
    def get(self,request,*args,**kwargs):
        qs=Transaction.objects.filter(user_object=request.user)

        current_month=timezone.now().month
        current_year=timezone.now().year

        data=Transaction.objects.filter(
            created_date__month=current_month,
            created_date__year=current_year,
            user_object=request.user
        ).values("type").annotate(type_sum=Sum("amount"))

        cate=Transaction.objects.filter(
            created_date__month=current_month,
            created_date__year=current_year,
            user_object=request.user
        ).values("category").annotate(cate_sum=Sum("amount"))
        print(cate)

        return render(request,"transaction_list.html",{"data":qs,"type_total":data,"cat":cate})

        # print(current_month,current_year)

        # exp_total=Transaction.objects.filter(
        #     user_object=request.user,
        #     type="expense",
        #     created_date__month=current_month,
        #     created_date__year=current_year
        # ).aggregate(Sum("amount"))
        # print(exp_total)
        

        # income_total=Transaction.objects.filter(
        #     user_object=request.user,
        #     type="income",
        #     created_date__month=current_month,
        #     created_date__year=current_year
        # ).aggregate(Sum("amount"))
        # print(income_total)

        



# view for creating new transaction
# url:-localhost:8000/transactions/add/
# method: post
    
@method_decorator(decs,name="dispatch")

class TransactionCreateView(View):
    def get(self,request,*args,**kwargs):
        form=TransactionForm()
        return render(request,"transaction_add.html",{"form":form})
    
    def post(self,request,*args,**kwargs):
        form=TransactionForm(request.POST)
        if form.is_valid():
            # data=form.cleaned_data
            # Transaction.objects.create(**data)
            form.instance.user_object=request.user
            form.save()
            messages.success(request,"Transaction has been added")
            return redirect("transaction-list")
        else:
            messages.error(request,"failed to add transaction")
            return render(request,"transaction_add.html",{"form":form})




# transaction detail
        # url:localhodt:8000/transactions/{id}/
        # method: get

@method_decorator(decs,name="dispatch")


class TransactionDetailView(View):
    def get(self,request,*args,**kwargs):
        # if not request.user.is_authenticated:
        #     return redirect("signin")
        id=kwargs.get("pk")

        qs=Transaction.objects.get(id=id)
        return render(request,"transaction_detail.html",{"data":qs})
    


# transaction delete
    # url:loclahost:8000/tansactions/{int}/
    # method: get

@method_decorator(decs,name="dispatch")

class TransactionDeleteView(View):
    def get(self,request,*args,**kwargs):

        id=kwargs.get("pk")
        Transaction.objects.filter(id=id).delete()
        messages.success(request,"Transaction has been removed")
        return redirect("transaction-list")
    


# transaction edit
    # url:localhost:8000/transactions/{int}/change/
    # methost: get,post

@method_decorator(decs,name="dispatch")

class TransactionUpdateView(View):
    def get(self,request,*args,**kwargs):
        id=kwargs.get("pk")
        transaction_object=Transaction.objects.get(id=id)
        form=TransactionForm(instance=transaction_object)
        return render(request,'transaction_edit.html',{"form":form})
    
    def post(self,request,*args,**kwargs):
        id=kwargs.get("pk")
        transaction_object=Transaction.objects.get(id=id)
        data=request.POST
        form=TransactionForm(data,instance=transaction_object)
        if form.is_valid():
            form.save()
            messages.success(request,"Transaction has been updated")
            return redirect('transaction-list')
        else:
            messages.error(request,"Failed to update transaction")
            return render(request,'transaction_edit.html',{"form":form})
        



class RegistrationForm(forms.ModelForm):
    class Meta:
        model=User
        fields=["username","email","password",]

        widgets={
            "username":forms.TimeInput(attrs={"class":"form-control"}),
            "email":forms.EmailInput(attrs={"class":"form-control"}),
            "password":forms.PasswordInput(attrs={"class":"form-control form-select"}),
        }



class LoginForm(forms.Form):

    username=forms.CharField(widget=forms.TextInput(attrs={"calss":"format-control"}))
    password=forms.CharField(widget=forms.PasswordInput(attrs={"calss":"forms-control"}))







# signup
        # url :localhost:8000/signup/
        # method; get, post

class SignupView(View):

    def get(self,request,*args,**kwargs):
        form=RegistrationForm()
        return render(request,"signup.html",{"form":form})
    
    def post(self,request,*args,**kwargs):
        form=RegistrationForm(request.POST)
        if form.is_valid():
            # form.save() #password encrypt
            User.objects.create_user(**form.cleaned_data)
            print("Registartion Successful")
            return redirect("signin")
        else:
            return render(request,"signup.html",{"form":form})


    

# sign in
        # url:localhost:8000/signin/
        # method: get,post

class SigInView(View):
    def get(self,request,*args,**kwargs):
        form=LoginForm()
        return render(request,"signin.html",{"form":form})

    def post(self,request,*args,**kwargs):
        form=LoginForm(request.POST)
        if form.is_valid():
            u_name=form.cleaned_data.get("username")
            pwd=form.cleaned_data.get("password")

            user_object=authenticate(request,username=u_name,password=pwd)
            if user_object:
                print("credentials are valid")
                login(request,user_object)
                messages.success(request,"login success")
                return redirect("transaction-list")
                messages.success(request,"login success")

        print("invalid")
        return render(request,"signin.html",{"form":form})
    

@method_decorator(decs,name="dispatch")

class SignOutView(View):
    def get(self,request,*args,**kwargs):
        logout(request)
        messages.success(request,"Logout successfully")
        return redirect('signin')
    

            


