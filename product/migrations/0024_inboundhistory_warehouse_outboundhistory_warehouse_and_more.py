# Generated by Django 4.1.1 on 2023-01-23 16:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0023_inboundhistory_reference_no_delete_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='inboundhistory',
            name='warehouse',
            field=models.ForeignKey(db_column='warehouse', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='warehouse_name_i', to='product.warehouse', to_field='warehouse'),
        ),
        migrations.AddField(
            model_name='outboundhistory',
            name='warehouse',
            field=models.ForeignKey(db_column='warehouse', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='warehouse_name_o', to='product.warehouse', to_field='warehouse'),
        ),
    ]
