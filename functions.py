from .models import Log,Index,Supplier,Package

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
