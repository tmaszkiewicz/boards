from math import fabs
import pkgutil
from statistics import mode
from tkinter import Widget
from django.db import models
from django import forms
from datetime import date

# Create your models here.


class Supplier(models.Model):    
    name = models.CharField(max_length=150,blank=False,null=False)
    def __repr__(self):
        return self.name
    def __str__(self):
        return self.name

class Index(models.Model):
    sap = models.CharField(max_length=20,blank=False,null=False)
    name = models.CharField(max_length=100,blank=False,null=False)
    country = models.CharField(max_length=5, blank=True,null=True,default="PL") 
    werk = models.CharField(max_length=10,blank=False,null=False,default="3000")
    default_length = models.FloatField(blank=True,null=True)
    def __unicode__(self):
        return self.name
    def __str__(self):
        return "{} {}".format(self.sap,self.name)

class Package(models.Model):
    # = models.CharField(max_length=12,blank=False,null=False,default="0")
    index = models.ForeignKey(Index,on_delete=models.CASCADE,null=False)
    delivery_date = models.DateField(default=date.today)
    delivery_time = models.DateTimeField(auto_now=True)
    supplier = models.ForeignKey(Supplier,on_delete=models.SET_NULL,null=True,blank=True) # .CharField(max_length=100,blank=True,null=True)
    werk = models.CharField(max_length=10,blank=False,null=False,default="3000")
    localisation = models.CharField(max_length=15,blank=False,null=False)
    length = models.FloatField(default="0",blank=True,null=True)
    wz = models.CharField(max_length=15,blank=True,null=True)

    #description = models.CharField(max_length=100,blank=True,null=True)
    @property
    def pk_formatted(self):
        return "0" * (12-len(str(self.pk)))+ str(self.pk)
        self.pk_formatted = "0" #* (12-len(str(self.pk))) #+ str(self.pk)
    
    def create_label(self,print):
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.pdfgen import canvas
        from reportlab.lib.units import cm
        from reportlab.graphics.barcode import code128
        from subprocess import call
        pdfmetrics.registerFont(TTFont('AlegreyaSC', 'boards/static/ttf/AlegreyaSC-Bold.ttf'))
        _barcode = code128.Code128(self.pk_formatted,barHeight=35,barWidth = 1.8)
        #c = canvas.Canvas("tmp/etykieta.pdf", pagesize=(7.8 * cm, 5.4 * cm))
        c = canvas.Canvas("tmp/etykieta.pdf", pagesize=(8.8 * cm, 9.8 * cm))
        _barcode.drawOn(c, 20, 130)

        c.setFont('AlegreyaSC', size=20)
        c.drawString(10,200,f"SAP Index: {self.index.sap}")
        c.setFont('AlegreyaSC', size=10)
        c.drawString(10,180,self.index.name)
        c.setFont('AlegreyaSC', size=13)
        c.drawString(80,120,self.pk_formatted)
        c.drawString(10,80,f"Data przyjęcia: {self.delivery_date}")
        c.drawString(10,60,f"Dostawca: {self.supplier}")
        c.drawString(10,40,f"Długość: _____________")
        

        c.showPage()
        c.save()
        if print==True:
            call(['/etc/init.d/cups start'], shell=True)

            call(['lp -o Resolution=203dpi -o portrait -o PageSize=w880h980mm tmp/etykieta.pdf'], shell=True) 
            #call(['lp -o Resolution=203dpi -o portrait -o PageSize=w144h216 tmp/etykieta.pdf'], shell=True) 
            


    def __str__(self):
        return "{}".format(self.index.name)
class PackageTrash(Package):
   def __str__(self):
        return "{}".format(self.index.name)
class CurrentUser(models.Model):
    userid = models.CharField(max_length=8,null=False)
    host = models.CharField(max_length=15,null=False)
    name = models.CharField(max_length=50,null=False)
    login_time = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.userid}  {self.name} {self.host} {self.login_time}"


class Log(models.Model):
    op = (
        (0,'MAG'),
        (1,'PRD'),
        (2,'CLOSED'),
        (3,'EDIT'),
    )
    package = models.ForeignKey(Package,on_delete=models.SET_NULL,null=True)
    index_before = models.ForeignKey(Index,on_delete=models.SET_NULL,null=True,related_name="index_before")
    index_after = models.ForeignKey(Index,on_delete=models.SET_NULL,null=True,related_name="index_after")
    supplier_before = models.ForeignKey(Supplier,on_delete=models.SET_NULL,null=True,related_name="supplier_before")
    supplier_after = models.ForeignKey(Supplier,on_delete=models.SET_NULL,null=True,related_name="supplier_after")

    operation = models.IntegerField(default=0, choices=op)
    time = models.DateTimeField(auto_now_add=True)
    #user = models.CharField
    scanner = models.CharField(max_length=15,null=True,blank=True)
    userid = models.CharField(max_length=15,null=True,blank=True)
    username = models.CharField(max_length=15,null=True,blank=True)
    length_before = models.FloatField(blank=True,null=True)
    length_after = models.FloatField(blank=True,null=True)
    localisation_before =  models.CharField(max_length=15,blank=True,null=True)
    localisation_after =  models.CharField(max_length=15,blank=True,null=True)
    delivery_date_before = models.DateField()
    delivery_date_after = models.DateField()
    def __str__(self):
        return f"{self.scanner} {self.operation} {self.time}"



class IndexForm(forms.ModelForm):
    class Meta:
        model = Index
        fields = '__all__' 
        widgets = {
            'delivery_date': forms.DateInput(format=('%m/%d/%Y'), attrs={'class':'form-control', 'placeholder':'Select a date', 'type':'date'}),
            }
class PackageForm(forms.ModelForm):
    class Meta:
        from django.utils.translation import gettext_lazy as _
        model = Package
        fields = '__all__'
        labels = {
            'index': _('INDEX'),
            'delivery_date': _('DATA PRZYJĘCIA'),
            'supplier': _('DOSTAWCA'),
            'localisation': _('LOKALIZACJA'),
            'wz': _('WZ'),
        }
        help_texts = {
            'name': _('Some useful help text.'),
        } 
        widgets = {
            'delivery_date': forms.DateInput(format=('%m/%d/%Y'), attrs={'class':'form-control', 'placeholder':'Select a date', 'type':'date'}),
            }
class IndexForm(forms.ModelForm):
    class Meta:
        from django.utils.translation import gettext_lazy as _
        model = Index
        fields = ('sap','name',)
        labels = {
            'sap': _('SAP'),
            'name': _('NAZWA'),
        }
        help_texts = {
            'sap': _('SAP INDEX'),
        } 
class SupplierForm(forms.ModelForm):
    class Meta:
        from django.utils.translation import gettext_lazy as _
        model = Supplier
        fields = ('name',)
        labels = {
            'name': _('NAZWA'),
        }
        help_texts = {
            'sap': _('NAME'),
        }     