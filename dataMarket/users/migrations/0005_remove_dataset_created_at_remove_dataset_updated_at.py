# Generated by Django 4.1.7 on 2023-02-18 21:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_dataset_created_at_dataset_updated_at'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dataset',
            name='created_at',
        ),
        migrations.RemoveField(
            model_name='dataset',
            name='updated_at',
        ),
    ]
