from django.db import models
from django.utils import timezone
import uuid
from datetime import date

#TODO VALIDATE REF NO
def invoice_number():
    today = date.today()
    today_string = today.strftime('%m%d%y')
    last_invoice_outbound = OutboundHistory.objects.filter(invoice_no__startswith=today_string).order_by('-id').first()
    last_invoice_inbound = InboundHistory.objects.filter(invoice_no__startswith=today_string).order_by('-id').first()
    # last_invoice = last_invoice_outbound or last_invoice_inbound

    if (last_invoice_outbound != None and last_invoice_inbound != None) and False:
        last_invoice = max(int(last_invoice_inbound), int(last_invoice_outbound))
    
    else:
        last_invoice = last_invoice_outbound or last_invoice_inbound

    if not last_invoice:
        return today_string + "00001"
    
    invoice_no = last_invoice.invoice_no
    invoice_int = int(invoice_no[6:])
    new_invoice_int = str(invoice_int + 1).zfill(5)
    new_invoice_no = today_string + str(new_invoice_int)
    return new_invoice_no

    
class Brand(models.Model):

    brand = models.CharField(max_length=125, null=False, blank=False, unique=True, default="null")
    description = models.CharField(max_length=500, null=True, blank=True, unique=False, default="")
    updated_at = models.DateTimeField(blank=False, default=timezone.now, null=False)
    created_at = models.DateTimeField(blank=False, default=timezone.now, null=False, editable=False)
    is_active = models.BooleanField(default=True)
    end_date = models.DateTimeField(blank=True, null=True, default=None)
    start_date = models.DateTimeField(blank=True, null=True, default=None)


class PartNo(models.Model):

    part = models.CharField(max_length=125, null=False, blank=False, unique=True, default="null")
    description = models.CharField(max_length=500, null=True, blank=True, unique=False, default="")
    other_part_no = models.CharField(max_length=500, null=True, blank=True, unique=False, default="")
    updated_at = models.DateTimeField(blank=False, default=timezone.now, null=False)
    created_at = models.DateTimeField(blank=False, default=timezone.now, null=False, editable=False)
    is_active = models.BooleanField(default=True)
    end_date = models.DateTimeField(blank=True, null=True, default=None)
    start_date = models.DateTimeField(blank=True, null=True, default=None)
    brand = models.ForeignKey(Brand ,to_field="brand", db_column="brand", on_delete=models.CASCADE)

class Unit(models.Model):

    unit = models.CharField(max_length=125, null=False, blank=False, unique=True, default="null")
    description = models.CharField(max_length=500, null=True, blank=True, unique=False, default="")
    updated_at = models.DateTimeField(blank=False, default=timezone.now, null=False)
    created_at = models.DateTimeField(blank=False, default=timezone.now, null=False, editable=False)
    is_active = models.BooleanField(default=True)
    end_date = models.DateTimeField(blank=True, null=True, default=None)
    start_date = models.DateTimeField(blank=True, null=True, default=None)

class Supplier(models.Model):

    supplier = models.CharField(max_length=125, null=False, blank=False, unique=True, default="null")
    description = models.CharField(max_length=500, null=True, blank=True, unique=False, default="")
    updated_at = models.DateTimeField(blank=False, default=timezone.now, null=False)
    created_at = models.DateTimeField(blank=False, default=timezone.now, null=False, editable=False)
    is_active = models.BooleanField(default=True)
    end_date = models.DateTimeField(blank=True, null=True, default=None)
    start_date = models.DateTimeField(blank=True, null=True, default=None)



class JobRole(models.Model):

    job_role = models.CharField(max_length=125, null=False, blank=False, unique=True, default="null")
    description = models.CharField(max_length=500, null=True, blank=True, unique=False, default="")
    updated_at = models.DateTimeField(blank=False, default=timezone.now, null=False)
    created_at = models.DateTimeField(blank=False, default=timezone.now, null=False, editable=False)
    is_active =  models.BooleanField(default=True)
    end_date = models.DateTimeField(blank=True, null=True, default=None)
    start_date = models.DateTimeField(blank=True, null=True, default=None)


class Warehouse(models.Model):

    warehouse = models.CharField(max_length=125, null=False, blank=False, unique=True, default="null")
    description = models.CharField(max_length=500, null=True, blank=True, unique=False, default="")
    updated_at = models.DateTimeField(blank=False, default=timezone.now, null=False)
    created_at = models.DateTimeField(blank=False, default=timezone.now, null=False, editable=False)
    start_date = models.DateTimeField(blank=True, null=True, default=None)
    end_date = models.DateTimeField(blank=True, null=True, default=None)
    is_active = models.BooleanField(default=True)


class Employee(models.Model):
    uuid = models.UUIDField(default = uuid.uuid4, editable = False)
    email = models.EmailField(db_index=True, unique=True, max_length=254)
    first_name = models.CharField(max_length=240)
    middle_name =  models.CharField(max_length=120, blank=True, null=True)
    last_name =  models.CharField(max_length=120)
    employee_id = models.CharField(max_length=120)
    remarks  =  models.CharField(max_length=500, null=True, blank=True)
    warehouse = models.ForeignKey(Warehouse, to_field="warehouse", db_column="warehouse", on_delete=models.CASCADE, null=True)
    job_role = models.ForeignKey(JobRole, to_field="job_role", db_column="job_role", on_delete=models.CASCADE, null=True)
    start_date = models.DateTimeField(blank=False, null=False, default=timezone.now, editable=False)
    end_date = models.DateTimeField(blank=False, null=True)
    updated_at = models.DateTimeField(blank=False, default=timezone.now, null=False)
    created_at = models.DateTimeField(blank=False, default=timezone.now, null=False, editable=False)

class Product(models.Model):
    uuid = models.UUIDField(default = uuid.uuid4, editable = False)
    warehouse = models.ForeignKey(Warehouse, related_name="warehouse_name", to_field="warehouse", db_column="warehouse", on_delete=models.CASCADE, null=True)
    part = models.ForeignKey(PartNo ,related_name="part_number" , to_field="part", db_column="part", on_delete=models.CASCADE, default='NaN')
    other_part = models.ForeignKey(PartNo ,related_name="other_part_number", to_field="part", db_column="other_part", on_delete=models.CASCADE, null=True)
    description = models.TextField(blank=True, null=False)
    brand = models.ForeignKey(Brand ,to_field="brand", db_column="brand", on_delete=models.CASCADE)
    remaining_stock = models.IntegerField(blank=False, default=0, null=False)
    unit = models.ForeignKey(Unit ,to_field="unit", db_column="unit", on_delete=models.CASCADE, null=True)
    supplier = models.ForeignKey(Supplier ,to_field="supplier", db_column="supplier", on_delete=models.CASCADE, null=True)
    updated_at = models.DateTimeField(blank=False, default=timezone.now, null=False)
    created_at = models.DateTimeField(blank=False, default=timezone.now, null=False, editable=False)


class InboundHistory(models.Model):

    uuid = models.UUIDField(default = uuid.uuid4, editable = False)
    date = models.DateTimeField(blank=False, default=timezone.now, null=False)
    invoice_no = models.CharField(default=invoice_number, max_length=120, null=False)
    reference_no = models.TextField(blank=True, null=True)
    action = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    user = models.ForeignKey("core.User", on_delete=models.CASCADE, null=True)
    product = models.ForeignKey("Product", on_delete=models.CASCADE, null=True, default=None)
    updated_at = models.DateTimeField(blank=False, default=timezone.now, null=False)
    created_at = models.DateTimeField(blank=False, default=timezone.now, null=False, editable=False)
    warehouse = models.ForeignKey(Warehouse, related_name="warehouse_name_i" ,to_field="warehouse", db_column="warehouse", on_delete=models.CASCADE, null=True)
    supplier = models.ForeignKey(Supplier, related_name="supplier_i", to_field="supplier", db_column="supplier", on_delete=models.CASCADE, null=True)

class OutboundHistory(models.Model):
    

    uuid = models.UUIDField(default = uuid.uuid4, editable = False)
    date = models.DateTimeField(blank=False, default=timezone.now, null=False)
    invoice_no = models.CharField(default=invoice_number, max_length=120, null=False)
    action = models.TextField(blank=True, null=True)
    reference_no = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    user = models.ForeignKey("core.User", on_delete=models.CASCADE, null=True)
    product = models.ForeignKey("Product", on_delete=models.CASCADE, null=True, default=None)
    remarks = models.TextField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=False, default=timezone.now, null=False)
    created_at = models.DateTimeField(blank=False, default=timezone.now, null=False, editable=False)
    warehouse_to = models.ForeignKey(Warehouse, related_name="warehouse_name_to" ,to_field="warehouse", db_column="warehouse_to", on_delete=models.CASCADE, null=True)
    warehouse = models.ForeignKey(Warehouse, related_name="warehouse_name_o" ,to_field="warehouse", db_column="warehouse", on_delete=models.CASCADE, null=True)

