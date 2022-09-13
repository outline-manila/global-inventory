from django.db import models
from django.utils import timezone
import uuid
from datetime import datetime

#TODO VALIDATE REF NO
def invoice_number():
    today = datetime.date.today()
    today_string = today.strftime('%y%m%d')
    last_invoice = TransactionHistory.objects.filter(invoice_id__startswith=today_string).order_by('id').last()
    if not last_invoice:
        return today_string + "00001"
    
    invoice_no = last_invoice.invoice_no
    invoice_int = int(invoice_no.invoice_id[6:])
    new_invoice_int = invoice_int + 1
    new_invoice_no = today_string + str(new_invoice_int)
    
    return new_invoice_no

class PartNo(models.Model):

    part_no = models.CharField(max_length=125, null=False, blank=False, unique=True, default="null")
    updated_at = models.DateTimeField(blank=False, default=timezone.now, null=False)
    created_at = models.DateTimeField(blank=False, default=timezone.now, null=False, editable=False)
    is_active = models.BooleanField(default=True)

class Unit(models.Model):

    unit = models.CharField(max_length=125, null=False, blank=False, unique=True, default="null")
    updated_at = models.DateTimeField(blank=False, default=timezone.now, null=False)
    created_at = models.DateTimeField(blank=False, default=timezone.now, null=False, editable=False)
    is_active = models.BooleanField(default=True)

class Supplier(models.Model):

    supplier = models.CharField(max_length=125, null=False, blank=False, unique=True, default="null")
    updated_at = models.DateTimeField(blank=False, default=timezone.now, null=False)
    created_at = models.DateTimeField(blank=False, default=timezone.now, null=False, editable=False)
    is_active = models.BooleanField(default=True)

class Brand(models.Model):

    brand = models.CharField(max_length=125, null=False, blank=False, unique=True, default="null")
    updated_at = models.DateTimeField(blank=False, default=timezone.now, null=False)
    created_at = models.DateTimeField(blank=False, default=timezone.now, null=False, editable=False)
    is_active = models.BooleanField(default=True)


class JobRole(models.Model):

    job_role = models.CharField(max_length=125, null=False, blank=False, unique=True, default="null")
    updated_at = models.DateTimeField(blank=False, default=timezone.now, null=False)
    created_at = models.DateTimeField(blank=False, default=timezone.now, null=False, editable=False)
    is_active =  models.BooleanField(default=True)


class Warehouse(models.Model):

    warehouse_no = models.CharField(max_length=125, null=False, blank=False, unique=True, default="null")
    updated_at = models.DateTimeField(blank=False, default=timezone.now, null=False)
    created_at = models.DateTimeField(blank=False, default=timezone.now, null=False, editable=False)
    is_active = models.BooleanField(default=True)


class Product(models.Model):
    uuid = models.UUIDField(default = uuid.uuid4, editable = False)
    warehouse_no = models.ForeignKey(Warehouse ,to_field="warehouse_no", db_column="warehouse_no", on_delete=models.DO_NOTHING)
    part_no = models.ForeignKey(PartNo ,related_name="part" , to_field="part_no", db_column="part_no", on_delete=models.DO_NOTHING)
    other_part_no = models.ForeignKey(PartNo ,related_name="other_part", to_field="part_no", db_column="other_part_no", on_delete=models.DO_NOTHING)
    description = models.TextField(blank=True, null=False)
    brand = models.ForeignKey(Brand ,to_field="brand", db_column="brand", on_delete=models.DO_NOTHING)
    remaining_stock = models.IntegerField(blank=False, default=0, null=False)
    unit = models.ForeignKey(Unit ,to_field="unit", db_column="unit", on_delete=models.DO_NOTHING)
    supplier = models.ForeignKey(Supplier ,to_field="supplier", db_column="supplier", on_delete=models.DO_NOTHING)
    updated_at = models.DateTimeField(blank=False, default=timezone.now, null=False)
    created_at = models.DateTimeField(blank=False, default=timezone.now, null=False, editable=False)


class TransactionHistory(models.Model):

    uuid = models.UUIDField(default = uuid.uuid4, editable = False)
    date = models.DateTimeField(blank=False, default=timezone.now, null=False)
    invoice_no = models.CharField(default=invoice_number, max_length=120, null=False)
    action = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    user_id = models.ForeignKey("core.User", on_delete=models.DO_NOTHING)
    warehouse_no = models.ForeignKey(Warehouse ,to_field="warehouse_no", db_column="warehouse_no", on_delete=models.DO_NOTHING)
    product_id = models.ForeignKey("Product", on_delete=models.DO_NOTHING)
