# Generated by Django 5.1.1 on 2024-09-08 14:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transaction',
            name='products',
        ),
        migrations.AddField(
            model_name='transaction',
            name='products',
            field=models.TextField(default=str),
            preserve_default=False,
        ),
    ]
