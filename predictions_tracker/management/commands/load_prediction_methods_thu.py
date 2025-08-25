import importlib
import inspect
import logging
import os
from datetime import date, timedelta
from typing import Any, Dict, List, Optional

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from predictions_tracker.models import (
    PredictionMethod,
    WeeklyPerformanceStats,
    WeeklyPredictionMethod,
    WeeklyTrackingSession,
)
from results.models import KetQuaXoSo

logger = logging.getLogger(__name__)

METHODS_THU_PATH = "predictions_tracker.methods_btl.method_theo_thu"


def get_weekly_method_classes() -> List[type]:
    """
    ✅ CHỈ quét các method classes trong folder method_theo_thu
    KHÔNG load các method khác
    """
    method_classes = []
    try:
        package = importlib.import_module(METHODS_THU_PATH)
        package_path = os.path.dirname(str(package.__file__))

        for fname in os.listdir(package_path):
            if fname.endswith(".py") and fname not in ("__init__.py",):
                module_name = f"{METHODS_THU_PATH}.{fname[:-3]}"
                try:
                    module = importlib.import_module(module_name)
                    for name, obj in inspect.getmembers(module, inspect.isclass):
                        if (
                            hasattr(obj, "get_code")
                            and hasattr(obj, "get_name")
                            and hasattr(obj, "calculate")
                            and name != "BasePredictionMethod"
                        ):
                            try:
                                # ✅ Tạo instance để test method
                                instance = obj()
                                code = instance.get_code()
                                # ✅ CHỈ LẤY WEEKLY METHODS
                                if any(
                                    day in code.upper()
                                    for day in [
                                        "T2",
                                        "T3",
                                        "T4",
                                        "T5",
                                        "T6",
                                        "T7",
                                        "CN",
                                    ]
                                ):
                                    method_classes.append(obj)
                            except Exception as e:
                                logger.warning(f"Lỗi khi tạo instance {name}: {e}")
                                continue
                except ImportError as e:
                    logger.warning(f"Không thể import module {module_name}: {e}")

    except Exception as e:
        logger.error(f"Lỗi khi quét weekly methods: {e}")

    return method_classes


class Command(BaseCommand):
    help = "Xử lý prediction methods theo thứ trong tuần"

    def add_arguments(self, parser):
        parser.add_argument(
            "--weekday",
            type=int,
            choices=range(7),
            help="Thứ cụ thể cần xử lý (0=Thứ 2, 6=Chủ nhật)",
        )

        parser.add_argument(
            "--date",
            type=str,
            help="Ngày cụ thể cần xử lý (YYYY-MM-DD)",
        )

        parser.add_argument(
            "--weeks-back",
            type=int,
            default=4,
            help="Số tuần trong quá khứ cần xử lý",
        )

        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Chỉ hiển thị thông tin, không ghi vào database",
        )

        parser.add_argument(
            "--force",
            action="store_true",
            help="Buộc tạo lại dữ liệu",
        )

    def handle(self, *args, **options):
        try:
            self.stdout.write(
                self.style.SUCCESS("🗓️  WEEKLY PREDICTION METHODS COMMAND")
            )
            self.stdout.write("✅ Chỉ xử lý methods theo thứ trong tuần")
            self.stdout.write("❌ KHÔNG xử lý daily methods")

            dry_run = options["dry_run"]
            force = options["force"]

            # 1. Quét và tạo weekly methods
            weekly_methods = self._create_weekly_methods(dry_run, force)

            if not weekly_methods:
                self.stdout.write(
                    self.style.WARNING("Không tìm thấy weekly method nào")
                )
                return

            # 2. Xác định ngày/thứ cần xử lý
            target_dates = self._get_target_dates(options)

            # 3. Xử lý predictions cho các ngày
            if not dry_run:
                self._process_weekly_predictions(weekly_methods, target_dates, force)
            else:
                self.stdout.write(
                    f"DRY RUN: Sẽ xử lý {len(target_dates)} ngày với {len(weekly_methods)} weekly methods"
                )

            self.stdout.write(
                self.style.SUCCESS("✅ Hoàn thành xử lý weekly prediction methods!")
            )

        except Exception as e:
            logger.exception("Lỗi trong load_prediction_methods_thu command")
            raise CommandError(f"Lỗi xử lý: {str(e)}")

    def _create_weekly_methods(
        self, dry_run: bool, force: bool
    ) -> List[WeeklyPredictionMethod]:
        """✅ TẠO CHỈ WeeklyPredictionMethod từ method classes"""
        method_classes = get_weekly_method_classes()
        self.stdout.write(f"📊 Tìm thấy {len(method_classes)} weekly method classes")

        weekly_methods = []

        for cls in method_classes:
            try:
                instance = cls()
                code = instance.get_code()
                name = instance.get_name()

                # ✅ Xác định thứ từ tên file hoặc code
                weekday = self._extract_weekday_from_code(code)
                if weekday is None:
                    self.stdout.write(
                        self.style.WARNING(f"⚠️  Không thể xác định thứ từ code: {code}")
                    )
                    continue

                weekday_name = [
                    "Thứ 2",
                    "Thứ 3",
                    "Thứ 4",
                    "Thứ 5",
                    "Thứ 6",
                    "Thứ 7",
                    "Chủ nhật",
                ][weekday]

                if dry_run:
                    self.stdout.write(
                        f"✅ Sẽ tạo weekly method: {name} ({weekday_name})"
                    )
                    continue

                # ✅ Tạo hoặc lấy base method (CHỈ CHO WEEKLY)
                base_method, created = PredictionMethod.objects.get_or_create(
                    code=code,
                    defaults={
                        "name": name,
                        "description": getattr(
                            instance,
                            "get_description",
                            lambda: f"Weekly method for {weekday_name}",
                        )(),
                        "category": "pattern",  # Weekly methods thường là pattern-based
                        "is_active": True,
                    },
                )

                if created:
                    self.stdout.write(f"📝 Tạo base method: {base_method.name}")

                # ✅ Tạo weekly method
                if force:
                    WeeklyPredictionMethod.objects.filter(
                        base_method=base_method, target_weekday=weekday
                    ).delete()

                weekly_method, w_created = WeeklyPredictionMethod.objects.get_or_create(
                    base_method=base_method,
                    target_weekday=weekday,
                    defaults={
                        "tracking_weeks": 4,
                        "is_active": True,
                    },
                )

                weekly_methods.append(weekly_method)

                action = "✅ Tạo mới" if w_created else "🔄 Cập nhật"
                self.stdout.write(f"{action}: {weekly_method}")

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Lỗi xử lý {cls.__name__}: {e}"))

        return weekly_methods

    def _extract_weekday_from_code(self, code: str) -> Optional[int]:
        """Trích xuất thứ từ code method"""
        # Mapping từ ký hiệu thứ sang số
        weekday_map = {
            "T2": 0,  # Thứ 2 = Monday
            "T3": 1,  # Thứ 3 = Tuesday
            "T4": 2,  # Thứ 4 = Wednesday
            "T5": 3,  # Thứ 5 = Thursday
            "T6": 4,  # Thứ 6 = Friday
            "T7": 5,  # Thứ 7 = Saturday
            "CN": 6,  # Chủ nhật = Sunday
        }

        code_upper = code.upper()
        for key, value in weekday_map.items():
            if key in code_upper:
                return value

        return None

    def _get_target_dates(self, options: Dict[str, Any]) -> List[date]:
        """Xác định danh sách ngày cần xử lý"""
        target_dates = []

        if options["date"]:
            # Xử lý ngày cụ thể
            try:
                target_date = timezone.datetime.strptime(
                    options["date"], "%Y-%m-%d"
                ).date()
                target_dates.append(target_date)
            except ValueError:
                raise CommandError("Định dạng ngày không hợp lệ")

        elif options["weekday"] is not None:
            # Xử lý thứ cụ thể trong vài tuần gần đây
            weekday = options["weekday"]
            weeks_back = options["weeks_back"]

            today = timezone.now().date()
            current_weekday = today.weekday()

            # Tìm ngày gần nhất của thứ đó
            days_diff = weekday - current_weekday
            if days_diff > 0:
                days_diff -= 7  # Lấy tuần trước

            recent_date = today + timedelta(days=days_diff)

            # Lấy các ngày cùng thứ trong weeks_back tuần
            for i in range(weeks_back):
                check_date = recent_date - timedelta(weeks=i)
                target_dates.append(check_date)

        else:
            # Xử lý tất cả các thứ trong tuần gần đây
            weeks_back = options["weeks_back"]
            today = timezone.now().date()

            for week_offset in range(weeks_back):
                for weekday in range(7):
                    # Tính ngày cho thứ này trong tuần đó
                    days_back = week_offset * 7 + (today.weekday() - weekday)
                    if days_back < 0:
                        days_back += 7

                    check_date = today - timedelta(days=days_back)
                    target_dates.append(check_date)

        # Lọc các ngày có kết quả xổ số
        valid_dates = []
        for target_date in target_dates:
            try:
                KetQuaXoSo.objects.get(ngay=target_date)
                valid_dates.append(target_date)
            except KetQuaXoSo.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f"Không có kết quả cho {target_date}")
                )

        return sorted(set(valid_dates))

    def _process_weekly_predictions(
        self,
        weekly_methods: List[WeeklyPredictionMethod],
        target_dates: List[date],
        force: bool,
    ):
        """Xử lý dự đoán cho các weekly methods"""
        self.stdout.write(
            f"\nXử lý {len(weekly_methods)} methods trên {len(target_dates)} ngày..."
        )

        total_processed = 0
        total_errors = 0

        for target_date in target_dates:
            try:
                # Lấy kết quả xổ số cho ngày này
                ketqua = KetQuaXoSo.objects.get(ngay=target_date)
                weekday = target_date.weekday()

                # Lọc methods phù hợp với thứ này
                matching_methods = [
                    wm for wm in weekly_methods if wm.target_weekday == weekday
                ]

                if not matching_methods:
                    continue

                self.stdout.write(
                    f"\nXử lý {target_date} ({weekday}) - {len(matching_methods)} methods"
                )

                # Tạo data cho calculation
                data = self._create_data_dict(ketqua)

                for weekly_method in matching_methods:
                    try:
                        # Skip nếu đã xử lý và không force
                        if (
                            not force
                            and WeeklyTrackingSession.objects.filter(
                                weekly_method=weekly_method, prediction_date=target_date
                            ).exists()
                        ):
                            continue

                        # Tính toán prediction
                        base_instance = self._create_method_instance(
                            weekly_method.base_method
                        )
                        result = base_instance.calculate(data)
                        numbers = (
                            result.get("two_digits_loto")
                            if isinstance(result, dict)
                            else result
                        )

                        if not numbers:
                            continue

                        # Tạo tracking session
                        if force:
                            WeeklyTrackingSession.objects.filter(
                                weekly_method=weekly_method, prediction_date=target_date
                            ).delete()

                        # ✅ Tính tracking_date = thứ cùng tên tuần sau
                        next_week_tracking_date = target_date + timedelta(days=7)

                        session, created = WeeklyTrackingSession.objects.get_or_create(
                            weekly_method=weekly_method,
                            prediction_date=target_date,
                            defaults={
                                "tracking_date": next_week_tracking_date,
                                "predicted_numbers": numbers,
                                "total_predicted": (
                                    len(numbers) if isinstance(numbers, list) else 0
                                ),
                                "status": "pending",
                            },
                        )

                        # Kiểm tra xem đã có kết quả tracking chưa
                        tracking_date = session.tracking_date
                        try:
                            tracking_result = KetQuaXoSo.objects.get(ngay=tracking_date)
                            session.actual_numbers = list(
                                tracking_result.get_all_2digit_numbers()
                            )
                            session.calculate_results()

                            self.stdout.write(
                                f"  ✓ {weekly_method.base_method.name}: {session.hit_count}/{session.total_predicted} ({session.hit_rate:.1f}%)"
                            )
                        except KetQuaXoSo.DoesNotExist:
                            self.stdout.write(
                                f"  ⏳ {weekly_method.base_method.name}: Chờ kết quả {tracking_date}"
                            )

                        total_processed += 1

                    except Exception as e:
                        total_errors += 1
                        self.stdout.write(
                            self.style.ERROR(
                                f"  ✗ {weekly_method.base_method.name}: {e}"
                            )
                        )

            except Exception as e:
                total_errors += 1
                self.stdout.write(self.style.ERROR(f"Lỗi xử lý {target_date}: {e}"))

        # Cập nhật thống kê
        self._update_performance_stats(weekly_methods)

        self.stdout.write(
            f"\nKết quả: {total_processed} thành công, {total_errors} lỗi"
        )

    def _create_data_dict(self, ketqua: KetQuaXoSo) -> Dict[str, str]:
        """Tạo data dict từ KetQuaXoSo object"""
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

    def _create_method_instance(self, base_method: PredictionMethod):
        """Tạo instance của method class từ code"""
        method_classes = get_weekly_method_classes()

        for cls in method_classes:
            try:
                instance = cls()
                if instance.get_code() == base_method.code:
                    return instance
            except:
                continue

        raise ValueError(f"Không tìm thấy method class cho {base_method.code}")

    def _update_performance_stats(self, weekly_methods: List[WeeklyPredictionMethod]):
        """Cập nhật thống kê hiệu suất"""
        current_date = timezone.now().date()
        year = current_date.year
        month = current_date.month

        for weekly_method in weekly_methods:
            stats, created = WeeklyPerformanceStats.objects.get_or_create(
                weekly_method=weekly_method, year=year, month=month
            )
            stats.update_stats()

            # Cập nhật weekly_method stats
            recent_sessions = WeeklyTrackingSession.objects.filter(
                weekly_method=weekly_method, status="completed"
            ).order_by("-prediction_date")[
                :20
            ]  # 20 sessions gần nhất

            if recent_sessions:
                total_predictions = sum(s.total_predicted for s in recent_sessions)
                total_hits = sum(s.hit_count for s in recent_sessions)

                weekly_method.total_weekly_predictions = total_predictions
                weekly_method.total_weekly_hits = total_hits
                weekly_method.weekly_success_rate = (
                    (total_hits / total_predictions * 100) if total_predictions else 0
                )
                weekly_method.last_prediction_week = recent_sessions[0].prediction_date
                weekly_method.save()
