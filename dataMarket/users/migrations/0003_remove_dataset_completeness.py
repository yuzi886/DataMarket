# Generated by Django 4.1.7 on 2023-02-18 20:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_remove_sub_domain_domain_delete_task_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dataset',
            name='completeness',
        ),
    ]
