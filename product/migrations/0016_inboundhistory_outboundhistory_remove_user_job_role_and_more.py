# Generated by Django 4.1.2 on 2023-01-02 15:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import product.models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('product', '0015_alter_employee_middle_name_delete_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='InboundHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('invoice_no', models.CharField(default=product.models.invoice_number, max_length=120)),
                ('action', models.TextField(blank=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
            ],
        ),
        migrations.CreateModel(
            name='OutboundHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('invoice_no', models.CharField(default=product.models.invoice_number, max_length=120)),
                ('action', models.TextField(blank=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
            ],
        ),
        migrations.AddField(
            model_name='partno',
            name='brand',
            field=models.ForeignKey(db_column='brand', default='CROWN', on_delete=django.db.models.deletion.CASCADE, to='product.brand', to_field='brand'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='employee',
            name='job_role',
            field=models.ForeignKey(db_column='job_role', null=True, on_delete=django.db.models.deletion.CASCADE, to='product.jobrole', to_field='job_role'),
        ),
        migrations.AlterField(
            model_name='employee',
            name='warehouse',
            field=models.ForeignKey(db_column='warehouse', null=True, on_delete=django.db.models.deletion.CASCADE, to='product.warehouse', to_field='warehouse'),
        ),
        migrations.AlterField(
            model_name='product',
            name='brand',
            field=models.ForeignKey(db_column='brand', on_delete=django.db.models.deletion.CASCADE, to='product.brand', to_field='brand'),
        ),
        migrations.AlterField(
            model_name='product',
            name='other_part',
            field=models.ForeignKey(db_column='other_part', on_delete=django.db.models.deletion.CASCADE, related_name='other_part_number', to='product.partno', to_field='part'),
        ),
        migrations.AlterField(
            model_name='product',
            name='part',
            field=models.ForeignKey(db_column='part', default='NaN', on_delete=django.db.models.deletion.CASCADE, related_name='part_number', to='product.partno', to_field='part'),
        ),
        migrations.AlterField(
            model_name='product',
            name='supplier',
            field=models.ForeignKey(db_column='supplier', on_delete=django.db.models.deletion.CASCADE, to='product.supplier', to_field='supplier'),
        ),
        migrations.AlterField(
            model_name='product',
            name='unit',
            field=models.ForeignKey(db_column='unit', on_delete=django.db.models.deletion.CASCADE, to='product.unit', to_field='unit'),
        ),
        migrations.AlterField(
            model_name='product',
            name='warehouse',
            field=models.ForeignKey(db_column='warehouse', on_delete=django.db.models.deletion.CASCADE, related_name='warehouse_name', to='product.warehouse', to_field='warehouse'),
        ),
        migrations.DeleteModel(
            name='TransactionHistory',
        ),
        migrations.AddField(
            model_name='outboundhistory',
            name='product_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.product'),
        ),
        migrations.AddField(
            model_name='outboundhistory',
            name='user_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='outboundhistory',
            name='warehouse',
            field=models.ForeignKey(db_column='warehouse', default='NaN', on_delete=django.db.models.deletion.CASCADE, related_name='warehouse_name_o', to='product.warehouse', to_field='warehouse'),
        ),
        migrations.AddField(
            model_name='inboundhistory',
            name='product_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.product'),
        ),
        migrations.AddField(
            model_name='inboundhistory',
            name='user_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='inboundhistory',
            name='warehouse',
            field=models.ForeignKey(db_column='warehouse', default='NaN', on_delete=django.db.models.deletion.CASCADE, related_name='warehouse_name_i', to='product.warehouse', to_field='warehouse'),
        ),
    ]
