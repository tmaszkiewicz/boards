from django.db.models import Sum
#from  datetime import date
import datetime
from .models import Index, Package,DayQuantity
def update_quantinies():
    current_date = datetime.date.today() 
    indexy = Index.objects.all()
    for index in indexy:
        sum_MAG = Package.objects.filter(index=index,localisation="MAG").aggregate(Sum('length'))
        sum_PRD = Package.objects.filter(index=index,localisation="PRD").aggregate(Sum('length'))
        sum_ALL = Package.objects.filter(index=index).exclude(localisation="CLOSED").aggregate(Sum('length'))
        print(sum_MAG)
        dayq = DayQuantity.objects.get_or_create(date=current_date,index=index)
        dayq_filter = DayQuantity.objects.filter(date=current_date,index=index).first()

        dayq_filter.mag_qty = sum_MAG['length__sum'] if sum_MAG['length__sum']!=None else 0
        dayq_filter.prd_qty = sum_PRD['length__sum'] if sum_PRD['length__sum']!=None else 0
        dayq_filter.all_qty = sum_ALL['length__sum'] if sum_ALL['length__sum']!=None else 0

        dayq_filter.save()



        

