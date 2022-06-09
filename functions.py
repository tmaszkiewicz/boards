import datetime
from .models import Log,Index,Supplier,Package,DayQuantity,LogInventory,inventory

def remove_slash(slug):
    slug = slug.replace("\\","QQQQ") # CLUTCH SOLUTION
    slug = slug.replace("/","qqqq")
    return slug

def return_slash(slug):
    slug = slug.replace("QQQQ","\\") # CLUTCH SOLUTION
    slug = slug.replace("qqqq","/")
    return slug



    return
#def package_label(package):
def delivery_print():
    print("test")
    pass
def create_LogInventory(name, inv_pk, package_pk,index_pk,scanner,userid,username,length_before,length_after,localisation_before,localisation_after, paczka_before, paczka_after):
    logInventory = LogInventory()
    LogInventory.objects.get_or_create(
        inventory_name = name,
        inventory = inventory.objects.get(pk=inv_pk),
        package = Package.objects.get(pk=package_pk),
        index = Index.objects.get(pk=index_pk)
        )
    logInventory = LogInventory.objects.get(
        inventory_name = name,
        package = Package.objects.get(pk=package_pk),
        index = Index.objects.get(pk=index_pk)
    )
    #logInventory.inventory_name = name
    #logInventory.package = Package.objects.get(pk=package_pk)
    #logInventory.index = Index.objects.get(pk=index_pk)
    logInventory.scanner = scanner
    logInventory.userid = userid
    logInventory.username = username
    logInventory.length_before = length_before
    logInventory.length_after = length_after
    logInventory.localisation_before = localisation_before
    logInventory.localisation_after = localisation_after
    logInventory.paczka_before = paczka_before
    logInventory.paczka_after = paczka_after

    logInventory.package_barcode = logInventory.package.pk
    logInventory.index_name = logInventory.index.name
    logInventory.index_sap = logInventory.index.sap


    logInventory.save()
    
    return("OK")


def create_log(operation, userid, length_before,length_after,localisation_before,localisation_after,delivery_date_before,delivery_date_after,username,scanner,index_pk,package_pk,supplier_pk,paczka_before,paczka_after,length_correction_before,length_correction_after):
    #try:
    log = Log()
    log.index_before=Index.objects.get(pk=index_pk) 
    if supplier_pk != "0":
        log.supplier_before=Supplier.objects.get(pk=supplier_pk)
    log.package=Package.objects.get(pk=package_pk)  
    print(log.index_before)
    log.operation = operation
    log.scanner = scanner
    log.userid = userid
    log.username = username
    log.length_before = length_before
    log.length_after = length_after
    log.length_correction_before = length_correction_before
    log.length_correction_after = length_correction_after
    log.localisation_before = localisation_before
    log.localisation_after = localisation_after
    log.delivery_date_before = delivery_date_before
    log.delivery_date_after= delivery_date_after
    log.paczka_before= paczka_before
    log.paczka_after= paczka_after

    log.save()
    return "OK"
    #except:
    #    return "NOK"
def update_utilisation(operation, length_before, length_after, index_pk):

    index = Index.objects.get(pk=index_pk)
    current_date = datetime.date.today()
    dayq = DayQuantity.objects.get_or_create(date=current_date,index=index)
    dayq_filter = DayQuantity.objects.filter(date=current_date,index=index).first()

    if  operation == "warehouse_package": ## Dorzucamy stan ze skanera
        dayq_filter.warehouse_package = dayq_filter.warehouse_package + float(length_after) - float(length_before) if dayq_filter.warehouse_package!=None else float(length_after) - float(length_before)
    elif  operation == "warehouse_package_update": ##Dorzucamy roznice 
        dayq_filter.warehouse_package_update = dayq_filter.warehouse_package_update + float(length_after) - float(length_before) if dayq_filter.warehouse_package_update!=None else float(length_after) - float(length_before)
    elif  operation == "release_package": ##Przepychamy stan ze skanera 

        dayq_filter.release_package = dayq_filter.release_package + float(length_after)  if dayq_filter.release_package!=None else  float(length_after)
    elif  operation == "update_length":
        dayq_filter.update_length = dayq_filter.update_length + float(length_before) - float(length_after) if dayq_filter.update_length!=None else float(length_before) -float(length_after)
    elif  operation == "close_package":
        dayq_filter.close_package = dayq_filter.close_package + float(length_before) - float(length_after) if dayq_filter.close_package!=None else float(length_before) - float(length_after)
    else:
        print("Unknown operation")
    dayq_filter.save()



    return "OK"