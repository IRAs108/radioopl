# Generated by Django 3.0 on 2019-12-12 11:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scrobbell', '0007_auto_20191212_1128'),
    ]

    operations = [
        migrations.AddField(
            model_name='song',
            name='stations',
            field=models.ManyToManyField(to='scrobbell.Station'),
        ),
    ]