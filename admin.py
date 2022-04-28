from atexit import register
from django.contrib import admin
from .models import Index,Supplier,Package,Log,CurrentUser,DayQuantity, DeletedPackage

class PackageAdmin(admin.ModelAdmin):
    search_fields = ['pk']
    readonly_fields = ['delivery_time']

# Register your models here.
admin.site.register(Index)
admin.site.register(Supplier)
admin.site.register(Package,PackageAdmin)
#admin.site.register(PackageTrash)
admin.site.register(DeletedPackage)
admin.site.register(Log)
admin.site.register(CurrentUser)
admin.site.register(DayQuantity)



