# Generated by Django 4.1.1 on 2022-10-13 09:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0005_delete_user'),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='job_role',
            field=models.ForeignKey(db_column='job_role', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='product.jobrole', to_field='job_role'),
        ),
    ]