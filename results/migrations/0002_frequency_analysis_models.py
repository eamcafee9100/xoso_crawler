# Generated manually for frequency analysis models

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('results', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='NumberAnalysisCache',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(db_index=True, help_text='Số 2 chữ số (00-99)', max_length=2)),
                ('analysis_date', models.DateField(db_index=True, help_text='Ngày thực hiện phân tích')),
                ('appearances_30d', models.IntegerField(default=0, help_text='Số lần xuất hiện trong 30 ngày')),
                ('appearances_total', models.IntegerField(default=0, help_text='Tổng số lần xuất hiện trong 1 năm')),
                ('avg_cycle_days', models.FloatField(default=0, help_text='Chu kỳ xuất hiện trung bình (ngày)')),
                ('median_cycle_days', models.FloatField(default=0, help_text='Chu kỳ xuất hiện median (ngày)')),
                ('current_gan_days', models.IntegerField(default=0, help_text='Số ngày gan hiện tại')),
                ('max_gan_days', models.IntegerField(default=0, help_text='Gan tối đa trong lịch sử')),
                ('max_gan_start_date', models.DateField(blank=True, help_text='Ngày bắt đầu gan tối đa', null=True)),
                ('max_gan_end_date', models.DateField(blank=True, help_text='Ngày kết thúc gan tối đa', null=True)),
                ('probability_next_appearance', models.FloatField(default=0, help_text='Xác suất xuất hiện trong chu kỳ tiếp theo (%)')),
                ('probability_when_max_gan', models.FloatField(default=0, help_text='Xác suất xuất hiện khi gan cực đại (%)')),
                ('weekday_analysis', models.JSONField(default=dict, help_text='Phân tích theo thứ trong tuần')),
                ('companion_numbers', models.JSONField(default=list, help_text='Top 10 số thường xuất hiện cùng')),
                ('max_consecutive_days', models.IntegerField(default=0, help_text='Số ngày liên tiếp tối đa')),
                ('consecutive_history', models.JSONField(default=list, help_text='Lịch sử xuất hiện liên tiếp')),
                ('consecutive_probabilities', models.JSONField(default=dict, help_text='Xác suất xuất hiện liên tiếp theo số ngày')),
                ('predecessor_analysis', models.JSONField(default=list, help_text='Top 10 số thường xuất hiện trước 1 ngày')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'indexes': [
                    models.Index(fields=['number', 'analysis_date'], name='results_num_number_5f4458_idx'),
                    models.Index(fields=['updated_at'], name='results_num_updated_5c6f3a_idx'),
                ],
                'unique_together': {('number', 'analysis_date')},
            },
        ),
        migrations.CreateModel(
            name='NumberAnalysisDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('detail_type', models.CharField(choices=[('gan_history', 'Lịch sử gan'), ('cycle_pattern', 'Mẫu chu kỳ'), ('companion_detail', 'Chi tiết số đính kèm'), ('consecutive_events', 'Sự kiện liên tiếp')], max_length=20)),
                ('data', models.JSONField(help_text='Dữ liệu chi tiết')),
                ('cache', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='details', to='results.numberanalysiscache')),
            ],
            options={
                'indexes': [
                    models.Index(fields=['cache', 'detail_type'], name='results_num_cache_i_8e72a3_idx'),
                ],
                'unique_together': {('cache', 'detail_type')},
            },
        ),
    ]
