# Generated by Django 4.2.11 on 2024-03-27 10:27

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='id',
        ),
        migrations.AddField(
            model_name='user',
            name='displayName',
            field=models.CharField(max_length=25, null=True, validators=[django.core.validators.MinLengthValidator(5, 'Must contains at least 5 char')]),
        ),
        migrations.AddField(
            model_name='user',
            name='gunFightElo',
            field=models.PositiveIntegerField(default=200),
        ),
        migrations.AddField(
            model_name='user',
            name='picture',
            field=models.CharField(max_length=25, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='pongElo',
            field=models.PositiveIntegerField(default=200),
        ),
        migrations.AlterField(
            model_name='user',
            name='login',
            field=models.CharField(max_length=15, primary_key=True, serialize=False),
        ),
    ]