# Generated by Django 4.1.1 on 2023-01-23 15:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0022_outboundhistory_reference_no_delete_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='inboundhistory',
            name='reference_no',
            field=models.TextField(blank=True, null=True),
        ),
    ]