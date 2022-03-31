from .models import Log

#def package_label(package):
def delivery_print():
    print("test")
    pass
def create_log(operation, userid, length_before,length_after,localisation_before,localisation_after,delivery_date_before,delivery_date_after):
    #try:
    log = Log()
    log.operation = operation
    #log.scanner = scanner
    log.userid = userid
    log.length_before = length_before
    log.length_after = length_after
    log.localisation_before = localisation_before
    log.localisation_after = localisation_after
    log.delivery_date_before = delivery_date_before
    log.delivery_date_after= delivery_date_after
    log.save()
    #    return "OK"
    #except:
    return "NOK"
