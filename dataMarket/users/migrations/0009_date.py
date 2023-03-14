# Generated by Django 4.1.7 on 2023-03-13 16:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_rename_uniqueness_dataset_unique_num_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Date',
            fields=[
                ('dataset_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='users.dataset')),
                ('column_name', models.CharField(max_length=100)),
                ('datetime', models.JSONField(blank=True)),
            ],
        ),
    ]