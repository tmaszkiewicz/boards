import datetime
from .models import Log,Index,Supplier,Package,DayQuantity

#def package_label(package):
def delivery_print():
    print("test")
    pass
def create_log(operation, userid, length_before,length_after,localisation_before,localisation_after,delivery_date_before,delivery_date_after,username,scanner,index_pk,package_pk,supplier_pk,paczka_before,paczka_after):
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