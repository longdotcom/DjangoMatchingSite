# Generated by Django 2.1.3 on 2018-12-09 00:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('matchingapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='member',
            name='hobby',
            field=models.ManyToManyField(blank=True, to='matchingapp.Hobby'),
        ),
    ]