# Generated by Django 5.1.1 on 2024-09-19 01:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App_Combustivel', '0008_usuario_email'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='usuario',
            name='senha',
        ),
        migrations.AddField(
            model_name='usuario',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='usuario',
            name='is_staff',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='usuario',
            name='last_login',
            field=models.DateTimeField(blank=True, null=True, verbose_name='last login'),
        ),
        migrations.AddField(
            model_name='usuario',
            name='password',
            field=models.CharField(default='1234', max_length=128, verbose_name='password'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='usuario',
            name='usuario',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]
