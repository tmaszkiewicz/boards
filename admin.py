from atexit import register
from django.contrib import admin
from .models import Index,Supplier,Package,Log,PackageTrash,CurrentUser,DayQuantity

# Register your models here.
admin.site.register(Index)
admin.site.register(Supplier)
admin.site.register(Package)
admin.site.register(PackageTrash)
admin.site.register(Log)
admin.site.register(CurrentUser)
admin.site.register(DayQuantity)



