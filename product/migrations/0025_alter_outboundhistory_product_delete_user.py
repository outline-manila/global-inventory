# Generated by Django 4.1.1 on 2023-01-23 17:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0024_inboundhistory_warehouse_outboundhistory_warehouse_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='outboundhistory',
            name='product',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='product.product'),
        ),
    ]