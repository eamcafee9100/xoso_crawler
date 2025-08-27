from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("results", "0002_frequency_analysis_models"),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name="numberfrequencystats",
            name="results_num_date_160709_idx",
        ),
        migrations.AlterField(
            model_name="numberfrequencystats",
            name="date",
            field=models.DateField(db_index=True, help_text="Ngày xuất hiện"),
        ),
    ]
