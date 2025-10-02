from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("apiary", "0001_initial"),
    ]

    run_before = [
        ("apiary", "0002_alter_apiary_hive_count_alter_apiary_location_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="revision",
            name="management_performed",
            field=models.BooleanField(default=False, verbose_name="Houve manejo?"),
        ),
    ]
