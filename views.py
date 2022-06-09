from ast import Index
from asyncio.locks import _ContextManagerMixin
from logging import exception
from math import lgamma
from pdb import post_mortem
import re
from socket import PACKET_LOOPBACK
from threading import local
from time import sleep
from urllib import request, response
from urllib.error import HTTPError
from venv import create
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.views.decorators.csrf import csrf_exempt
from  datetime import date, timedelta
from django.views.generic import TemplateView
from django.db.models import Sum
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets
import datetime
from django.views.generic.base import ContextMixin


from .models import IndexForm, Index, Supplier, PackageForm, Package, LogInventory, inventory,deletions
from .models import IndexForm, SupplierForm, CurrentUser, Log, DayQuantity, DeletedPackage, InvetoriedRestore
from .functions import create_log, update_utilisation, remove_slash, return_slash, create_LogInventory
from .serializers import IndexSerializer, SupplierSerializer, PackageSerializer
from .forms import LoginForm, RetrievePackageForm


# Create your views here.
    

LABELS = {
    'package_supplier':'DOSTAWCA',
    'index_sap':'SAP',
    'index_name':'NAZWA',
    'package_pk':'ID PACZKI',
    'package_paczka':'PACZKA',
    'package_delivery_date':'DATA DOSTAWY',
    'package_localisation':'LOKALIZACJA',
    'package_deviation' : "BRAKI",
    'package_length':'DŁUGOŚĆ',
    'package_wz':'WZ',
    'log_package':'ID PACZKI',
    'log_operation':'OPERACJA',
    'log_time':'CZAS',
    'log_username':'UŻYTKOWNIK',
    'log_length_before':'DŁUGOŚĆ',
    'log_length_after':'DŁUGOŚĆ',
    'log_localisation_before':'LOKALIZACJA',
    'log_localisation_after':'LOKALIZACJA',




}

LOCS = ("WSZYSTKIE","MAG","PRD")

class inventory_retrieve(TemplateView):
    form_class = RetrievePackageForm
    template_name = 'boards/inventory_retrieve.html'
    deletedPackage= ""
    package = Package()
    def get_context_data(self, **kwargs):
        context = super(inventory_retrieve, self).get_context_data(**kwargs)
        context['form'] = self.form_class()
        context['deletedPackage'] = self.deletedPackage
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            package_id = form.cleaned_data['package_id']
            print(package_id)

            self.deletedPackage = get_object_or_404(DeletedPackage, pk=package_id)
            self.package.pk = self.deletedPackage.pk
            self.package.id = self.deletedPackage.id
            self.package.paczka = self.deletedPackage.paczka
            self.package.index = self.deletedPackage.index
            self.package.delivery_date = self.deletedPackage.delivery_date
            self.package.delivery_time = self.deletedPackage.delivery_time
            self.package.supplier = self.deletedPackage.supplier
            self.package.werk = self.deletedPackage.werk
            self.package.localisation = self.deletedPackage.localisation
            self.package.length_on_close =  self.deletedPackage.length_on_close
            self.package.length =  self.deletedPackage.length
            self.package.length_correction = self.deletedPackage.length_correction
            self.package.length_initial_prd = self.deletedPackage.length_initial_prd
            self.package.wz = self.deletedPackage.wz
            self.package.inventoried = False #self.deletedPackage.inventoried
            self.package.save()
            DeletedPackage.objects.get(pk=self.deletedPackage.pk).delete()

            #for i in self.deletedPackage._meta.get_fields():
            #    self = self.
            #    print(i)            


            #Package.objects.get(pk=package_id)

            return render(request, self.template_name, self.get_context_data(**kwargs))
        else:
            print(self.form.is_valid())
            return HttpResponse("BLAD")

#    
    #def get(self, request, *args,  **kwargs):
    #    context['form'] = self.form_class(None)



@login_required(login_url='/boards/loginlocal/')      
def inventory_arch(request, *args, **kwargs):
    url='boards/inventory_arch.html'
    #def get(self, request)
    #    return 

    inventories = inventory.objects.all().order_by('-inventory_date')
    context = {
        'inventories' : inventories,
    }

    if request.method == 'POST':
        inventory_arch = inventory.objects.filter(name=request.POST['inventories']).first()
        logInventories = LogInventory.objects.filter(inventory_name="INWENTURA")
        for logInventory in logInventories:
            logInventory.inventory_name=inventory_arch.name
            logInventory.inventory=inventory_arch
            logInventory.save()
        for package in Package.objects.filter(inventoried=True): #.exclude(localisation="DOST").exclude(localisation="CLOSED"):  ## Chyb jednak zdejmujemy wszystkie inventoried! też te CLOSED

            package.inventoried = False
            package.save()
            invetoriedRestore = InvetoriedRestore()
            invetoriedRestore.package=package
            invetoriedRestore.inventory = inventory_arch
            invetoriedRestore.save()
        context['logInventories'] = logInventories




        

    return render(request,url,context)

@login_required(login_url='/boards/loginlocal/')      
def inventory_move(request, *args, **kwargs):
    url='boards/inventory_move.html'
    alert = ""
    context = {
    }
    print(request.POST)
    if request.method == 'POST' and request.POST['postnr']=="1":
        try:
            print(request.POST)
            if request.POST['locs']!="WSZYSTKIE":
                packagesToBeDeleted = Package.objects.filter(inventoried=False,localisation=request.POST['locs'])
                packagesToBeDeletedCnt = Package.objects.filter(inventoried=False,localisation=request.POST['locs']).count()
            else:
                packagesToBeDeleted = Package.objects.filter(inventoried=False).exclude(localisation="DOST").exclude(localisation="CLOSED")
                packagesToBeDeletedCnt = Package.objects.filter(inventoried=False).exclude(localisation="DOST").exclude(localisation="CLOSED").count()

            context['packagesToBeDeleted'] = packagesToBeDeleted
            context['packagesToBeDeletedCnt'] = packagesToBeDeletedCnt
        except  Exception as e:
            alert = f"Wybierz lokalizację!!! - błąd {e}"
    elif request.method == 'POST' and request.POST['postnr']=="2":
        keys = filter(lambda x:x[0].isdigit(),request.POST.keys())
        keys_tmp = filter(lambda x:x[0].isdigit(),request.POST.keys())
        package_deleted_as_first = list(keys_tmp)[0]
        for pk in keys:

            deletions.objects.create(package=int(pk), package_deleted_as_first=int(package_deleted_as_first))
            try:
                if DeletedPackage.objects.get(pk=pk):
                    DeletedPackage.objects.get(pk=pk).delete()
            except:
                pass
            DeletedPackage.objects.create(
                                        pk=pk,
                                        paczka=Package.objects.get(pk=pk).paczka,
                                        index=Package.objects.get(pk=pk).index,
                                        delivery_date=Package.objects.get(pk=pk).delivery_date,
                                        delivery_time=Package.objects.get(pk=pk).delivery_time,
                                        supplier=Package.objects.get(pk=pk).supplier,
                                        werk=Package.objects.get(pk=pk).werk,
                                        localisation=Package.objects.get(pk=pk).localisation,
                                        length=Package.objects.get(pk=pk).length,
                                        length_correction=Package.objects.get(pk=pk).length_correction,
                                        length_on_close=Package.objects.get(pk=pk).length_on_close,
                                        length_initial_prd=Package.objects.get(pk=pk).length_initial_prd,
                                        wz=Package.objects.get(pk=pk).wz,
                                        inventoried=False)
            #Package.objects.get(pk=pk).delete() ### ODBLOKUJ!!!ODBLOKUJ!!!ODBLOKUJ!!!ODBLOKUJ!!!ODBLOKUJ!!!



    context['locs']=LOCS
    context['alert'] = alert
    return render(request,url,context)


@login_required(login_url='/boards/loginlocal/')      
def add_inv_arch(request, *args, **kwargs):
    url = 'boards/add_inv_arch.html'
    inv_list = inventory.objects.all().order_by('inventory_date')
    i=0
    recommended_name = "INWENTURA_{}_MAG".format(datetime.date.today())
    while True:
        i+=1
        if not inventory.objects.filter(name=recommended_name):
            break
        else:
            recommended_name = recommended_name[:-1]+str(i)

    recommended_date = "{}".format(datetime.date.today().strftime("%Y-%m-%d"))
    context = {
        'inv_list': inv_list,
        'recommended_name' : recommended_name,
        'recommended_date' : recommended_date,
        
    }
    if request.method == "POST":
        try:
            inventory.objects.create(name=request.POST['inwentura'],inventory_date=request.POST['data_inv_arch'])
            return HttpResponseRedirect("/boards/add_inv_arch/")
        except:
            context['alert'] = "PRÓBA UTWORZENIA DUPLIKATU!!!"
        

    
    return render(request,url, context)
@login_required(login_url='/boards/loginlocal/')      
def zuzycie(request, *args, **kwargs):
    url='boards/zuzycie.html'
    context = {}
    current_date = datetime.date.today()
    indexes = Index.objects.all()
    dayQuantities = []
    print(request.POST)
    if request.method == "POST":
        data_od = request.POST['data_od']
        data_do = request.POST['data_do']
        for index in indexes:
            dq = {}
            dayQuantity = DayQuantity.objects.filter(date__gte=data_od,date__lte=data_do,index=index)
            sum_update_length = DayQuantity.objects.filter(date__gte=data_od,date__lte=data_do,index=index).aggregate(Sum('update_length'))
            sum_close_package = DayQuantity.objects.filter(date__gte=data_od,date__lte=data_do,index=index).aggregate(Sum('close_package'))
            sum_update_length_ = sum_update_length['update_length__sum'] if sum_update_length['update_length__sum'] != None else 0
            sum_close_package_ = sum_close_package['close_package__sum'] if sum_close_package['close_package__sum'] != None else 0
            utilisation4day = sum_update_length_ + sum_close_package_
            dq['index'] = index
            dq['utilisation4day'] = utilisation4day
            dayQuantities.append(dq)
        print(dayQuantities)
    else:
        for index in indexes:
            dq = {}
            dayQuantity = DayQuantity.objects.filter(date=current_date,index=index).first()
            update_length = dayQuantity.update_length if dayQuantity.update_length!=None else 0
            close_package = dayQuantity.close_package if dayQuantity.close_package!=None else 0
            utilisation4day = update_length + close_package
            dq['index'] = index
            dq['utilisation4day'] = utilisation4day         
            dayQuantities.append(dq)

    context['data'] = current_date
    context['labels'] = LABELS
    context['dayQuantities'] = dayQuantities

    return render(request,url,context)

@login_required(login_url='/boards/loginlocal/')      
def zuzycie_log(request, *args, **kwargs):
    url='boards/zuzycie_log.html'
    context = {}
    current_date = datetime.date.today()# +timedelta(days = 1)
    print(current_date)
    indexes = Index.objects.all()
    dayQuantities = []
    print(request.POST)

    rowid=0
    if request.method == "POST":
        data_od = request.POST['data_od']
        data_do_ = request.POST['data_do']
        #data_do_ = datetime.datetime.strptime(data_do, '%Y-%m-%d')+timedelta(days = 1)
        print(data_do_)
        
        for index in indexes:
            rowid +=1
            dq = {}

            log = Log.objects.filter(index_before=index, localisation_before="PRD",time__gte=data_od,time__lte=data_do_).exclude(localisation_after="DOST") # 17.05.2022 exclude(localisation_after="MAG").
            sum_length_before = log.aggregate(Sum('length_before'))['length_before__sum'] if log.aggregate(Sum('length_before'))['length_before__sum'] != None else 0
            sum_length_after = log.aggregate(Sum('length_after'))['length_after__sum'] if log.aggregate(Sum('length_after'))['length_after__sum'] != None else 0


            utilisation4day = sum_length_before - sum_length_after
            packages = set()
            for l in log:                
                packages.add(l.package)

            sum_length_correction = 0
            for package in packages:
                rowid+=1
                sum_length_correction += package.length_correction

            dq['rowtype'] = "HEADER"
            dq['index'] = index
            dq['utilisation4day'] = utilisation4day
            dq['sum_length_correction'] = sum_length_correction
            dq['rowid'] = rowid
            dq['packages_cnt']=len(packages)
            dayQuantities.append(dq)

            for package in packages:
                dq = {}
                #rowid +=1

                logP = log.filter(package=package)
                sum_length_beforeP = logP.aggregate(Sum('length_before'))['length_before__sum'] if logP.aggregate(Sum('length_before'))['length_before__sum'] != None else 0
                sum_length_afterP = logP.aggregate(Sum('length_after'))['length_after__sum'] if logP.aggregate(Sum('length_after'))['length_after__sum'] != None else 0
                utilisation4dayP = sum_length_beforeP - sum_length_afterP
                print(sum_length_beforeP, sum_length_afterP, utilisation4dayP)

                dq['rowtype'] = "ROW"
                dq['package_pk'] = package.pk
                dq['package_paczka'] = package.paczka

                dq['package_name'] = package.paczka
                dq['package_length'] = package.length
                dq['index'] = index
                dq['utilisation4dayP'] = utilisation4dayP
                dq['package_length_correction']=package.length_correction
                dq['rowid'] = rowid
                dq['packages_cnt']=0

                dayQuantities.append(dq)

    else:
        #from datetime import date
        #from datetime import datetime

        #dt = datetime.datetime.combine(current_date, datetime.datetime.min.time())

        for index in indexes:
            rowid +=1            
            print(current_date)
            dq = {}
            log = Log.objects.filter(index_before=index, localisation_before="PRD",time__gte=current_date).exclude(localisation_after="DOST") # 17.05.2022 exclude(localisation_after="MAG").
            sum_length_before = log.aggregate(Sum('length_before'))['length_before__sum'] if log.aggregate(Sum('length_before'))['length_before__sum'] != None else 0
            sum_length_after = log.aggregate(Sum('length_after'))['length_after__sum'] if log.aggregate(Sum('length_after'))['length_after__sum'] != None else 0

            #dayQuantity = DayQuantity.objects.filter(date=current_date,index=index).first()
            #update_length = dayQuantity.update_length if dayQuantity.update_length!=None else 0
            #close_package = dayQuantity.close_package if dayQuantity.close_package!=None else 0
            #utilisation4day = update_length + close_package
            utilisation4day = sum_length_before - sum_length_after
            packages = set()
            for l in log:                
                packages.add(l.package)

            sum_length_correction = 0
            for package in packages:
                rowid+=1
                sum_length_correction += package.length_correction

            dq['rowtype'] = "HEADER"
            dq['index'] = index
            dq['utilisation4day'] = utilisation4day
            dq['sum_length_correction'] = sum_length_correction
            dq['rowid'] = rowid
            dq['packages_cnt']=len(packages)

            dayQuantities.append(dq)
            for package in packages:
                dq = {}
                logP = log.filter(package=package)
                sum_length_beforeP = logP.aggregate(Sum('length_before'))['length_before__sum'] if logP.aggregate(Sum('length_before'))['length_before__sum'] != None else 0
                sum_length_afterP = logP.aggregate(Sum('length_after'))['length_after__sum'] if logP.aggregate(Sum('length_after'))['length_after__sum'] != None else 0
                utilisation4dayP = sum_length_beforeP - sum_length_afterP
                print(sum_length_beforeP, sum_length_afterP, utilisation4dayP)
                dq['rowtype'] = "ROW"
                dq['package_pk'] = package.pk
                dq['package_name'] = package.paczka
                dq['package_length'] = package.length
                dq['index'] = index
                dq['utilisation4dayP'] = utilisation4dayP
                dq['package_length_correction']=package.length_correction
                dq['rowid'] = rowid
                dq['packages_cnt']=0
                dayQuantities.append(dq)

    context['data'] = current_date
    context['labels'] = LABELS
    context['dayQuantities'] = dayQuantities

    return render(request,url,context)

@login_required(login_url='/boards/loginlocal/')      
def stany_magazyn(request, *args, **kwargs):
    url='boards/stany_magazyn.html'
    indexes = Index.objects.all()
    context = {}
    stany = [] 
    for index in indexes:
        stan = {}
        sum_MAG = Package.objects.filter(index=index,localisation="MAG").aggregate(Sum('length'))
        stan['index'] = index
        
        stan['suma'] = sum_MAG['length__sum'] if sum_MAG['length__sum']!=None else 0
        stany.append(stan)
    context['labels'] = LABELS
    context['stany'] = stany

    return render(request,url,context)

@login_required(login_url='/boards/loginlocal/')          
def stany_produkcja(request, *args, **kwargs):
    url='boards/stany_produkcja.html'
    indexes = Index.objects.all()
    context = {}
    stany = [] 
    for index in indexes:
        stan = {}
        sum_PRD = Package.objects.filter(index=index,localisation="PRD").aggregate(Sum('length'))
        stan['index'] = index
        
        stan['suma'] = sum_PRD['length__sum'] if sum_PRD['length__sum']!=None else 0
        stany.append(stan)
    context['labels'] = LABELS
    context['stany'] = stany

    return render(request,url,context)

@login_required(login_url='/boards/loginlocal/')      
def stany_lacznie(request, *args, **kwargs):
    url='boards/stany_lacznie.html'
    indexes = Index.objects.all()
    context = {}
    stany = [] 
    for index in indexes:
        stan = {}
        sum_PRD = Package.objects.filter(index=index,localisation="PRD").aggregate(Sum('length'))
        sum_MAG = Package.objects.filter(index=index,localisation="MAG").aggregate(Sum('length'))
        sum_ALL = Package.objects.filter(index=index).exclude(localisation="CLOSED").aggregate(Sum('length'))
        stan['index'] = index
        stan['suma_prd'] = sum_PRD['length__sum'] if sum_PRD['length__sum']!=None else 0
        stan['suma_mag'] = sum_MAG['length__sum'] if sum_MAG['length__sum']!=None else 0
        stan['suma_all'] = sum_ALL['length__sum'] if sum_ALL['length__sum']!=None else 0
        stany.append(stan)
    context['labels'] = LABELS
    context['stany'] = stany
    return render(request,url,context)


@login_required(login_url='/boards/loginlocal/')      
def packages_history(request, *args, **kwargs):
    url = 'boards/packages_history.html'
    context  = {

    }

    pk = kwargs['pk']
    context['logs'] = Log.objects.filter(package__pk=pk)
    context['labels'] = LABELS
    return render(request,url,context)

def info_del(request, *args, **kwargs):
    url='boards/info_del.html'
    context = {}

    return render(request,url,context)

def loginlocal(request, *args, **kwargs):
    context = {
    }
    url='boards/loginlocal.html'
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user = data['user']
            password = data['password']
            user_check = authenticate(username=user, password=password)
            if user_check:
                if user_check.is_authenticated:
                    login(request, user_check)
                    #return render(request,url,context)
                    return HttpResponseRedirect('/boards/')
            else:
                form = LoginForm()
                context['form']=form
                return render(request,url,context)
    else:
        form = LoginForm()
    context['form']=form
    return render(request,url,context)


def logoutlocal(request):
    logout(request)
    return HttpResponseRedirect('/boards/loginlocal')

@login_required(login_url='/boards/loginlocal/')      
def home(request, *args, **kwargs):
    url = 'boards/home.html'
    context = {
    }
    return render(request, url, context)

@login_required(login_url='/boards/loginlocal/')      
def packages_index(request, *args, **kwargs):
    url = "boards/packages_index.html"
    context = {}
    index = kwargs['pk']
    wz = kwargs['wz']
    wz = wz.replace("QQQQ","\\") # CLUTCH SOLUTION
    wz = wz.replace("qqqq","/")
    print(wz)
    if wz == "0":
        packages = Package.objects.filter(index__pk=index).exclude(localisation="CLOSED").order_by('pk')
        return_path = "/boards/index_report2/"
    else:
        print(wz)
        packages = Package.objects.filter(index__pk=index,wz=wz).exclude(localisation="CLOSED").order_by('pk') ##exclude(localisation="CLOSED")
        return_path = "/boards/index_report3/"


    context['packages'] = packages
    context['return_path'] = return_path
    context['labels'] = LABELS

    return render(request, url, context)
@login_required(login_url='/boards/loginlocal/')      
def packages_delivery(request, *args, **kwargs):
    url = 'boards/packages_delivery.html'

    context = {
    }
    if request.method == 'POST':
        packageForm = PackageForm(request.POST)# or print(request.POST['index'])
        qty = int(request.POST['qty'])+1
        for number in range(1, qty):
            index = Index.objects.get(pk=request.POST['index'])
            #if request.POST['supplier']!="":
            supplier = Supplier.objects.get(pk=request.POST['supplier']) \
                if request.POST['supplier'] != "" else None
            #package = Package.objects.create(index=index,supplier=supplier,delivery_date=request.POST['delivery_date'],localisation='MAG',length=request.POST['length'])
            package = Package.objects.create(index=index,supplier=supplier,delivery_date=request.POST['delivery_date'],localisation='DOST',wz=request.POST['wz'])
            package.create_label_large(True,LABELS,False) if 'print' in request.POST.keys()  else package.create_label_large(False,LABELS,False)
            try:
                create_log(5,"", package.length,package.length, package.localisation, package.localisation, package.delivery_date, package.delivery_date, request.user , "PC",package.index.pk,package.pk,supplier.pk,package.paczka,package.paczka,package.length_correction,package.length_correction)
            except  Exception as e:
                print(f"Nie utworzono loga {e}")



        info = f"Dodano paczkę  indeksu: {index.name} od dostawcy {supplier}"
        context['info'] = info 

            #return HttpResponseRedirect("/boards/packages_delivery/")

    else:
        packageForm = PackageForm()
        today = date.today()
        packageForm.fields['delivery_date'].initial = today.isoformat()
        packageForm.fields['length'].initial = "100"

    context['PackageForm'] = packageForm
    return render(request, url, context)
@login_required(login_url='/boards/loginlocal/')      
def admission(request, *args, **kwargs): ###DO USUNIECIA
    url = 'boards/admission.html'
    context = {
    }

    print(request)
    if request.method == 'POST':
        indexForm = IndexForm(request.POST)
        if indexForm.is_valid():
            index = Index()
            index.sap = indexForm.cleaned_data['sap']
            index.name = indexForm.cleaned_data['name']
            index.country = indexForm.cleaned_data['country']
            #index.delivery_date = indexForm.cleaned_data['delivery_date']
            index.werk = indexForm.cleaned_data['werk']
            index.localisation = indexForm.cleaned_data['localisation']
            index.save()
    context['IndexForm'] = IndexForm
    return render(request, url, context)
@login_required(login_url='/boards/loginlocal/')      
def suppliers(request, *args, **kwargs):
    url = 'boards/suppliers.html'
    suppliers = Supplier.objects.all().order_by('name')
    context = {
    }
    if request.method == 'POST':
        try:
            print(request.POST)
            supplier = Supplier.objects.get(pk=request.POST['supplier'])
            supplier.name = request.POST['name']
            supplier.save()
        except:
            print("BLA")
    context = {
    }
    context['indexes']=indexes


    context['suppliers']=suppliers
    return render(request, url, context)

@login_required(login_url='/boards/loginlocal/')      
def packages(request, *args, **kwargs):
    url = 'boards/packages.html'
    sorts = ('pk','index__sap','index','supplier','localisation','length')
    context = {
    }
    if request.method == 'POST':
        packages = Package.objects.all().exclude(localisation="CLOSED").order_by(request.POST['sort'])
        context['actual_sort'] = request.POST['sort']

    else:
        packages = Package.objects.all().exclude(localisation="CLOSED").order_by('-pk')
        context['actual_sort'] = 'pk'
    
    context['sorts']=sorts
    context['packages']=packages
    return render(request, url, context)

@login_required(login_url='/boards/loginlocal/')      
def packages_filter(request, *args, **kwargs):
    url = 'boards/packages_filter.html'
    sorts = ('pk','index__sap','index','supplier','localisation','length')
    context = {
    }
    if request.method == 'POST':
        package_filter=request.POST['package']
        delivery_date_filter=request.POST['delivery_date']
        wz_filter=request.POST['wz']
        if package_filter:
            packages = Package.objects.filter(pk=package_filter).order_by(request.POST['sort'])
        else:
            packages = Package.objects.all().order_by(request.POST['sort'])
        if delivery_date_filter:
            packages = packages.filter(delivery_date=delivery_date_filter)
        if wz_filter:
            packages = packages.filter(wz=wz_filter)
        context['actual_sort'] = request.POST['sort']

    else:
        packages = Package.objects.all().order_by('-pk')
        context['actual_sort'] = 'pk'
    
    context['sorts']=sorts
    context['packages']=packages
    context['labels']=LABELS

    return render(request, url, context)

@login_required(login_url='/boards/loginlocal/')
def packages_delivery_edit(request, *args, **kwargs):
    url = 'boards/packages_delivery_edit.html'
    wz = kwargs['wz']
    wz = return_slash(wz)
    print(wz)


    if request.method == 'POST':
        packages = Package.objects.filter(wz=request.POST['wz']) if request.POST['wz']!="" else Package.objects.all()
    else:

        package_last=Package.objects.latest('id')
        if wz!="0" and Package.objects.filter(wz=wz):
            packages = Package.objects.filter(wz=wz)
        elif package_last.wz!="" and package_last.wz!=None:
            packages = Package.objects.filter(wz=package_last.wz)
        else:
            packages = Package.objects.filter(delivery_date=package_last.delivery_date)



    context = {
    }
    #Print labels once again....
    #for package in packages:
    #    package.create_label()

    context['wz'] = Package.objects.order_by('-wz').values('wz').distinct()
    context['packages']=packages

    return render(request, url, context)

@login_required(login_url='/boards/loginlocal/')      
def packages_edit(request, *args, **kwargs):
    #wz = wz.replace("\\","QQQQ")
    #wz = wz.replace("/","qqqq")
    url = 'boards/packages_edit.html'
    context = {}
    pk = kwargs['pk']
    print(request.path_info)
    package = Package.objects.get(pk=pk)
    packageForm = PackageForm()
    packageForm.fields['delivery_date'].initial = package.delivery_date.isoformat()
    packageForm.fields['index'].initial = package.index

    packageForm.fields['supplier'].initial = package.supplier
    packageForm.fields['length'].initial = package.length
    packageForm.fields['wz'].initial = package.wz
    
    if request.method == 'POST':
        create_log(3,"", package.length,request.POST['length'], package.localisation, package.localisation, package.delivery_date, request.POST['delivery_date'] , request.user, "PC",request.POST['index'],package.pk,request.POST['supplier'],package.paczka,package.paczka,package.length_correction,package.length_correction)
        print(package,request.POST)
        package.delivery_date=request.POST['delivery_date']
        if request.POST['supplier']!="":
            package.supplier=Supplier.objects.get(pk=request.POST['supplier'])
        else:
            package.supplier=None
        package.index.pk=request.POST['index']
        package.length=request.POST['length']
        package.wz=request.POST['wz']
        package.save()
        if "/boards/packages_edit2/" in request.path_info:
            wz = remove_slash(request.POST['wz'])
            return HttpResponseRedirect("/boards/packages_delivery_edit/"+wz)
        else:
            return HttpResponseRedirect("/boards/packages/")

    #else:
        #packageForm = PackageForm()#instance = package
    context['PackageForm']=packageForm
    return render(request, url, context)
    
@login_required(login_url='/boards/loginlocal/')      
def packages_del(request,*args,**kwargs):
    pk = kwargs['pk']
    print(request)
    #### PackageThrash - NIe tworzy się - UTWORZYC NOWY MODEL POD THRASH
    #DeletedPackage.objects.create(pk=pk,index=Package.objects.get(pk=pk).index,supplier=Package.objects.get(pk=pk).supplier,delivery_date=Package.objects.get(pk=pk).delivery_date,length=Package.objects.get(pk=pk).length,localisation=Package.objects.get(pk=pk).localisation,wz=Package.objects.get(pk=pk).wz,length_initial_prd=Package.objects.get(pk=pk).length_initial_prd)
    DeletedPackage.objects.create(
                                    pk=pk,
                                    paczka=Package.objects.get(pk=pk).paczka,
                                    index=Package.objects.get(pk=pk).index,
                                    delivery_date=Package.objects.get(pk=pk).delivery_date,
                                    delivery_time=Package.objects.get(pk=pk).delivery_time,
                                    supplier=Package.objects.get(pk=pk).supplier,
                                    werk=Package.objects.get(pk=pk).werk,
                                    localisation=Package.objects.get(pk=pk).localisation,
                                    length=Package.objects.get(pk=pk).length,
                                    length_correction=Package.objects.get(pk=pk).length_correction,
                                    length_on_close=Package.objects.get(pk=pk).length_on_close,
                                    length_initial_prd=Package.objects.get(pk=pk).length_initial_prd,
                                    wz=Package.objects.get(pk=pk).wz,
                                    inventoried=False)



    
    Package.objects.get(pk=pk).delete()

    return HttpResponseRedirect("/boards/packages/")
def packages_del_delivery(request,*args,**kwargs):
    pk = kwargs['pk']
    print(request)
    #### PackageThrash - NIe tworzy się
    #DeletedPackage.objects.create(pk=pk,index=Package.objects.get(pk=pk).index,supplier=Package.objects.get(pk=pk).supplier,delivery_date=Package.objects.get(pk=pk).delivery_date,length=Package.objects.get(pk=pk).length,localisation=Package.objects.get(pk=pk).localisation,wz=Package.objects.get(pk=pk).wz,length_initial_prd=Package.objects.get(pk=pk).length_initial_prd)
    DeletedPackage.objects.create(
                                    pk=pk,
                                    paczka=Package.objects.get(pk=pk).paczka,
                                    index=Package.objects.get(pk=pk).index,
                                    delivery_date=Package.objects.get(pk=pk).delivery_date,
                                    delivery_time=Package.objects.get(pk=pk).delivery_time,
                                    supplier=Package.objects.get(pk=pk).supplier,
                                    werk=Package.objects.get(pk=pk).werk,
                                    localisation=Package.objects.get(pk=pk).localisation,
                                    length=Package.objects.get(pk=pk).length,
                                    length_correction=Package.objects.get(pk=pk).length_correction,
                                    length_on_close=Package.objects.get(pk=pk).length_on_close,
                                    length_initial_prd=Package.objects.get(pk=pk).length_initial_prd,
                                    wz=Package.objects.get(pk=pk).wz,
                                    inventoried=False)


    wz = Package.objects.get(pk=pk).wz
    wz = remove_slash(wz)
    Package.objects.get(pk=pk).delete() ### - ODBLOKUJ!!!!


    return HttpResponseRedirect("/boards/packages_delivery_edit/"+wz)
    
    
@login_required(login_url='/boards/loginlocal/')      
def suppliers_del(request, *args, **kwargs):
    pk = kwargs['pk']
    Supplier.objects.filter(pk=kwargs['pk']).delete()
    return HttpResponseRedirect("/boards/suppliers/")
@login_required(login_url='/boards/loginlocal/')      
def suppliers_add(request, *args, **kwargs):
    url = 'boards/suppliers_add.html'
    context = {}
    supplierForm=SupplierForm()
    if request.method == 'POST':
        #if indexForm.is_valid():
        supplier = Supplier()
        supplier.name = request.POST['name'] #indexForm.cleaned_data(name)
        supplier.save()
        return HttpResponseRedirect('/boards/suppliers/')
        #else:
        #    print(indexForm.errors)
    context['SupplierForm'] = supplierForm
    return render(request, url, context)

    return HttpResponseRedirect("/boards/suppliers/")
@login_required(login_url='/boards/loginlocal/')      
def indexes(request, *args, **kwargs):
    url = 'boards/indexes.html'
    indexes = Index.objects.all().order_by('name')
    if request.method == 'POST':
        try:
            print(request.POST)
            index = Index.objects.get(pk=request.POST['index'])
            index.name = request.POST['name']
            index.sap = request.POST['sap']
            #index.default_length = float(request.POST['default_length'])
            index.save()
        except:
            print("BLA")
    context = {
    }
    context['indexes']=indexes
    return render(request, url, context)
@login_required(login_url='/boards/loginlocal/')      
def indexes_del(request, *args, **kwargs):
    pk = kwargs['pk']
    Index.objects.filter(pk=kwargs['pk']).delete()
    return HttpResponseRedirect("/boards/indexes/")
@login_required(login_url='/boards/loginlocal/')      
def indexes_add(request, *args, **kwargs):
    url = 'boards/indexes_add.html'
    context = {

    }
    indexForm=IndexForm()
    if request.method == 'POST':
        #if indexForm.is_valid():
        index = Index()
        index.sap = request.POST['sap'] #indexForm.cleaned_data(sap)
        index.name = request.POST['name'] #indexForm.cleaned_data(name)
        index.save()
        return HttpResponseRedirect('/boards/indexes/')
        #else:
        #    print(indexForm.errors)
    context['IndexForm'] = indexForm
    return render(request, url, context)

         
@login_required(login_url='/boards/loginlocal/')      
def index_report3(request,*args,**kwargs):
    url = 'boards/index_report3.html'
    context = {        
    }
    indexes = []
    if request.method == 'POST':
#        print(request.POST['sap'])
#        sap = request.POST['sap']
        print(request.POST['wz'])
        wz = request.POST['wz']
    else:
        try:
            sap = ""
            wz = Package.objects.last().wz
        except:
            raise Http404

    #if sap!="": ## DO KOREKTY OD STRONY ALGORYTMU MOŻE JAKIEŚ LIST EXTENSION??? ALBO FILTER??
        #indexes = Index.objects.filter(sap__startswith=sap)    
    #    for i in Index.objects.filter(sap__startswith=sap):
    #        if Package.objects.filter(index=i).count()>0:
    #            indexes.append(i) 
    #else:
    packages = Package.objects.all()
    for i in Index.objects.all():
        if Package.objects.filter(wz=wz,index=i).count()>0:
            indexes.append(i) 

    reportrows = []
    ind_nr = 0

    for index in indexes:
        ind_nr += 1
        sum_MAG = Package.objects.filter(index=index,localisation="MAG",wz=wz).aggregate(Sum('length'))
        sum_PRD = Package.objects.filter(index=index,localisation="PRD",wz=wz).aggregate(Sum('length'))
        sum_ALL = Package.objects.filter(index=index,wz=wz).exclude(localisation="CLOSED").aggregate(Sum('length'))
        #reportline = ["I",f"{index.name} SAP: {index.sap}", f"Łącznie MAG: {sum_MAG['length__sum']} Łącznie PRD: {sum_PRD['length__sum']}"]
        lengthSumMag = sum_MAG['length__sum'] if sum_MAG['length__sum'] != None else 0.0
        lengthSumPrd = sum_PRD['length__sum'] if sum_PRD['length__sum'] != None else 0.0
        lengthSumAll = sum_ALL['length__sum'] if sum_ALL['length__sum'] != None else 0.0
        reportline = ["I",index.name, index.sap, lengthSumMag, lengthSumPrd, lengthSumAll, "tr"+str(ind_nr), "0", Package.objects.filter(wz=wz,index=index).exclude(localisation="CLOSED").count(),index.pk] 
        reportrows.append(reportline)
        row_nr = 0
        for package in Package.objects.filter(index=index,wz=wz).exclude(localisation="CLOSED").order_by('-localisation'): ##exclude(localisation="CLOSED")
            try:
                n = package.supplier.name
            except AttributeError:
                n = ""

            row_nr += 1
            #reportline = ["P","",n,package.delivery_date,package.localisation,package.length,"tr"+str(ind_nr), row_nr]
            barcode = ""
            for i in range(12-len(str(package.pk))):
                barcode = barcode+"0"
            barcode = barcode+str(package.pk)

            reportline = ["P",barcode,n,package.delivery_date,package.localisation,package.length,"tr"+str(ind_nr), row_nr, package.paczka]

            reportrows.append(reportline)
    wz_ = wz
    wz = wz.replace("\\","QQQQ")
    wz = wz.replace("/","qqqq")
    context['wz_'] = wz_
    context['wz'] = wz
    context['indexes'] = indexes
    context['packages'] = packages
    context['reportrows'] = reportrows
    context['labels'] = LABELS
    context['wz_list'] = Package.objects.values('wz').distinct()
    return render(request, url, context)



@login_required(login_url='/boards/loginlocal/')      
def index_report2(request,*args,**kwargs):
    url = 'boards/index_report2.html'
    context = {        
    }
    if request.method == 'POST':
        print(request.POST['sap'])
        sap = request.POST['sap']
    else:
        sap = ""

    if sap!="":
        indexes = Index.objects.filter(sap__startswith=sap)    
    else:
        indexes = Index.objects.all()
    packages = Package.objects.all()
    reportrows = []
    ind_nr = 0

    for index in indexes:
        ind_nr += 1
        sum_MAG = Package.objects.filter(index=index,localisation="MAG").aggregate(Sum('length'))
        sum_PRD = Package.objects.filter(index=index,localisation="PRD").aggregate(Sum('length'))
        sum_ALL = Package.objects.filter(index=index).exclude(localisation="CLOSED").aggregate(Sum('length'))
        #reportline = ["I",f"{index.name} SAP: {index.sap}", f"Łącznie MAG: {sum_MAG['length__sum']} Łącznie PRD: {sum_PRD['length__sum']}"]
        lengthSumMag = sum_MAG['length__sum'] if sum_MAG['length__sum'] != None else 0.0
        lengthSumPrd = sum_PRD['length__sum'] if sum_PRD['length__sum'] != None else 0.0
        lengthSumAll = sum_ALL['length__sum'] if sum_ALL['length__sum'] != None else 0.0

        reportline = ["I",index.name, index.sap, lengthSumMag, lengthSumPrd, lengthSumAll, "tr"+str(ind_nr), "0",index.pk] 



        reportrows.append(reportline)
        row_nr = 0
        for package in Package.objects.filter(index=index).exclude(localisation="CLOSED").order_by('-localisation'):
            try:
                n = package.supplier.name
            except AttributeError:
                n = ""

            row_nr += 1
            #reportline = ["P","",n,package.delivery_date,package.localisation,package.length,"tr"+str(ind_nr), row_nr]
            barcode = ""
            for i in range(12-len(str(package.pk))):
                barcode = barcode+"0"
            barcode = barcode+str(package.pk)

            reportline = ["P",barcode,n,package.delivery_date,package.localisation,package.length,"tr"+str(ind_nr), row_nr,package.paczka]

            reportrows.append(reportline)
        
    context['indexes'] = indexes
    context['packages'] = packages
    context['reportrows'] = reportrows
    context['labels'] = LABELS
    return render(request, url, context)

@login_required(login_url='/boards/loginlocal/')      
def index_report(request,*args,**kwargs):
    url = 'boards/index_report.html'
    context = {        
    }
    if request.method == 'POST':
        print(request.POST['sap'])
        sap = request.POST['sap']
    else:
        sap = ""

    if sap!="":
        indexes = Index.objects.filter(sap__startswith=sap)    
    else:
        indexes = Index.objects.all()    
    packages = Package.objects.all()
    reportrows = []
    for index in indexes:
        sum_MAG = Package.objects.filter(index=index,localisation="MAG").aggregate(Sum('length'))
        sum_PRD = Package.objects.filter(index=index,localisation="PRD").aggregate(Sum('length'))


        reportline = ["I",f"{index.name} SAP: {index.sap}", f"Łącznie MAG: {sum_MAG['length__sum']} Łącznie PRD: {sum_PRD['length__sum']}"]
        
        reportrows.append(reportline)
        for package in Package.objects.filter(index=index).exclude(localisation="CLOSED").order_by('-localisation'):
            try:
                n = package.supplier.name
            except AttributeError:
                n = ""


            reportline = ["P","",n,package.delivery_date,package.localisation,package.length]
            reportrows.append(reportline)
        
    context['indexes'] = indexes
    context['packages'] = packages
    context['reportrows'] = reportrows
    return render(request, url, context)

@login_required(login_url='/boards/loginlocal/')      
def suppliers_report(request, *args, **kwargs):

    url = 'boards/suppliers_report.html'
    reportrows = []
    suppliers = Supplier.objects.all() # DODAJ FILTER
    for supplier in suppliers:
        sum_MAG = Package.objects.filter(localisation="MAG",supplier=supplier).aggregate(Sum('length'))
        sum_PRD = Package.objects.filter(localisation="PRD",supplier=supplier).aggregate(Sum('length'))
        sum_ALL = Package.objects.filter(supplier=supplier).exclude(localisation="CLOSED").aggregate(Sum('length'))
        sum_MAG_ = sum_MAG['length__sum'] if sum_MAG['length__sum']!=None else ""
        sum_PRD_ = sum_PRD['length__sum'] if sum_PRD['length__sum']!=None else ""
        sum_ALL_ = sum_ALL['length__sum'] if sum_ALL['length__sum']!=None else ""

        reportrow =(supplier.name,"",sum_MAG_,sum_PRD_,sum_ALL_,"D")
        reportrows.append(reportrow)
        for index in Index.objects.all():
            sum_MAG = Package.objects.filter(index=index,localisation="MAG",supplier=supplier).aggregate(Sum('length')) 
            sum_PRD = Package.objects.filter(index=index,localisation="PRD",supplier=supplier).aggregate(Sum('length'))
            sum_ALL = Package.objects.filter(index=index,supplier=supplier).exclude(localisation="CLOSED").aggregate(Sum('length'))
            sum_MAG_ = sum_MAG['length__sum'] if sum_MAG['length__sum']!=None else ""
            sum_PRD_ = sum_PRD['length__sum'] if sum_PRD['length__sum']!=None else ""
            sum_ALL_ = sum_ALL['length__sum'] if sum_ALL['length__sum']!=None else ""
            reportrow = (index.sap,  index.name,sum_MAG_,sum_PRD_,sum_ALL_,"I")
            reportrows.append(reportrow)

    context = {
        'reportrows': reportrows,
        'labels':LABELS,
    }

    return render(request, url, context)




def print_label(request, *args, **kwargs):
    pk = kwargs['pk']
    prt = kwargs['prt']
#    try:
    package = Package.objects.get(pk=pk)
    package.create_label(False,LABELS)
    if prt =="view":

        package.create_label_large(False,LABELS,False)            
        with open('tmp/etykieta_large.pdf', 'rb') as pdf:
            response = HttpResponse(pdf.read(), content_type='application/pdf')
            response['Content-Disposition'] = 'filename=tmp/etykieta_large.pdf'
            return response
        pdf.closed
    else:
        print(pk)
        print(package, package.pk)
        package.create_label_large(True,LABELS,True)

        

#    except:
#        print("BLAD")
#        raise Http404
    return HttpResponseRedirect("/boards/packages_delivery_edit/")




@csrf_exempt
def scanner_load(request):
    #poststream = request.POST['typ']
    #typ = poststream.split("|")[0]
    #print(typ)
    #request_ = {}
    #for posts in poststream.split("|")[1:]:
    #    request_[posts.split("=")[0]]=posts.split("=")[1]
    #print(request_)
    #print("request",request.POST)
    typ = request.POST['typ']

    username = request.POST['username'][:14]
    print(username)
    scanner = request.POST['scanner'][:14]

    


    sap_str = ""
    if typ == "indexy":

        indexy = Index.objects.all()
        
        for i in indexy:
            sap_str+=f"{i.sap} | {i.name}  |  {i.pk};" 
    elif typ == "dostawcy":
        suppliers = Supplier.objects.all()
        for i in suppliers:
            sap_str+=f"{i.name} | {i.pk};" 
    if typ == "create_delivery":
        sap_str="OK"
        print(f"{request.POST['index']} {request.POST['supplier']} {request.POST['qty']} {request.POST['delivery_date']} {request.POST['length']}")
        try:
            for number in range(1,int(request.POST['qty'])+1):
                index = Index.objects.get(pk=request.POST['index'])
                supplier = Supplier.objects.get(pk=request.POST['supplier'])
                delivery_date = request.POST['delivery_date']  ## Uwaga na format!!!
                length = request.POST['length']

                package = Package.objects.create(index=index,supplier=supplier,delivery_date=request.POST['delivery_date'],localisation='MAG',length=length)
                supplier_pk = package.supplier.pk if package.supplier!=None else "0"
                create_log(0,"", package.length,package.length, package.localisation, "MAG", package.delivery_date, package.delivery_date,username,scanner,package.index.pk,package.pk,supplier_pk,package.length_correction,package.length_correction)
                package.create_label()
            sap_str = f"utworzono {request.POST['qty']} paczek/paczki {request.POST['index']}"
        except:
            sap_str = f"Problem z utworzeniem paczek {request.POST['index']}"

            #package.create_label()
    if  typ == "read_package":
        try:
            package = Package.objects.get(pk=request.POST['package'].lstrip("0"))
            supplier = package.supplier.name if package.supplier!=None else ""
            t = (package.index.name,supplier,str(package.length),str(package.delivery_date),package.localisation,str(package.pk),package.paczka,str(package.length_correction))
            sap_str = "|".join(t)
        except: 
            return HttpResponse(f"Obiekt {request.POST['package']} nie istnieje")
    if typ == "warehouse_package":
        #try:
        package = Package.objects.get(pk=request.POST['package'].lstrip("0"))
        supplier_pk = package.supplier.pk if package.supplier!=None else "0"
        create_log(0,"", package.length,request.POST['length'], package.localisation, "MAG", package.delivery_date, package.delivery_date, username, scanner,package.index.pk,package.pk,supplier_pk,package.paczka,request.POST['paczka'],package.length_correction,package.length_correction)            
        print(package.length,request.POST['length'])
        update_utilisation(typ, package.length,request.POST['length'], package.index.pk)
        
        

        package.localisation = "MAG"
        package.length = request.POST['length']
        package.paczka = request.POST['paczka']
        package.save()
        sap_str =(f"Paczka {request.POST['package']} wprowadzona na magazyn")

        #except: 
        #    return HttpResponse(f"Obiekt {request.POST['package']} nie istnieje")

    if typ == "rewarehouse_package":
        #try:
        package = Package.objects.get(pk=request.POST['package'].lstrip("0"))
        if float(request.POST['length']) <= package.length_initial_prd:

            supplier_pk = package.supplier.pk if package.supplier!=None else "0"
            create_log(0,"", package.length,request.POST['length'], package.localisation, "MAG", package.delivery_date, package.delivery_date, username, scanner,package.index.pk,package.pk,supplier_pk,package.paczka,request.POST['paczka'],package.length_correction,package.length_correction)            
            print(package.length,request.POST['length'])
            update_utilisation(typ, package.length,request.POST['length'], package.index.pk)
            
            

            package.localisation = "MAG"
            package.length = request.POST['length']
            package.paczka = request.POST['paczka']
            package.save()
            sap_str =(f"Paczka {request.POST['package']} wprowadzona na magazyn")
        else:
            return HttpResponse(f"ZA DŁUGA!!!! NIE ZAMKNIĘTO!!! ZAMKNIJ PONOWNIE!!!!")


        #except: 
        #    return HttpResponse(f"Obiekt {request.POST['package']} nie istnieje")

    if typ == "warehouse_package_update":
        try:
            package = Package.objects.get(pk=request.POST['package'].lstrip("0"))
            supplier_pk = package.supplier.pk if package.supplier!=None else "0"
            create_log(4,"", package.length,request.POST['length'], package.localisation, "MAG", package.delivery_date, package.delivery_date, username, scanner,package.index.pk,package.pk,supplier_pk,package.paczka,request.POST['paczka'],package.length_correction,package.length_correction)
            update_utilisation(typ, package.length,request.POST['length'], package.index.pk)
            package.localisation = "MAG"
            package.length = request.POST['length']
            package.paczka = request.POST['paczka']
            #package.paczka = request.POST['paczka'] if request.POST['paczka'].strip()!="" else package.paczka

            package.save()
            sap_str =(f"Paczka {request.POST['package']} zaktualizowana")

        except: 
            return HttpResponse(f"Obiekt {request.POST['package']} nie istnieje")


    if typ == "release_package":
        try:
            package = Package.objects.get(pk=request.POST['package'].lstrip("0"))
            supplier_pk = package.supplier.pk if package.supplier!=None else "0"

            create_log(1,"", package.length,request.POST['length'], package.localisation, "PRD", package.delivery_date, package.delivery_date, username, scanner,package.index.pk,package.pk,supplier_pk,package.paczka,package.paczka,package.length_correction,package.length_correction)
            update_utilisation(typ, package.length,request.POST['length'], package.index.pk)
            package.localisation = "PRD"
            package.length = request.POST['length']
            package.length_initial_prd = request.POST['length']

            package.save()
            sap_str =(f"Paczka {request.POST['package']} przekazana na produkcję")

        except: 
            return HttpResponse(f"Obiekt {request.POST['package']} nie istnieje")

    if typ == "close_package":
#        print("aa")

        try:
            package = Package.objects.get(pk=request.POST['package'].lstrip("0"))
            if float(request.POST['length']) <= package.length_initial_prd:
                supplier_pk = package.supplier.pk if package.supplier!=None else "0"

                #create_log(2,"", package.length,request.POST['length'], package.localisation, "CLOSED", package.delivery_date, package.delivery_date,username,scanner,package.index.pk,package.pk,supplier_pk,package.paczka,package.paczka)
                create_log(2,"", package.length,0, package.localisation, "CLOSED", package.delivery_date, package.delivery_date,username,scanner,package.index.pk,package.pk,supplier_pk,package.paczka,package.paczka,package.length_correction,package.length_correction)
                update_utilisation(typ, package.length,0, package.index.pk)

                package.localisation = "CLOSED"
                package.length = 0 #request.POST['length']
                package.length_on_close = request.POST['length']

                package.save()
                sap_str =(f"Paczka {request.POST['package']} została zakończona")
            else:
                return HttpResponse(f"ZA DŁUGA!!!! NIE ZAMKNIĘTO!!! ZAMKNIJ PONOWNIE!!!!")

        except: 
            return HttpResponse(f"Obiekt {request.POST['package']} nie istnieje")

    if typ == "update_length":
        try:
            print(request.POST)
            package = Package.objects.get(pk=request.POST['package'].lstrip("0"))
            if float(request.POST['length']) <= package.length_initial_prd:

                supplier_pk = package.supplier.pk if package.supplier!=None else "0"
                
                if package.length != float(request.POST['length']) or (request.POST['paczka'].strip()!="" and package.paczka != request.POST['paczka']):
                    create_log(4,"", package.length,request.POST['length'], package.localisation, package.localisation, package.delivery_date, package.delivery_date,username,scanner,package.index.pk,package.pk,supplier_pk,package.paczka,package.paczka,package.length_correction,package.length_correction)
                    update_utilisation(typ, package.length,request.POST['length'], package.index.pk)
                    package.length = request.POST['length']
                    package.paczka = request.POST['paczka'] if request.POST['paczka'].strip()!="" else package.paczka

                    package.save()
                    sap_str =(f"Paczka {request.POST['package']} ZOSTAŁA ZMODYFIKOWANA")
                else:
                    sap_str =(f"Dlugość paczki {request.POST['package']} NIE ULEGŁA ZMIANIE")
            else:
                return HttpResponse(f"ZA DŁUGA!!!! NIE ZAMKNIĘTO!!! ZAMKNIJ PONOWNIE!!!!")



        except: 
            return HttpResponse(f"Obiekt {request.POST['package']} nie istnieje")

    if typ == "update_correction":
        try:
            package = Package.objects.get(pk=request.POST['package'].lstrip("0"))
            if float(request.POST['length_correction']) <= package.length_initial_prd:
                supplier_pk = package.supplier.pk if package.supplier!=None else "0"

                if package.length_correction != float(request.POST['length_correction']):

                    ##Dodajemy log z dla korekty
                    create_log(6,"", package.length,package.length, package.localisation, package.localisation, package.delivery_date, package.delivery_date,username,scanner,package.index.pk,package.pk,supplier_pk,package.paczka,package.paczka, package.length_correction, request.POST['length_correction']) 
                    ## Korekta będzie doliczana na etapie zamknięcia belki.
                    #update_utilisation(typ, package.length,request.POST['length'], package.index.pk)
                    package.length_correction = request.POST['length_correction'] ###correction

                    package.save()
                    sap_str =(f"Korekta paczki {request.POST['package']}  ZMODYFIKOWANA")
                else:
                    sap_str =(f"Korekta paczki {request.POST['package']} NIE ULEGŁA ZMIANIE!!!")
            else:
                return HttpResponse(f"ZA DUŻA KOREKTA!!!! NIE WPROWADZONO!!! ZAMKNIJ PONOWNIE!!!!")

        except: 
            return HttpResponse(f"Obiekt {request.POST['package']} nie istnieje")

    if typ == "inventory":
            package = Package.objects.get(pk=request.POST['package'].lstrip("0"))
            index = package.index
            supplier_pk = package.supplier.pk if package.supplier!=None else "0"
            inv = inventory.objects.get(name="INWENTURA")
            print(request.POST['length'])
            create_LogInventory(name = "INWENTURA", 
                                inv_pk = inv.pk,
                                package_pk = package.pk,
                                index_pk = index.pk,
                                scanner = scanner,
                                userid = "",
                                username = username,
                                length_before = package.length,
                                length_after = request.POST['length'],
                                localisation_before = package.localisation,
                                localisation_after = package.localisation, 
                                paczka_before = package.paczka, 
                                paczka_after = package.paczka)
            create_log(7,"", package.length,request.POST['length'], package.localisation, package.localisation, package.delivery_date, package.delivery_date,username,scanner,package.index.pk,package.pk,supplier_pk,package.paczka,package.paczka,package.length_correction,package.length_correction)
            package.length = request.POST['length']
            package.inventoried = True
            package.save()
            return HttpResponse(f"Zinwentaryzowano {request.POST['package']}")


    if typ == "edit_delivery":
        sap_str="OK"
        print(f"{request.POST['package']}  {request.POST['index']} {request.POST['supplier']} {request.POST['delivery_date']} {request.POST['length']} {request.POST['localisation']}")
        index = Index.objects.get(pk=request.POST['index'])
        print(index)
        supplier = Supplier.objects.get(pk=request.POST['supplier'])
        print(supplier)
        delivery_date = request.POST['delivery_date']  ## Uwaga na format!!!
        length = request.POST['length']
        try:
            package = Package.objects.get(pk=request.POST['package'])
            supplier_pk = package.supplier.pk if package.supplier!=None else "0"
            create_log(3,"", package.length,length, package.localisation, request.POST['localisation'], package.delivery_date, request.POST['delivery_date'],username,scanner,package.index.pk,package.pk,supplier_pk,package.paczka,package.paczka,package.length_correction,package.length_correction)

            package.index=index
            package.supplier=supplier
            package.length = length
            package.delivery_date=request.POST['delivery_date']
            package.localisation=request.POST['localisation']
            package.save()
            sap_str = f"Paczka {request.POST['package']} została zmodyfikowana"
        except:
            sap_str = f"Wystąpił problem z modyfikacją paczki {request.POST['package']}"


        #package = Package.objects.create(index=index,supplier=supplier,delivery_date=request.POST['delivery_date'],localisation=request.POST['localisation'])
        #package.create_label()


    if typ =="login":
        print(request.POST['id'])
        print(request.POST['host'])
        print(request.POST['name'])
        CurrentUser.objects.create(userid=request.POST['id'],host=request.POST['host'],name=request.POST['name'])
        sap_str="Login"

        print("login")


    if typ =="logout":
        sap_str="Logout"
        print(request.POST['host'])
        CurrentUser.objects.filter(host=request.POST['host']).delete()
    
        print("logon")

    #if typ == 'host':
    #    hostname = request.POST['hostname']
    #    print(hostname)
    #    sap_str=hostname
    return HttpResponse(sap_str)

@csrf_exempt
def scanner_load2(request):
    #print(request)
    return ("nie istnieje")
class PackageViewSet(viewsets.ModelViewSet):
    queryset = Package.objects.all()
    serializer_class = PackageSerializer
class IndexViewSet(viewsets.ModelViewSet):
    queryset = Index.objects.all()
    serializer_class = IndexSerializer
class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer

@csrf_exempt
def scanner_load3_read_package(request,*args,**kwargs):
    try:
        package = Package.objects.get(pk=kwargs['pk'].lstrip('0'))
        t = (package.index.name,package.supplier.name,str(package.length),str(package.delivery_date),package.localisation,str(package.pk),package.paczka,package.paczka)
        sap_str = "|".join(t)
    except: 
        return HttpResponse(f"Obiekt {kwargs['pk']} nie istnieje")
    return HttpResponse(sap_str)
@csrf_exempt
def scanner_load3_warehouse_package(request,*args,**kwargs):
    try:
        package = Package.objects.get(pk=kwargs['pk'].lstrip("0"))
        create_log(0,"", package.length,kwargs['length'], package.localisation, "MAG", package.delivery_date, package.delivery_date,package.paczka,package.paczka, package.length_correction,package.length_correction)
        package.localisation = "MAG"
        package.length = kwargs['length'].lstrip('0')
        package.save()
        sap_str =(f"Paczka {kwargs['pk']} wprowadzona na magazyn")

    except: 
        return HttpResponse(f"Obiekt {kwargs['pk']} nie istnieje")
    return HttpResponse(sap_str)
@csrf_exempt
def scanner_load3_prd_package(request,*args,**kwargs):
    try:
        package = Package.objects.get(pk=kwargs['pk'].lstrip("0"))
        create_log(0,"", package.length,kwargs['length'], package.localisation, "PRD", package.delivery_date, package.delivery_date,package.paczka,package.paczka,package.length_correction,package.length_correction)
        package.localisation = "PRD"
        package.length = kwargs['length'].lstrip('0')
        package.save()
        sap_str =(f"Paczka {kwargs['pk']} przekazana na produkcję")

    except: 
        return HttpResponse(f"Obiekt {kwargs['pk']} nie istnieje")
    return HttpResponse(sap_str)
@csrf_exempt
def scanner_load3_closed_package(request,*args,**kwargs):
    try:
        package = Package.objects.get(pk=kwargs['pk'].lstrip("0"))
        create_log(0,"", package.length,kwargs['length'], package.localisation, "CLOSED", package.delivery_date, package.delivery_date,package.paczka,package.paczka,package.length_correction,package.length_correction)
        package.localisation = "CLOSED"
        package.length = kwargs['length'].lstrip('0')
        package.save()
        sap_str =(f"Paczka {kwargs['pk']} zakończona")

    except: 
        return HttpResponse(f"Obiekt {kwargs['pk']} nie istnieje")
    return HttpResponse(sap_str)
@csrf_exempt
def scanner_load3_login(request,*args,**kwargs):
    try:
        CurrentUser.objects.create(userid=kwargs['id'],host=kwargs['host'],name=kwargs['name'])
        sap_str="Login"
    except:
        sap_str="Login ERROR"

    return HttpResponse(sap_str)
@csrf_exempt
def scanner_load3_logout(request,*args,**kwargs):
    try:
        sap_str="Logout"
        CurrentUser.objects.filter(host=kwargs['host']).delete() 
        print("logout")
    except:
        sap_str="Logout ERROR"
    return HttpResponse(sap_str)
def inventory_rep(request, *args, **kwargs):
    url='boards/inventory_rep.html'
    context = {}
    inventories = inventory.objects.all()
    if request.method == 'POST':
        if request.POST['locs'] == "WSZYSTKIE":
            #print("LOL",request.POST['inventories'])
            logInventories = LogInventory.objects.filter(inventory_name=request.POST['inventories']).exclude(localisation_after="DOST").exclude(localisation_after="CLOSED")
        elif request.POST['locs'] == "MAG":
            logInventories = LogInventory.objects.filter(inventory_name=request.POST['inventories'],localisation_after="MAG")
        elif request.POST['locs'] == "PRD":
            logInventories = LogInventory.objects.filter(inventory_name=request.POST['inventories'],localisation_after="PRD")

    else:
        logInventories = LogInventory.objects.filter(inventory_name="INWENTURA")
    rows = []
    for index in Index.objects.all():
        row = {}
        row['index']  = index
        row['package_qty'] = logInventories.filter(index=index).count()
        row['package_length'] = logInventories.filter(index=index).aggregate(Sum('length_after'))
        row['rowtype'] = "HEADER"
        rows.append(row)
        ##W zależnosci od checka w formularzu wyrzucaj tylko zinwentaryzowane lub wszystkie i koloruj zinwentaryzowane
        if "full" not in request.POST.keys():
            for package in logInventories.filter(index=index):
                row = {}
                #row['package'] =  package.package
                #print(len(str(package.package_barcode)))
                row['package'] = (12-len(str(package.package_barcode)))*"0" + package.package_barcode
                row['length_after'] =  package.length_after
                row['paczka_after'] =  package.paczka_after
                row['rowtype']="ROW"
                rows.append(row)
        else:
            if request.POST['locs'] == "WSZYSTKIE":
               packages = Package.objects.filter(index=index).exclude(localisation="DOST").exclude(localisation="CLOSED")
            else:
               packages = Package.objects.filter(index=index, localisation=request.POST['locs']).exclude(localisation="DOST").exclude(localisation="CLOSED")

            
            #for package in Package.objects.filter(index=index).exclude(localisation="DOST").exclude(localisation="CLOSED"):
            for package in packages:
                row = {}
                #row['package'] =  package.package
                #print(len(str(package.pk)))
                row['package'] = (12-len(str(package.pk)))*"0" + str(package.pk)
                row['length_after'] =  package.length
                row['paczka_after'] =  package.paczka
                row['rowtype']="ROW"
                if logInventories.filter(package_barcode=package.pk).count()>0:
                    row['inventored']="T"
                else:
                    row['inventored']="N"

                
                rows.append(row)



    locs = ("WSZYSTKIE","MAG","PRD")
    context['locs'] = LOCS
    context['rows'] = rows
    context['labels'] =LABELS
    context['inventories'] = inventories
    context['logInventories']=logInventories
    return render(request,url,context)
