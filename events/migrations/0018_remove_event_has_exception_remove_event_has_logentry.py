# Generated by Django 4.2.19 on 2025-02-09 20:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0017_alter_event_calculated_type_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="event",
            name="has_exception",
        ),
        migrations.RemoveField(
            model_name="event",
            name="has_logentry",
        ),
    ]
