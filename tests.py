from django.test import TestCase,Client
from boards.models import Index

# Create your tests here.
class home(TestCase):
    def test_home(self):
        c = Client()
        resp = c.post('/boards/',{})
        self.assertEqual(resp.status_code,200)
class admission(TestCase):
    def test_admission(self):
        c = Client()
        resp = c.post('/admission/',{})
        self.assertEqual(resp.status_code,200)
class suppliers(TestCase):
    def test_suppliers(self):
        c = Client()
        resp = c.post('/suppliers/',{})
        self.assertEqual(resp.status_code,200)      
class packages(TestCase):
    def test_packages(self):
        c = Client()
        resp = c.post('/packages/',{})
        self.assertEqual(resp.status_code,200)      
class packages_edit(TestCase):
    def test_packages_edit(self):
        c = Client()
        resp = c.post('/packages_edit/xx',{})
        self.assertEqual(resp.status_code,200)      

class suppliers_del(TestCase):
    def test_suppliers_del(self):
        ##Trzeba utworzyc suppliera, po czym usunac go po PK -TODO
        c = Client()
        resp = c.post('/suppliers/1/',{})
        self.assertEqual(resp.status_code,200)     
class suppliers_add(TestCase):
    def test_suppliers_add(self):
        ##Trzeba utworzyc suppliera, po czym usunac go po PK -TODO
        c = Client()
        resp = c.post('/suppliers_add/',{})
        self.assertEqual(resp.status_code,200)     
class indexes(TestCase):
    def test_indexes(self):
        c = Client()
        resp = c.post('/indexes/',{})
        self.assertEqual(resp.status_code,200) 
class indexes_del(TestCase):
    def test_indexes(self):
        ##Trzeba utworzyc index, po czym usunac go po PK -TODO
        c = Client()
        resp = c.post('/indexes/1/',{})
        self.assertEqual(resp.status_code,200)   
class indexes_add(TestCase):
    def test_indexes_add(self):
        ##Trzeba utworzyc index, po czym usunac go po PK -TODO
        c = Client()
        resp = c.post('/indexes_add/',{})
        self.assertEqual(resp.status_code,200)     

class index_report(TestCase):
    def test_index_report(self):
        ##Trzeba utworzyc index, po czym usunac go po PK -TODO
        c = Client()
        resp = c.post('/index_report/',{})
        self.assertEqual(resp.status_code,200)       

class scanner_load(TestCase) :
    def test_scanner_load(self):
        c = Client()
        #try all casese for request typ=...
        resp = c.post('/scanner/load/',{})
        self.assertEqual(resp.status_code,200)     

class IndexTest(TestCase):
    # Dlaczego nie dziala inicjacja z polem sap?
    def createIndex(self, sap="1",name="test"):
        return Index.objects.create(name=name)
    def testIndexCreate(self):
        i =self.createIndex(self)
        self.assertTrue(isinstance(i, Index))
        self.assertEqual(i.__unicode__(),i.name)
class SupplierTest(TestCase):
    def createSupplier(self, name="Suppl"):
        return Supplier.objects.create(name=name)
    def testSupplierCreate(self):
        i =self.createSupplier(self)
        self.assertTrue(isinstance(i, Supplier))
        self.assertEqual(i.__repr__(),i.Supplier)
class PackageTest(TestCase):
    def createPackage(self, name="Suppl"):
        index = Index.objects.create(name=name)
        return Package.objects.create(index=index)
        ##Przetestowanie czy dziala create_label, czy np tworzy sie plik... w tmp
    def testSupplierCreate(self):
        i =self.createSupplier(self)
        self.assertTrue(isinstance(i, Supplier))
        self.assertEqual(i.__repr__(),i.Supplier)
class CurrentUserTest(TestCase):
        i = self.createCurrentUser(self)
        self.assertTrue(isinstance(i, CurrentUser))
        self.assertEqual(i.__repr__(),i.CurrentUser)



