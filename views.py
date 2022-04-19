from ast import Index
from pdb import post_mortem
import re
from socket import PACKET_LOOPBACK
from threading import local
from time import sleep
from urllib import request, response
from urllib.error import HTTPError
from venv import create
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.views.decorators.csrf import csrf_exempt
from  datetime import date
from django.db.models import Sum
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets
from .models import IndexForm, Index, Supplier, PackageForm, Package
from .models import PackageTrash, IndexForm, SupplierForm, CurrentUser
from .functions import create_log
from .serializers import IndexSerializer, SupplierSerializer, PackageSerializer
from .forms import LoginForm


# Create your views here.
    

LABELS = {
    'package_supplier':'DOSTAWCA',
    'index_sap':'SAP',
    'index_name':'NAZWA',
    'package_pk':'ID PACZKI',
    'package_paczka':'PACZKA',
    'package_delivery_date':'DATA DOSTAWY',
    'package_localisation':'LOKALIZACJA',
    'package_length':'DŁUGOŚĆ',
    'package_wz':'WZ',

}

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
        packages = Package.objects.all().order_by(request.POST['sort'])
        context['actual_sort'] = request.POST['sort']

    else:
        packages = Package.objects.all().order_by('-pk')
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

    
    if request.method == 'POST':
        packages = Package.objects.filter(wz=request.POST['wz']) if request.POST['wz']!="" else Package.objects.all()
    else:

        package_last=Package.objects.latest('id')
        if package_last.wz!="" and package_last.wz!=None:
            packages = Package.objects.filter(wz=package_last.wz)
        else:
            packages = Package.objects.filter(delivery_date=package_last.delivery_date)



    context = {
    }
    #Print labels once again....
    #for package in packages:
    #    package.create_label()

    context['wz'] = Package.objects.order_by('wz').values('wz').distinct()
    context['packages']=packages

    return render(request, url, context)

@login_required(login_url='/boards/loginlocal/')      
def packages_edit(request, *args, **kwargs):
    url = 'boards/packages_edit.html'
    context = {}
    pk = kwargs['pk']
    package = Package.objects.get(pk=pk)
    packageForm = PackageForm()
    packageForm.fields['delivery_date'].initial = package.delivery_date.isoformat()
    packageForm.fields['index'].initial = package.index

    packageForm.fields['supplier'].initial = package.supplier
    packageForm.fields['length'].initial = package.length
    packageForm.fields['wz'].initial = package.wz
    
    if request.method == 'POST':
        print(package,request.POST)
        package.delivery_date=request.POST['delivery_date']
        if request.POST['supplier']!="":
            package.supplier=Supplier.objects.get(pk=request.POST['supplier'])
        else:
            package.supplier=None
        package.index.pk=request.POST['index']
        package.length=request.POST['length']
        package.save()
        return HttpResponseRedirect("/boards/packages_delivery_edit/")


    #else:

        
        #packageForm = PackageForm()#instance = package
    context['PackageForm']=packageForm
    return render(request, url, context)
@login_required(login_url='/boards/loginlocal/')      
def packages_del(request,*args,**kwargs):
    pk = kwargs['pk']
    PackageTrash.objects.create(pk=pk,index=Package.objects.get(pk=pk).index,supplier=Package.objects.get(pk=pk).supplier,delivery_date=Package.objects.get(pk=pk).delivery_date,length=Package.objects.get(pk=pk).length,localisation=Package.objects.get(pk=pk).localisation)
    Package.objects.get(pk=pk).delete()
    return HttpResponseRedirect("/boards/packages/")
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
        sap = ""
        wz = Package.objects.last().wz

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

            reportline = ["P",barcode+"/"+package.paczka,n,package.delivery_date,package.localisation,package.length,"tr"+str(ind_nr), row_nr,"0"]

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

            reportline = ["P",barcode+"/"+package.paczka,n,package.delivery_date,package.localisation,package.length,"tr"+str(ind_nr), row_nr,"0"]

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
                create_log(0,"", package.length,package.length, package.localisation, "MAG", package.delivery_date, package.delivery_date,username,scanner,package.index.pk,package.pk,supplier_pk)
                package.create_label()
            sap_str = f"utworzono {request.POST['qty']} paczek/paczki {request.POST['index']}"
        except:
            sap_str = f"Problem z utworzeniem paczek {request.POST['index']}"

            #package.create_label()
    if  typ == "read_package":
        try:
            package = Package.objects.get(pk=request.POST['package'].lstrip("0"))
            supplier = package.supplier.name if package.supplier!=None else ""
            t = (package.index.name,supplier,str(package.length),str(package.delivery_date),package.localisation,str(package.pk),package.paczka)
            sap_str = "|".join(t)
        except: 
            return HttpResponse(f"Obiekt {request.POST['package']} nie istnieje")
    if typ == "warehouse_package":
        try:
            package = Package.objects.get(pk=request.POST['package'].lstrip("0"))
            supplier_pk = package.supplier.pk if package.supplier!=None else "0"
            create_log(0,"", package.length,request.POST['length'], package.localisation, "MAG", package.delivery_date, package.delivery_date, username, scanner,package.index.pk,package.pk,supplier_pk,package.paczka,request.POST['paczka'])
            package.localisation = "MAG"
            package.length = request.POST['length']
            package.paczka = request.POST['paczka']
            package.save()
            sap_str =(f"Paczka {request.POST['package']} wprowadzona na magazyn")

        except: 
            return HttpResponse(f"Obiekt {request.POST['package']} nie istnieje")

    if typ == "warehouse_package_update":
        try:
            package = Package.objects.get(pk=request.POST['package'].lstrip("0"))
            supplier_pk = package.supplier.pk if package.supplier!=None else "0"
            create_log(4,"", package.length,request.POST['length'], package.localisation, "MAG", package.delivery_date, package.delivery_date, username, scanner,package.index.pk,package.pk,supplier_pk,package.paczka,request.POST['paczka'])
            package.localisation = "MAG"
            package.length = request.POST['length']
            package.paczka = request.POST['paczka']
            package.save()
            sap_str =(f"Paczka {request.POST['package']} zaktualizowana")

        except: 
            return HttpResponse(f"Obiekt {request.POST['package']} nie istnieje")


    if typ == "release_package":
        try:
            package = Package.objects.get(pk=request.POST['package'].lstrip("0"))
            supplier_pk = package.supplier.pk if package.supplier!=None else "0"

            create_log(1,"", package.length,request.POST['length'], package.localisation, "PRD", package.delivery_date, package.delivery_date, username, scanner,package.index.pk,package.pk,supplier_pk,package.paczka,package.paczka)
            package.localisation = "PRD"
            package.length = request.POST['length']
            package.save()
            sap_str =(f"Paczka {request.POST['package']} przekazana na produkcję")

        except: 
            return HttpResponse(f"Obiekt {request.POST['package']} nie istnieje")

    if typ == "close_package":
        try:
            package = Package.objects.get(pk=request.POST['package'].lstrip("0"))
            supplier_pk = package.supplier.pk if package.supplier!=None else "0"

            create_log(2,"", package.length,request.POST['length'], package.localisation, "CLOSED", package.delivery_date, package.delivery_date,username,scanner,package.index.pk,package.pk,supplier_pk,package.paczka,package.paczka)
            package.localisation = "CLOSED"
            package.length = request.POST['length']
            package.save()
            sap_str =(f"Paczka {request.POST['package']} została zakończona")

        except: 
            return HttpResponse(f"Obiekt {request.POST['package']} nie istnieje")

    if typ == "update_length":
        #try:
        print(request.POST)
        package = Package.objects.get(pk=request.POST['package'].lstrip("0"))
        supplier_pk = package.supplier.pk if package.supplier!=None else "0"
        if package.length != float(request.POST['length']) or (request.POST['paczka'].strip()!="" and package.paczka != request.POST['paczka']):
            create_log(4,"", package.length,request.POST['length'], package.localisation, package.localisation, package.delivery_date, package.delivery_date,username,scanner,package.index.pk,package.pk,supplier_pk,package.paczka,package.paczka)
            package.length = request.POST['length']
            package.paczka = request.POST['paczka'] if request.POST['paczka'].strip()!="" else package.paczka

            package.save()
            sap_str =(f"Paczka {request.POST['package']} ZOSTAŁA ZMODYFIKOWANA")
        else:
            sap_str =(f"Dlugość paczki {request.POST['package']} NIE ULEGŁA ZMIANIE")



        #except: 
        #    return HttpResponse(f"Obiekt {request.POST['package']} nie istnieje")


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

            create_log(3,"", package.length,length, package.localisation, request.POST['localisation'], package.delivery_date, request.POST['delivery_date'],username,scanner,package.index.pk,package.pk,supplier_pk,package.paczka,package.paczka)

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
        create_log(0,"", package.length,kwargs['length'], package.localisation, "MAG", package.delivery_date, package.delivery_date,package.paczka,package.paczka)
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
        create_log(0,"", package.length,kwargs['length'], package.localisation, "PRD", package.delivery_date, package.delivery_date,package.paczka,package.paczka)
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
        create_log(0,"", package.length,kwargs['length'], package.localisation, "CLOSED", package.delivery_date, package.delivery_date,package.paczka,package.paczka)
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