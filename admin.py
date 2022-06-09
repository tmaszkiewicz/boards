from atexit import register
from django.contrib import admin
from .models import Index,Supplier,Package,Log,CurrentUser,DayQuantity, DeletedPackage,LogInventory,inventory,deletions,InvetoriedRestore


class LogInventoryAdmin(admin.ModelAdmin):
    search_fields = ['pk','inventory_name']
    readonly_fields = ['timestamp']

class PackageAdmin(admin.ModelAdmin):
    search_fields = ['pk']
    readonly_fields = ['delivery_time']

class DeletedPackageAdmin(admin.ModelAdmin):
    search_fields = ['pk']
    readonly_fields = ['delivery_time']
class DeletionsAdmin(admin.ModelAdmin):
    search_fields = ['package','package_deleted_as_first','deletion_date']

    readonly_fields = ['deletion_date']
# Register your models here.
admin.site.register(Index)
admin.site.register(Supplier)
admin.site.register(Package,PackageAdmin)
#admin.site.register(PackageTrash)
admin.site.register(DeletedPackage,DeletedPackageAdmin)
admin.site.register(Log)
admin.site.register(LogInventory,LogInventoryAdmin)
admin.site.register(CurrentUser)
admin.site.register(DayQuantity)
admin.site.register(inventory)
admin.site.register(deletions,DeletionsAdmin)
admin.site.register(InvetoriedRestore)


