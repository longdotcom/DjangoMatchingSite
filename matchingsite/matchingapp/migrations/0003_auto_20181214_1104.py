# Generated by Django 2.1.3 on 2018-12-14 11:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('matchingapp', '0002_auto_20181209_0037'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='image',
            field=models.ImageField(blank=True, upload_to='media/'),
        ),
    ]