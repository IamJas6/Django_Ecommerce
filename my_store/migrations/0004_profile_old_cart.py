# Generated by Django 5.0.4 on 2024-07-07 12:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('my_store', '0003_profile'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='old_cart',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
