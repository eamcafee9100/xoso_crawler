import importlib
import inspect
import logging
import os
from datetime import date, timedelta
from typing import Any, Dict, List

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from predictions_tracker.models import (
    DailyTrackingSession,
    MethodPredictionResult,
    PredictionCycle,
    PredictionMethod,
    PredictionStrategy,
    TrackingEvaluation,
)
from results.models import KetQuaXoSo

# Thiết lập logging
logger = logging.getLogger(__name__)

METHODS_BTL_PATH = "predictions_tracker.methods_btl"


def get_all_method_classes() -> List[type]:
    """
    Quét toàn bộ các class method trong folder methods_btl (trừ base)

    Returns:
        List[type]: Danh sách các class method tìm được
    """
    method_classes = []
    try:
        package = importlib.import_module(METHODS_BTL_PATH)
        package_path = os.path.dirname(str(package.__file__))

        for fname in os.listdir(package_path):
            if fname.endswith(".py") and fname not in ("__init__.py", "base.py"):
                module_name = f"{METHODS_BTL_PATH}.{fname[:-3]}"
                try:
                    module = importlib.import_module(module_name)
                    for name, obj in inspect.getmembers(module, inspect.isclass):
                        if (
                            hasattr(obj, "get_code")
                            and hasattr(obj, "get_name")
                            and hasattr(obj, "calculate")
                            and name != "BasePredictionMethod"
                        ):
                            method_classes.append(obj)
                except ImportError as e:
                    logger.warning(f"Không thể import module {module_name}: {e}")
                    continue

    except Exception as e:
        logger.error(f"Lỗi khi quét methods: {e}")

    return method_classes


class Command(BaseCommand):
    help = "Quét, lưu và tính toán các phương pháp dự đoán trong methods_btl"

    def add_arguments(self, parser):
        parser.add_argument(
            "--date",
            type=str,
            help="Ngày phân tích cụ thể (format: YYYY-MM-DD)",
        )

        parser.add_argument(
            "--start-date",
            type=str,
            help="Ngày bắt đầu phân tích (format: YYYY-MM-DD)",
        )

        parser.add_argument(
            "--end-date",
            type=str,
            help="Ngày kết thúc phân tích (format: YYYY-MM-DD)",
        )

        parser.add_argument(
            "--days",
            type=int,
            default=3,
            help="Số ngày trong quá khứ cần phân tích (mặc định 30 ngày)",
        )

        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Chỉ hiển thị thông tin, không ghi vào database",
        )

        parser.add_argument(
            "--force",
            action="store_true",
            help="Buộc tạo lại dữ liệu ngay cả khi đã tồn tại",
        )
        parser.add_argument(
            "--clear-all",
            action="store_true",
            help="Xóa toàn bộ dữ liệu MethodPredictionResult và reset ID các bảng liên quan",
        )

    def handle(self, *args, **options):
        """
        Xử lý chính của command
        """
        try:

            # 1. Lấy các tham số
            dry_run = options["dry_run"]
            force = options["force"]
            clear_all = options["clear_all"]

            # 1.1 Xóa toàn bộ dữ liệu nếu được yêu cầu
            if clear_all:
                self._clear_all_data()
                return

            # 2. Xác định ngày cần phân tích
            dates_to_process = self._get_dates_to_process(options)

            # 3. Quét và lưu các method classes
            methods = self._load_prediction_methods(dry_run, force)

            if not methods:
                self.stdout.write(
                    self.style.WARNING("Không tìm thấy method nào để xử lý")
                )
                return

            # 4. Xử lý tính toán cho từng ngày
            if not dry_run:
                self._process_calculations(methods, dates_to_process, force)
            else:
                self.stdout.write(
                    f"DRY RUN: Sẽ xử lý {len(dates_to_process)} ngày với {len(methods)} methods"
                )

            self.stdout.write(
                self.style.SUCCESS("Hoàn thành xử lý prediction methods!")
            )

        except Exception as e:
            logger.exception("Lỗi trong load_prediction_methods command")
            raise CommandError(f"Lỗi xử lý: {str(e)}")

    def _get_dates_to_process(self, options: Dict[str, Any]) -> List[date]:
        """
        Xác định danh sách ngày cần xử lý dựa trên tham số đầu vào

        Args:
            options: Dict chứa các tham số command

        Returns:
            List[date]: Danh sách ngày cần xử lý
        """
        date_str = options["date"]
        start_date_str = options["start_date"]
        end_date_str = options["end_date"]
        days = options["days"]

        dates_to_process = []

        if date_str:
            # Xử lý ngày cụ thể
            try:
                specific_date = timezone.datetime.strptime(date_str, "%Y-%m-%d").date()
                dates_to_process.append(specific_date)
                self.stdout.write(f"Đang xử lý cho ngày: {specific_date}")
            except ValueError:
                raise CommandError(
                    f"Định dạng ngày không hợp lệ: {date_str}. Vui lòng sử dụng định dạng YYYY-MM-DD"
                )

        elif start_date_str and end_date_str:
            # Xử lý khoảng ngày
            try:
                start_date = timezone.datetime.strptime(
                    start_date_str, "%Y-%m-%d"
                ).date()
                end_date = timezone.datetime.strptime(end_date_str, "%Y-%m-%d").date()

                if start_date > end_date:
                    raise CommandError("Ngày bắt đầu không thể sau ngày kết thúc")

                current_date = start_date
                while current_date <= end_date:
                    dates_to_process.append(current_date)
                    current_date += timedelta(days=1)

                self.stdout.write(
                    f"Đang xử lý từ ngày {start_date} đến ngày {end_date}"
                )
            except ValueError:
                raise CommandError(
                    "Định dạng ngày không hợp lệ. Vui lòng sử dụng định dạng YYYY-MM-DD"
                )

        else:
            # Xử lý n ngày gần đây
            if days <= 0:
                raise CommandError("Số ngày phải là số dương")

            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=days - 1)

            current_date = start_date
            while current_date <= end_date:
                dates_to_process.append(current_date)
                current_date += timedelta(days=1)

            self.stdout.write(
                f"Đang xử lý {days} ngày gần đây (từ {start_date} đến {end_date})"
            )

        # Kiểm tra và lọc các ngày có kết quả xổ số
        valid_dates = []
        for process_date in dates_to_process:
            try:
                KetQuaXoSo.objects.get(ngay=process_date)
                valid_dates.append(process_date)
            except KetQuaXoSo.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(
                        f"Không có kết quả xổ số cho ngày {process_date}, bỏ qua"
                    )
                )

        return valid_dates

    def _clear_all_data(self):
        """
        Xóa toàn bộ dữ liệu và reset ID các bảng liên quan
        """
        from django.conf import settings
        from django.db import connection

        self.stdout.write("🔄 Bắt đầu xóa toàn bộ dữ liệu...")

        try:
            with transaction.atomic():
                # 1. Xóa dữ liệu theo thứ tự phụ thuộc
                deleted_counts = {}

                # TrackingEvaluation (phụ thuộc vào MethodPredictionResult)
                count = TrackingEvaluation.objects.count()
                TrackingEvaluation.objects.all().delete()
                deleted_counts["TrackingEvaluation"] = count

                # MethodPredictionResult (phụ thuộc vào DailyTrackingSession, PredictionMethod)
                count = MethodPredictionResult.objects.count()
                MethodPredictionResult.objects.all().delete()
                deleted_counts["MethodPredictionResult"] = count

                # DailyTrackingSession (phụ thuộc vào PredictionCycle)
                count = DailyTrackingSession.objects.count()
                DailyTrackingSession.objects.all().delete()
                deleted_counts["DailyTrackingSession"] = count

                # PredictionStrategy (phụ thuộc vào PredictionMethod)
                count = PredictionStrategy.objects.count()
                PredictionStrategy.objects.all().delete()
                deleted_counts["PredictionStrategy"] = count

                # PredictionMethod
                count = PredictionMethod.objects.count()
                PredictionMethod.objects.all().delete()
                deleted_counts["PredictionMethod"] = count

                # PredictionCycle
                count = PredictionCycle.objects.count()
                PredictionCycle.objects.all().delete()
                deleted_counts["PredictionCycle"] = count

                # 2. Reset AUTO_INCREMENT/SEQUENCE dựa trên database engine
                db_engine = settings.DATABASES["default"]["ENGINE"]

                with connection.cursor() as cursor:
                    tables_and_sequences = [
                        (
                            "predictions_tracker_trackingevaluation",
                            "predictions_tracker_trackingevaluation_id_seq",
                        ),
                        (
                            "predictions_tracker_methodpredictionresult",
                            "predictions_tracker_methodpredictionresult_id_seq",
                        ),
                        (
                            "predictions_tracker_dailytrackingsession",
                            "predictions_tracker_dailytrackingsession_id_seq",
                        ),
                        (
                            "predictions_tracker_predictionstrategy",
                            "predictions_tracker_predictionstrategy_id_seq",
                        ),
                        (
                            "predictions_tracker_predictionmethod",
                            "predictions_tracker_predictionmethod_id_seq",
                        ),
                        (
                            "predictions_tracker_predictioncycle",
                            "predictions_tracker_predictioncycle_id_seq",
                        ),
                    ]

                    if "postgresql" in db_engine:
                        # PostgreSQL: Reset sequence
                        for table, sequence in tables_and_sequences:
                            try:
                                cursor.execute(
                                    f"ALTER SEQUENCE {sequence} RESTART WITH 1;"
                                )
                                self.stdout.write(
                                    f"  ✓ Reset sequence cho bảng: {table}"
                                )
                            except Exception as seq_error:
                                # Nếu sequence name không đúng, thử tìm sequence tự động
                                try:
                                    cursor.execute(
                                        f"""
                                        SELECT pg_get_serial_sequence('{table}', 'id');
                                    """
                                    )
                                    result = cursor.fetchone()
                                    if result and result[0]:
                                        actual_sequence = result[0]
                                        cursor.execute(
                                            f"ALTER SEQUENCE {actual_sequence} RESTART WITH 1;"
                                        )
                                        self.stdout.write(
                                            f"  ✓ Reset sequence cho bảng: {table} (sequence: {actual_sequence})"
                                        )
                                    else:
                                        self.stdout.write(
                                            f"  ⚠ Không tìm thấy sequence cho bảng: {table}"
                                        )
                                except Exception as e:
                                    self.stdout.write(
                                        f"  ❌ Lỗi reset sequence cho {table}: {e}"
                                    )

                    elif "mysql" in db_engine:
                        # MySQL: Reset AUTO_INCREMENT
                        for table, _ in tables_and_sequences:
                            try:
                                cursor.execute(
                                    f"ALTER TABLE {table} AUTO_INCREMENT = 1;"
                                )
                                self.stdout.write(
                                    f"  ✓ Reset AUTO_INCREMENT cho bảng: {table}"
                                )
                            except Exception as e:
                                self.stdout.write(
                                    f"  ❌ Lỗi reset AUTO_INCREMENT cho {table}: {e}"
                                )

                    elif "sqlite" in db_engine:
                        # SQLite: Reset AUTOINCREMENT through sqlite_sequence
                        for table, _ in tables_and_sequences:
                            try:
                                cursor.execute(
                                    f"DELETE FROM sqlite_sequence WHERE name='{table}';"
                                )
                                self.stdout.write(
                                    f"  ✓ Reset AUTOINCREMENT cho bảng: {table}"
                                )
                            except Exception as e:
                                self.stdout.write(
                                    f"  ❌ Lỗi reset AUTOINCREMENT cho {table}: {e}"
                                )

                    else:
                        self.stdout.write(
                            f"  ⚠ Database engine không được hỗ trợ: {db_engine}"
                        )

                # 3. Hiển thị thống kê
                self.stdout.write("\n📊 Thống kê xóa dữ liệu:")
                for model_name, count in deleted_counts.items():
                    self.stdout.write(f"  - {model_name}: {count} bản ghi")

                self.stdout.write(
                    self.style.SUCCESS(
                        "\n✅ Hoàn thành xóa toàn bộ dữ liệu và reset ID!"
                    )
                )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Lỗi khi xóa dữ liệu: {e}"))
            raise CommandError(f"Lỗi xóa dữ liệu: {e}")

    def _load_prediction_methods(self, dry_run: bool, force: bool) -> List[tuple]:
        """
        Quét và lưu các prediction methods vào database

        Args:
            dry_run: Chỉ hiển thị thông tin, không lưu vào DB
            force: Buộc tạo lại dữ liệu

        Returns:
            List[tuple]: Danh sách (PredictionMethod, instance) đã được tạo
        """
        # 1. Quét method classes
        method_classes = get_all_method_classes()
        self.stdout.write(
            f"Tìm thấy {len(method_classes)} method classes trong methods_btl"
        )

        if not method_classes:
            self.stdout.write(self.style.WARNING("Không tìm thấy method class nào"))
            return []

        methods = []
        duplicate_codes = set()
        success_count = 0
        error_count = 0

        if dry_run:
            # Dry run - chỉ validate và hiển thị
            for cls in method_classes:
                try:
                    instance = cls()
                    code = instance.get_code()
                    name = instance.get_name()

                    if code in [m[1].get_code() for m in methods]:
                        duplicate_codes.add(code)
                        self.stdout.write(
                            self.style.ERROR(f"✗ Duplicate code: {code} trong {name}")
                        )
                        error_count += 1
                        continue

                    methods.append((None, instance))
                    self.stdout.write(f"✓ Sẽ tạo: {name} (code: {code})")
                    success_count += 1

                except Exception as e:
                    error_count += 1
                    self.stdout.write(
                        self.style.ERROR(f"✗ Lỗi khi khởi tạo {cls.__name__}: {e}")
                    )
        else:
            # Thực tế lưu vào database
            try:
                with transaction.atomic():
                    for cls in method_classes:
                        try:
                            instance = cls()
                            code = instance.get_code()
                            name = instance.get_name()
                            description = instance.get_description()
                            category = getattr(
                                instance, "get_category", lambda: "other"
                            )()
                            parameters = (
                                instance.get_parameters()
                                if hasattr(instance, "get_parameters")
                                else {}
                            )

                            # Kiểm tra duplicate code
                            if code in [m[1].get_code() for m in methods]:
                                duplicate_codes.add(code)
                                self.stdout.write(
                                    self.style.ERROR(
                                        f"✗ Duplicate code: {code} trong {name}"
                                    )
                                )
                                error_count += 1
                                continue

                            if force:
                                # Xóa method cũ nếu force
                                deleted_count = PredictionMethod.objects.filter(
                                    code=code
                                ).count()
                                if deleted_count > 0:
                                    PredictionMethod.objects.filter(code=code).delete()
                                    self.stdout.write(
                                        f"  Đã xóa {deleted_count} method cũ với code {code}"
                                    )
                            method, created = PredictionMethod.objects.update_or_create(
                                code=code,
                                defaults={
                                    "name": name,
                                    "description": description,
                                    "category": category,
                                    "parameters": parameters,
                                    "is_active": True,
                                    "priority": 5,
                                },
                            )

                            if created:
                                method_id = (
                                    getattr(method, "id", "unknown")
                                    if method
                                    else "unknown"
                                )
                                self.stdout.write(
                                    f"✓ Tạo mới: {name} (ID: {method_id})"
                                )
                            else:
                                method_id = (
                                    getattr(method, "id", "unknown")
                                    if method
                                    else "unknown"
                                )
                                self.stdout.write(
                                    f"✓ Cập nhật: {name} (ID: {method_id})"
                                )

                            # Tạo strategy
                            if force:
                                PredictionStrategy.objects.filter(
                                    method=method
                                ).delete()

                            strategy, strategy_created = (
                                PredictionStrategy.objects.update_or_create(
                                    method=method,
                                    defaults={
                                        "strategy_type": category,
                                        "ensemble_weight": 1.0,
                                        "ensemble_config": {},
                                    },
                                )
                            )

                            methods.append((method, instance))
                            success_count += 1

                        except Exception as e:
                            error_count += 1
                            self.stdout.write(
                                self.style.ERROR(f"✗ Lỗi khi xử lý {cls.__name__}: {e}")
                            )
                            logger.error(
                                f"Lỗi khi xử lý method {cls.__name__}", exc_info=True
                            )

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Lỗi transaction: {e}"))
                raise CommandError(f"Lỗi khi lưu methods: {e}")

        # Hiển thị thống kê
        self.stdout.write("\nThống kê Methods:")
        self.stdout.write(f"- Tổng số class tìm thấy: {len(method_classes)}")
        self.stdout.write(f"- Thành công: {success_count}")
        self.stdout.write(f"- Lỗi: {error_count}")

        if duplicate_codes:
            self.stdout.write(f"- Duplicate codes: {', '.join(duplicate_codes)}")

        return methods

    def _process_calculations(
        self, methods: List[tuple], dates_to_process: List[date], force: bool
    ):
        """
        Tính toán predictions cho các methods và ngày đã chọn - FIXED VERSION

        Args:
            methods: Danh sách (PredictionMethod, instance)
            dates_to_process: Danh sách ngày cần xử lý
            force: Buộc tạo lại dữ liệu
        """
        self.stdout.write(
            f"\nBắt đầu tính toán cho {len(methods)} methods trên {len(dates_to_process)} ngày..."
        )

        # Tạo hoặc cập nhật Prediction Cycle
        start_date = min(dates_to_process)
        end_date = max(dates_to_process)

        cycle, cycle_created = PredictionCycle.objects.update_or_create(
            cycle_name="Auto Import",
            defaults={
                "start_date": start_date,
                "end_date": end_date,
                "status": "completed",
                "tracking_days": 3,
            },
        )

        if cycle_created:
            self.stdout.write(f"✓ Tạo mới cycle: {cycle.cycle_name}")
        else:
            self.stdout.write(f"✓ Cập nhật cycle: {cycle.cycle_name}")

        total_success = 0
        total_error = 0

        for process_date in dates_to_process:
            try:
                ketqua = KetQuaXoSo.objects.get(ngay=process_date)
                self.stdout.write(f"\nĐang xử lý ngày {process_date}...")

                # Tạo data dict từ KetQuaXoSo
                data = self._create_data_dict(ketqua)

                # ✅ FIX: Tạo session CHỈ MỘT LẦN cho mỗi ngày, ngoài vòng lặp method
                if force:
                    DailyTrackingSession.objects.filter(
                        cycle=cycle, prediction_date=process_date
                    ).delete()

                session, session_created = (
                    DailyTrackingSession.objects.update_or_create(
                        cycle=cycle,
                        prediction_date=process_date,
                        defaults={
                            "session_id": f"auto_{process_date}",
                            "tracking_start_date": process_date,
                            "tracking_end_date": process_date + timedelta(days=3),
                            "status": "completed",
                        },
                    )
                )

                date_success = 0
                date_error = 0

                # ✅ FIX: Sử dụng session đã tạo cho TẤT CẢ methods
                for method, instance in methods:
                    try:
                        # Debug log
                        self.stdout.write(
                            f"  🔄 Đang xử lý method: {method.name} (ID: {method.id})"
                        )

                        # Tính toán prediction
                        result = instance.calculate(data)
                        numbers = (
                            result.get("two_digits_loto")
                            if isinstance(result, dict)
                            else result
                        )

                        if not numbers:
                            self.stdout.write(f"  ⚠ {method.name}: Không có kết quả")
                            continue

                        # ✅ FIX: Chỉ xóa method result của method cụ thể, không xóa toàn bộ session
                        if force:
                            MethodPredictionResult.objects.filter(
                                session=session, method=method
                            ).delete()

                        # Tạo method result
                        method_result, result_created = (
                            MethodPredictionResult.objects.update_or_create(
                                session=session,
                                method=method,
                                defaults={
                                    "base_prediction_numbers": numbers,
                                    "overall_confidence": 0.5,
                                },
                            )
                        )

                        # Debug log
                        action = "Tạo mới" if result_created else "Cập nhật"
                        self.stdout.write(
                            f"    📝 {action} MethodPredictionResult (ID: {method_result.pk})"
                        )

                        # Tạo tracking evaluation
                        self._create_tracking_evaluation(
                            session, method_result, ketqua, numbers, force
                        )

                        self.stdout.write(
                            f"  ✓ {method.name}: {', '.join(map(str, numbers))}"
                        )
                        date_success += 1

                    except Exception as e:
                        date_error += 1
                        self.stdout.write(self.style.ERROR(f"  ✗ {method.name}: {e}"))
                        logger.error(
                            f"Lỗi tính toán {method.name} cho {process_date}",
                            exc_info=True,
                        )

                self.stdout.write(
                    f"  Ngày {process_date}: {date_success} thành công, {date_error} lỗi"
                )
                total_success += date_success
                total_error += date_error

            except KetQuaXoSo.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(
                        f"Không có kết quả xổ số cho ngày {process_date}"
                    )
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Lỗi xử lý ngày {process_date}: {e}")
                )
                logger.error(f"Lỗi xử lý ngày {process_date}", exc_info=True)

        # Thống kê cuối cùng
        self.stdout.write(f"\nThống kê tính toán:")
        self.stdout.write(f"- Tổng số tính toán: {total_success + total_error}")
        self.stdout.write(f"- Thành công: {total_success}")
        self.stdout.write(f"- Lỗi: {total_error}")

        # Kiểm tra kết quả cuối cùng
        final_check = MethodPredictionResult.objects.values("method").distinct().count()
        self.stdout.write(f"- Số method có kết quả: {final_check}")

    def _create_data_dict(self, ketqua: KetQuaXoSo) -> Dict[str, str]:
        """
        Tạo data dict từ KetQuaXoSo object

        Args:
            ketqua: KetQuaXoSo object

        Returns:
            Dict[str, str]: Data dict với format chuẩn
        """
        return {
            "giai_db": ketqua.giai_db or "",
            "giai_1": ketqua.giai_1 or "",
            "giai_2_1": ketqua.giai_2_1 or "",
            "giai_2_2": ketqua.giai_2_2 or "",
            "giai_3_1": ketqua.giai_3_1 or "",
            "giai_3_2": ketqua.giai_3_2 or "",
            "giai_3_3": ketqua.giai_3_3 or "",
            "giai_3_4": ketqua.giai_3_4 or "",
            "giai_3_5": ketqua.giai_3_5 or "",
            "giai_3_6": ketqua.giai_3_6 or "",
            "giai_4_1": ketqua.giai_4_1 or "",
            "giai_4_2": ketqua.giai_4_2 or "",
            "giai_4_3": ketqua.giai_4_3 or "",
            "giai_4_4": ketqua.giai_4_4 or "",
            "giai_5_1": ketqua.giai_5_1 or "",
            "giai_5_2": ketqua.giai_5_2 or "",
            "giai_5_3": ketqua.giai_5_3 or "",
            "giai_5_4": ketqua.giai_5_4 or "",
            "giai_5_5": ketqua.giai_5_5 or "",
            "giai_5_6": ketqua.giai_5_6 or "",
            "giai_6_1": ketqua.giai_6_1 or "",
            "giai_6_2": ketqua.giai_6_2 or "",
            "giai_6_3": ketqua.giai_6_3 or "",
            "giai_7_1": ketqua.giai_7_1 or "",
            "giai_7_2": ketqua.giai_7_2 or "",
            "giai_7_3": ketqua.giai_7_3 or "",
            "giai_7_4": ketqua.giai_7_4 or "",
        }

    def _create_tracking_evaluation(
        self,
        session: DailyTrackingSession,
        method_result: MethodPredictionResult,
        ketqua: KetQuaXoSo,
        numbers: List[str],
        force: bool,
    ):
        """
        Tạo tracking evaluation cho method result

        Args:
            session: DailyTrackingSession object
            method_result: MethodPredictionResult object
            ketqua: KetQuaXoSo object
            numbers: Danh sách số dự đoán
            force: Buộc tạo lại dữ liệu
        """
        if force:
            TrackingEvaluation.objects.filter(
                session=session,
                method_result=method_result,
                evaluation_date=ketqua.ngay,
            ).delete()

        actual_numbers = list(ketqua.get_all_2digit_numbers())
        hit_numbers = list(set(numbers) & set(actual_numbers))
        hit_count = len(hit_numbers)
        total_predicted = len(numbers)
        hit_rate = (hit_count / total_predicted * 100) if total_predicted else 0

        TrackingEvaluation.objects.update_or_create(
            session=session,
            method_result=method_result,
            evaluation_date=ketqua.ngay,
            defaults={
                "days_after_prediction": 0,
                "actual_numbers": actual_numbers,
                "predicted_numbers": numbers,
                "hit_numbers": hit_numbers,
                "hit_count": hit_count,
                "total_predicted": total_predicted,
                "hit_rate": hit_rate,
                "wilson_score": 0,
            },
        )
