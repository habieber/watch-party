# Generated by Django 5.0.4 on 2024-04-11 20:00

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0005_alter_moviereview_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='showreview',
            name='date',
            field=models.DateField(default=datetime.date(2024, 4, 11)),
        ),
    ]
