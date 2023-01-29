# Generated by Django 4.1.1 on 2023-01-29 16:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0028_outboundhistory_remarks_outboundhistory_warehouse_to_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='inboundhistory',
            name='supplier',
            field=models.ForeignKey(db_column='supplier', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='supplier_i', to='product.supplier', to_field='supplier'),
        ),
    ]