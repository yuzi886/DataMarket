# Generated by Django 4.1.7 on 2023-03-13 16:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='date',
            name='dataset_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='users.dataset', unique=True),
        ),
    ]