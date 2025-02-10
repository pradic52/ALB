# Generated by Django 5.1.4 on 2025-02-07 04:05

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='GlobalSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=255, unique=True)),
                ('value_text', models.TextField(blank=True, null=True)),
                ('value_image', models.ImageField(blank=True, null=True, upload_to='settings/')),
                ('type', models.CharField(choices=[('text', 'Texte'), ('image', 'Image')], default='text', max_length=10)),
            ],
        ),
    ]
