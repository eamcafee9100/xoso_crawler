import json
from datetime import date, datetime, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Avg, Count, Q, Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django import forms

from .forms import (
    BaoCaoHieuQuaForm,
    DuDoanForm,
    LoKhungForm,
    PhanTichSoLieuForm,
    PhuongPhapTinhToanForm,
)
from .models import (
    BaoCaoHieuQua,
    CanhBaoHieuQua,
    DuDoan,
    LoKhung,
    PhanTichSoLieu,
    PhuongPhapTinhToan,
)
from .utils.method_executor import method_executor

# ==================== PHƯƠNG PHÁP TÍNH TOÁN VIEWS ====================


@login_required
def phuong_phap_list(request):
    """Danh sách các phương pháp tính toán"""
    phuong_phap_list = PhuongPhapTinhToan.objects.filter(nguoi_tao=request.user)

    # Lọc theo trạng thái
    trang_thai = request.GET.get("trang_thai")
    if trang_thai:
        phuong_phap_list = phuong_phap_list.filter(trang_thai=trang_thai)

    # Lọc theo loại phương pháp
    loai_phuong_phap = request.GET.get("loai_phuong_phap")
    if loai_phuong_phap:
        phuong_phap_list = phuong_phap_list.filter(loai_phuong_phap=loai_phuong_phap)

    # Tìm kiếm
    search = request.GET.get("search")
    if search:
        phuong_phap_list = phuong_phap_list.filter(
            Q(ten_phuong_phap__icontains=search) | Q(mo_ta__icontains=search)
        )

    # Sắp xếp
    sort_by = request.GET.get("sort", "ty_le_thanh_cong")
    if sort_by == "ty_le_thanh_cong":
        # Sắp xếp theo tỷ lệ thành công (calculated field)
        phuong_phap_list = sorted(
            phuong_phap_list, key=lambda x: x.ty_le_thanh_cong, reverse=True
        )
    else:
        phuong_phap_list = phuong_phap_list.order_by(f"-{sort_by}")

    # Phân trang
    paginator = Paginator(phuong_phap_list, 50)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "trang_thai_choices": PhuongPhapTinhToan.STATUS_CHOICES,
        "loai_phuong_phap_choices": PhuongPhapTinhToan.LOAI_PHUONG_PHAP_CHOICES,
        "current_filters": {
            "trang_thai": trang_thai,
            "loai_phuong_phap": loai_phuong_phap,
            "search": search,
            "sort": sort_by,
        },
    }

    return render(request, "lokhung/phuong_phap/list.html", context)


@login_required
def phuong_phap_detail(request, pk):
    """Chi tiết phương pháp tính toán"""
    phuong_phap = get_object_or_404(PhuongPhapTinhToan, pk=pk, nguoi_tao=request.user)

    # Lấy dự đoán gần đây
    du_doan_list = DuDoan.objects.filter(phuong_phap=phuong_phap).order_by("-ngay_tao")[
        :10
    ]

    # Lấy báo cáo hiệu quả gần nhất
    bao_cao_gan_nhat = BaoCaoHieuQua.objects.filter(phuong_phap=phuong_phap).first()

    # Lấy cảnh báo chưa xử lý
    canh_bao_list = CanhBaoHieuQua.objects.filter(
        phuong_phap=phuong_phap, da_xu_ly=False
    ).order_by("-ngay_canh_bao")

    # Thống kê nhanh
    tong_du_doan = DuDoan.objects.filter(phuong_phap=phuong_phap).count()
    du_doan_dung = DuDoan.objects.filter(
        phuong_phap=phuong_phap, trang_thai="trung"
    ).count()

    context = {
        "phuong_phap": phuong_phap,
        "du_doan_list": du_doan_list,
        "bao_cao_gan_nhat": bao_cao_gan_nhat,
        "canh_bao_list": canh_bao_list,
        "tong_du_doan": tong_du_doan,
        "du_doan_dung": du_doan_dung,
    }

    return render(request, "lokhung/phuong_phap/detail.html", context)


@login_required
def phuong_phap_create(request):
    """Tạo phương pháp tính toán mới"""
    if request.method == "POST":
        form = PhuongPhapTinhToanForm(request.POST)
        if form.is_valid():
            phuong_phap = form.save(commit=False)
            phuong_phap.nguoi_tao = request.user
            phuong_phap.save()
            messages.success(request, "Tạo phương pháp thành công!")
            return redirect("phuong_phap_detail", pk=phuong_phap.pk)
    else:
        form = PhuongPhapTinhToanForm()

    context = {"form": form, "title": "Tạo phương pháp mới"}

    return render(request, "lokhung/phuong_phap/form.html", context)


@login_required
def phuong_phap_edit(request, pk):
    """Chỉnh sửa phương pháp tính toán"""
    phuong_phap = get_object_or_404(PhuongPhapTinhToan, pk=pk, nguoi_tao=request.user)

    if request.method == "POST":
        form = PhuongPhapTinhToanForm(request.POST, instance=phuong_phap)
        if form.is_valid():
            form.save()
            messages.success(request, "Cập nhật phương pháp thành công!")
            return redirect("phuong_phap_detail", pk=phuong_phap.pk)
    else:
        form = PhuongPhapTinhToanForm(instance=phuong_phap)

    context = {
        "form": form,
        "phuong_phap": phuong_phap,
        "title": "Chỉnh sửa phương pháp",
    }

    return render(request, "lokhung/phuong_phap/form.html", context)


@login_required
def phuong_phap_delete(request, pk):
    """Xóa phương pháp tính toán"""
    phuong_phap = get_object_or_404(PhuongPhapTinhToan, pk=pk, nguoi_tao=request.user)

    if request.method == "POST":
        phuong_phap.delete()
        messages.success(request, "Xóa phương pháp thành công!")
        return redirect("phuong_phap_list")

    context = {"phuong_phap": phuong_phap}

    return render(request, "lokhung/phuong_phap/delete.html", context)


# ==================== DỰ ĐOÁN VIEWS ====================


@login_required
def du_doan_list(request):
    """Danh sách dự đoán"""
    du_doan_list = DuDoan.objects.filter(nguoi_tao=request.user)

    # Lọc theo ngày
    ngay_tu = request.GET.get("ngay_tu")
    ngay_den = request.GET.get("ngay_den")

    if ngay_tu:
        du_doan_list = du_doan_list.filter(ngay_du_doan__gte=ngay_tu)
    if ngay_den:
        du_doan_list = du_doan_list.filter(ngay_du_doan__lte=ngay_den)

    # Lọc theo trạng thái
    trang_thai = request.GET.get("trang_thai")
    if trang_thai:
        du_doan_list = du_doan_list.filter(trang_thai=trang_thai)

    # Lọc theo phương pháp
    phuong_phap_id = request.GET.get("phuong_phap")
    if phuong_phap_id:
        du_doan_list = du_doan_list.filter(phuong_phap_id=phuong_phap_id)

    # Sắp xếp
    sort_by = request.GET.get("sort", "-ngay_du_doan")
    du_doan_list = du_doan_list.order_by(sort_by)

    # Phân trang
    paginator = Paginator(du_doan_list, 50)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Lấy danh sách phương pháp cho filter
    phuong_phap_list = PhuongPhapTinhToan.objects.filter(nguoi_tao=request.user)

    context = {
        "page_obj": page_obj,
        "phuong_phap_list": phuong_phap_list,
        "trang_thai_choices": DuDoan.TRANG_THAI_CHOICES,
        "current_filters": {
            "ngay_tu": ngay_tu,
            "ngay_den": ngay_den,
            "trang_thai": trang_thai,
            "phuong_phap": phuong_phap_id,
            "sort": sort_by,
        },
    }

    return render(request, "lokhung/du_doan/list.html", context)


@login_required
def du_doan_detail(request, pk):
    """Chi tiết dự đoán"""
    du_doan = get_object_or_404(DuDoan, pk=pk, nguoi_tao=request.user)

    context = {"du_doan": du_doan}

    return render(request, "lokhung/du_doan/detail.html", context)


@login_required
def du_doan_create(request):
    """Tạo dự đoán mới"""
    if request.method == "POST":
        form = DuDoanForm(request.POST, user=request.user)
        if form.is_valid():
            du_doan = form.save(commit=False)
            du_doan.nguoi_tao = request.user
            du_doan.save()
            messages.success(request, "Tạo dự đoán thành công!")
            return redirect("du_doan_detail", pk=du_doan.pk)
    else:
        form = DuDoanForm(user=request.user)

    context = {"form": form, "title": "Tạo dự đoán mới"}

    return render(request, "lokhung/du_doan/form.html", context)


@login_required
def du_doan_edit(request, pk):
    """Chỉnh sửa dự đoán"""
    du_doan = get_object_or_404(DuDoan, pk=pk, nguoi_tao=request.user)

    if request.method == "POST":
        form = DuDoanForm(request.POST, instance=du_doan, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Cập nhật dự đoán thành công!")
            return redirect("du_doan_detail", pk=du_doan.pk)
    else:
        form = DuDoanForm(instance=du_doan, user=request.user)

    context = {"form": form, "du_doan": du_doan, "title": "Chỉnh sửa dự đoán"}

    return render(request, "lokhung/du_doan/form.html", context)


@login_required
@require_http_methods(["POST"])
def du_doan_check_result(request, pk):
    """Kiểm tra kết quả dự đoán"""
    du_doan = get_object_or_404(DuDoan, pk=pk, nguoi_tao=request.user)

    try:
        ket_qua = du_doan.kiem_tra_ket_qua()
        if ket_qua:
            messages.success(request, f"Dự đoán {du_doan.so_du_doan} đã trúng!")
        else:
            messages.info(request, f"Dự đoán {du_doan.so_du_doan} đã trượt.")
    except Exception as e:
        messages.error(request, f"Lỗi khi kiểm tra kết quả: {str(e)}")

    return redirect("du_doan_detail", pk=pk)


# ==================== LÔ KHUNG VIEWS ====================


@login_required
def lo_khung_list(request):
    """Danh sách lô khung"""
    lo_khung_list = LoKhung.objects.filter(nguoi_tao=request.user)

    # Lọc theo trạng thái
    trang_thai = request.GET.get("trang_thai")
    if trang_thai:
        lo_khung_list = lo_khung_list.filter(trang_thai=trang_thai)

    # Lọc theo thời gian
    hien_tai = request.GET.get("hien_tai")
    if hien_tai == "true":
        today = timezone.now().date()
        lo_khung_list = lo_khung_list.filter(
            ngay_bat_dau__lte=today, ngay_ket_thuc__gte=today
        )

    # Sắp xếp
    lo_khung_list = lo_khung_list.order_by("-ngay_tao")

    # Phân trang
    paginator = Paginator(lo_khung_list, 50)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "trang_thai_choices": LoKhung.TRANG_THAI_CHOICES,
        "current_filters": {
            "trang_thai": trang_thai,
            "hien_tai": hien_tai,
        },
    }

    return render(request, "lokhung/lo_khung/list.html", context)


@login_required
def lo_khung_detail(request, pk):
    """Chi tiết lô khung"""
    lo_khung = get_object_or_404(LoKhung, pk=pk, nguoi_tao=request.user)

    context = {"lo_khung": lo_khung}

    return render(request, "lokhung/lo_khung/detail.html", context)


@login_required
def lo_khung_create(request):
    """Tạo lô khung mới"""
    if request.method == "POST":
        form = LoKhungForm(request.POST, user=request.user)
        if form.is_valid():
            lo_khung = form.save(commit=False)
            lo_khung.nguoi_tao = request.user
            lo_khung.save()
            form.save_m2m()  # Lưu many-to-many relationships
            messages.success(request, "Tạo lô khung thành công!")
            return redirect("lokhung:lo_khung_detail", pk=lo_khung.pk)
    else:
        form = LoKhungForm(user=request.user)

    context = {"form": form, "title": "Tạo lô khung mới"}

    return render(request, "lokhung/lo_khung/form.html", context)


@login_required
def lo_khung_edit(request, pk):
    """Chỉnh sửa lô khung"""
    lo_khung = get_object_or_404(LoKhung, pk=pk, nguoi_tao=request.user)

    if request.method == "POST":
        form = LoKhungForm(request.POST, instance=lo_khung, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Cập nhật lô khung thành công!")
            return redirect("lo_khung_detail", pk=lo_khung.pk)
    else:
        form = LoKhungForm(instance=lo_khung, user=request.user)

    context = {"form": form, "lo_khung": lo_khung, "title": "Chỉnh sửa lô khung"}

    return render(request, "lokhung/lo_khung/form.html", context)


# ==================== BÁO CÁO HIỆU QUẢ VIEWS ====================


@login_required
def bao_cao_list(request):
    """Danh sách báo cáo hiệu quả"""
    bao_cao_list = BaoCaoHieuQua.objects.filter(
        phuong_phap__nguoi_tao=request.user
    ).select_related("phuong_phap")

    # Lọc theo loại báo cáo
    loai_bao_cao = request.GET.get("loai_bao_cao")
    if loai_bao_cao:
        bao_cao_list = bao_cao_list.filter(loai_bao_cao=loai_bao_cao)

    # Lọc theo phương pháp
    phuong_phap_id = request.GET.get("phuong_phap")
    if phuong_phap_id:
        bao_cao_list = bao_cao_list.filter(phuong_phap_id=phuong_phap_id)

    # Sắp xếp
    bao_cao_list = bao_cao_list.order_by("-ngay_tao")

    # Phân trang
    paginator = Paginator(bao_cao_list, 50)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Lấy danh sách phương pháp cho filter
    phuong_phap_list = PhuongPhapTinhToan.objects.filter(nguoi_tao=request.user)

    context = {
        "page_obj": page_obj,
        "phuong_phap_list": phuong_phap_list,
        "loai_bao_cao_choices": BaoCaoHieuQua.LOAI_BAO_CAO_CHOICES,
        "current_filters": {
            "loai_bao_cao": loai_bao_cao,
            "phuong_phap": phuong_phap_id,
        },
    }

    return render(request, "lokhung/bao_cao/list.html", context)


@login_required
def bao_cao_detail(request, pk):
    """Chi tiết báo cáo hiệu quả"""
    bao_cao = get_object_or_404(
        BaoCaoHieuQua, pk=pk, phuong_phap__nguoi_tao=request.user
    )

    context = {"bao_cao": bao_cao}

    return render(request, "lokhung/bao_cao/detail.html", context)


@login_required
def bao_cao_create(request):
    """Tạo báo cáo hiệu quả"""
    if request.method == "POST":
        phuong_phap_id = request.POST.get("phuong_phap")
        tu_ngay = datetime.strptime(request.POST.get("tu_ngay"), "%Y-%m-%d").date()
        den_ngay = datetime.strptime(request.POST.get("den_ngay"), "%Y-%m-%d").date()
        loai_bao_cao = request.POST.get("loai_bao_cao", "custom")
        print(
            f"Phương pháp ID: {phuong_phap_id}, Từ ngày: {tu_ngay}, Đến ngày: {den_ngay}, Loại báo cáo: {loai_bao_cao}"
        )
        try:
            phuong_phap = PhuongPhapTinhToan.objects.get(
                pk=phuong_phap_id, nguoi_tao=request.user
            )

            bao_cao = BaoCaoHieuQua.tao_bao_cao(
                phuong_phap=phuong_phap,
                tu_ngay=tu_ngay,
                den_ngay=den_ngay,
                loai_bao_cao=loai_bao_cao,
            )
            messages.success(request, "Tạo báo cáo thành công!")
            print("Báo cáo đã được tạo:", bao_cao)
            return redirect("lokhung:bao_cao_detail", pk=bao_cao.pk)

        except PhuongPhapTinhToan.DoesNotExist:
            messages.error(request, "Phương pháp không tồn tại!")
        except Exception as e:
            messages.error(request, f"Lỗi khi tạo báo cáo: {str(e)}")
        # Lỗi khi tạo báo cáo: Cannot filter a query once a slice has been taken.
    # Lấy danh sách phương pháp
    phuong_phap_list = PhuongPhapTinhToan.objects.filter(nguoi_tao=request.user)

    context = {
        "phuong_phap_list": phuong_phap_list,
        "loai_bao_cao_choices": BaoCaoHieuQua.LOAI_BAO_CAO_CHOICES,
        "title": "Tạo báo cáo hiệu quả",
    }

    return render(request, "lokhung/bao_cao/create.html", context)


# ==================== PHÂN TÍCH SỐ LIỆU VIEWS ====================


@login_required
def phan_tich_list(request):
    """Danh sách phân tích số liệu"""
    phan_tich_list = PhanTichSoLieu.objects.all().order_by("-ngay_phan_tich")

    # Lọc theo ngày
    ngay_tu = request.GET.get("ngay_tu")
    ngay_den = request.GET.get("ngay_den")

    if ngay_tu:
        phan_tich_list = phan_tich_list.filter(ngay_phan_tich__gte=ngay_tu)
    if ngay_den:
        phan_tich_list = phan_tich_list.filter(ngay_phan_tich__lte=ngay_den)

    # Phân trang
    paginator = Paginator(phan_tich_list, 50)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "current_filters": {
            "ngay_tu": ngay_tu,
            "ngay_den": ngay_den,
        },
    }

    return render(request, "lokhung/phan_tich/list.html", context)


@login_required
def phan_tich_detail(request, pk):
    """Chi tiết phân tích số liệu"""
    phan_tich = get_object_or_404(PhanTichSoLieu, pk=pk)

    context = {"phan_tich": phan_tich}

    return render(request, "lokhung/phan_tich/detail.html", context)


@login_required
@require_http_methods(["POST"])
def phan_tich_create_auto(request):
    """Tạo phân tích tự động cho ngày được chọn"""
    ngay_phan_tich = request.POST.get("ngay_phan_tich")

    try:
        ngay = datetime.strptime(ngay_phan_tich, "%Y-%m-%d").date()
        phan_tich = PhanTichSoLieu.tao_phan_tich_tu_dong(ngay)

        if phan_tich:
            messages.success(request, f"Tạo phân tích cho ngày {ngay} thành công!")
            return redirect("phan_tich_detail", pk=phan_tich.pk)
        else:
            messages.error(
                request, "Không thể tạo phân tích. Kiểm tra lại dữ liệu kết quả xổ số."
            )
    except ValueError:
        messages.error(request, "Định dạng ngày không hợp lệ!")
    except Exception as e:
        messages.error(request, f"Lỗi: {str(e)}")

    return redirect("phan_tich_list")


# ==================== CẢNH BÁO HIỆU QUẢ VIEWS ====================


@login_required
def canh_bao_list(request):
    """Danh sách cảnh báo hiệu quả"""
    canh_bao_list = CanhBaoHieuQua.objects.filter(
        phuong_phap__nguoi_tao=request.user
    ).select_related("phuong_phap")

    # Lọc theo trạng thái xử lý
    da_xu_ly = request.GET.get("da_xu_ly")
    if da_xu_ly == "true":
        canh_bao_list = canh_bao_list.filter(da_xu_ly=True)
    elif da_xu_ly == "false":
        canh_bao_list = canh_bao_list.filter(da_xu_ly=False)

    # Lọc theo mức độ
    muc_do = request.GET.get("muc_do")
    if muc_do:
        canh_bao_list = canh_bao_list.filter(muc_do=muc_do)

    # Sắp xếp
    canh_bao_list = canh_bao_list.order_by("-ngay_canh_bao")

    # Phân trang
    paginator = Paginator(canh_bao_list, 50)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "muc_do_choices": CanhBaoHieuQua.MUC_DO_CHOICES,
        "current_filters": {
            "da_xu_ly": da_xu_ly,
            "muc_do": muc_do,
        },
    }

    return render(request, "lokhung/canh_bao/list.html", context)


@login_required
def canh_bao_detail(request, pk):
    """Chi tiết cảnh báo"""
    canh_bao = get_object_or_404(
        CanhBaoHieuQua, pk=pk, phuong_phap__nguoi_tao=request.user
    )

    context = {"canh_bao": canh_bao}

    return render(request, "lokhung/canh_bao/detail.html", context)


@login_required
@require_http_methods(["POST"])
def canh_bao_mark_resolved(request, pk):
    """Đánh dấu cảnh báo đã xử lý"""
    canh_bao = get_object_or_404(
        CanhBaoHieuQua, pk=pk, phuong_phap__nguoi_tao=request.user
    )

    ghi_chu = request.POST.get("ghi_chu", "")
    canh_bao.danh_dau_da_xu_ly(ghi_chu)

    messages.success(request, "Đã đánh dấu cảnh báo đã xử lý!")
    return redirect("canh_bao_detail", pk=pk)


# ==================== DASHBOARD & API VIEWS ====================


@login_required
def dashboard(request):
    """Dashboard tổng quan"""
    # Thống kê cơ bản
    tong_phuong_phap = PhuongPhapTinhToan.objects.filter(nguoi_tao=request.user).count()
    tong_du_doan = DuDoan.objects.filter(nguoi_tao=request.user).count()
    tong_lo_khung = LoKhung.objects.filter(nguoi_tao=request.user).count()

    # Dự đoán gần đây
    du_doan_gan_day = DuDoan.objects.filter(nguoi_tao=request.user).order_by(
        "-ngay_tao"
    )[:5]

    # Phương pháp hiệu quả nhất
    phuong_phap_hieu_qua = (
        PhuongPhapTinhToan.objects.filter(nguoi_tao=request.user, so_lan_su_dung__gt=0)
        .extra(select={"ty_le": "so_lan_dung * 100.0 / so_lan_su_dung"})
        .order_by("-ty_le")[:5]
    )

    # Cảnh báo chưa xử lý
    canh_bao_chua_xu_ly = CanhBaoHieuQua.objects.filter(
        phuong_phap__nguoi_tao=request.user, da_xu_ly=False
    ).count()

    # Lô khung đang hoạt động
    today = timezone.now().date()
    lo_khung_hoat_dong = LoKhung.objects.filter(
        nguoi_tao=request.user,
        ngay_bat_dau__lte=today,
        ngay_ket_thuc__gte=today,
        trang_thai="active",
    ).count()

    context = {
        "tong_phuong_phap": tong_phuong_phap,
        "tong_du_doan": tong_du_doan,
        "tong_lo_khung": tong_lo_khung,
        "du_doan_gan_day": du_doan_gan_day,
        "phuong_phap_hieu_qua": phuong_phap_hieu_qua,
        "canh_bao_chua_xu_ly": canh_bao_chua_xu_ly,
        "lo_khung_hoat_dong": lo_khung_hoat_dong,
    }

    return render(request, "lokhung/dashboard.html", context)


@login_required
def api_phuong_phap_stats(request, pk):
    """API lấy thống kê phương pháp"""
    phuong_phap = get_object_or_404(PhuongPhapTinhToan, pk=pk, nguoi_tao=request.user)

    # Thống kê theo tháng
    thang_gan_day = timezone.now().date() - timedelta(days=30)
    du_doan_thang = DuDoan.objects.filter(
        phuong_phap=phuong_phap, ngay_tao__gte=thang_gan_day
    )

    stats = {
        "ten_phuong_phap": phuong_phap.ten_phuong_phap,
        "ty_le_thanh_cong": phuong_phap.ty_le_thanh_cong,
        "so_lan_su_dung": phuong_phap.so_lan_su_dung,
        "so_lan_dung": phuong_phap.so_lan_dung,
        "trong_so": phuong_phap.trong_so,
        "do_tin_cay": phuong_phap.do_tin_cay,
        "du_doan_thang_qua": {
            "tong": du_doan_thang.count(),
            "dung": du_doan_thang.filter(trang_thai="trung").count(),
            "sai": du_doan_thang.filter(trang_thai="truot").count(),
            "cho_ket_qua": du_doan_thang.filter(trang_thai="cho_ket_qua").count(),
        },
    }

    return JsonResponse(stats)


@login_required
@require_http_methods(["POST"])
def api_check_all_predictions(request):
    """API kiểm tra tất cả dự đoán chưa có kết quả"""
    du_doan_list = DuDoan.objects.filter(
        nguoi_tao=request.user,
        trang_thai="cho_ket_qua",
        ngay_du_doan__lt=timezone.now().date(),
    )

    ket_qua = {"tong_kiem_tra": 0, "trung": 0, "truot": 0, "loi": 0}

    for du_doan in du_doan_list:
        try:
            ket_qua["tong_kiem_tra"] += 1
            if du_doan.kiem_tra_ket_qua():
                ket_qua["trung"] += 1
            else:
                ket_qua["truot"] += 1
        except:
            ket_qua["loi"] += 1

    return JsonResponse(ket_qua)


@login_required
def export_du_doan_excel(request):
    """Xuất dự đoán ra file Excel"""
    import io

    import xlsxwriter
    from django.http import HttpResponse

    # Tạo file Excel trong memory
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet("Dự đoán")

    # Header
    headers = [
        "Ngày dự đoán",
        "Số dự đoán",
        "Loại số",
        "Phương pháp",
        "Điểm tin cậy",
        "Trạng thái",
        "Kết quả thực tế",
        "Ngày tạo",
    ]

    for col, header in enumerate(headers):
        worksheet.write(0, col, header)

    # Dữ liệu
    du_doan_list = (
        DuDoan.objects.filter(nguoi_tao=request.user)
        .select_related("phuong_phap")
        .order_by("-ngay_du_doan")
    )

    for row, du_doan in enumerate(du_doan_list, 1):
        worksheet.write(row, 0, du_doan.ngay_du_doan.strftime("%Y-%m-%d"))
        worksheet.write(row, 1, du_doan.so_du_doan)
        worksheet.write(row, 2, du_doan.get_loai_so_display())
        worksheet.write(row, 3, du_doan.phuong_phap.ten_phuong_phap)
        worksheet.write(row, 4, du_doan.diem_tin_cay)
        worksheet.write(row, 5, du_doan.get_trang_thai_display())
        worksheet.write(row, 6, du_doan.ket_qua_thuc_te or "")
        worksheet.write(row, 7, du_doan.ngay_tao.strftime("%Y-%m-%d %H:%M"))

    workbook.close()
    output.seek(0)

    response = HttpResponse(
        output.read(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = (
        f'attachment; filename="du_doan_{timezone.now().strftime("%Y%m%d")}.xlsx"'
    )

    return response


@login_required
def run_auto_prediction(request, phuong_phap_id):
    """
    View để chạy phương pháp tự động và tạo dự đoán
    """
    phuong_phap = get_object_or_404(
        PhuongPhapTinhToan, pk=phuong_phap_id, nguoi_tao=request.user
    )

    if request.method == "POST":
        analysis_date = request.POST.get("analysis_date")
        prediction_date = request.POST.get("prediction_date")

        try:
            analysis_date = datetime.strptime(analysis_date, "%Y-%m-%d").date()
            prediction_date = datetime.strptime(prediction_date, "%Y-%m-%d").date()

            # Chạy phương pháp
            predictions = method_executor.create_predictions_from_method(
                phuong_phap, analysis_date, prediction_date, request.user
            )

            if predictions:
                messages.success(
                    request,
                    f"Đã tạo thành công {len(predictions)} dự đoán từ phương pháp {phuong_phap.ten_phuong_phap}",
                )
            else:
                messages.warning(request, "Không thể tạo dự đoán từ phương pháp này.")

        except Exception as e:
            messages.error(request, f"Lỗi khi chạy phương pháp: {str(e)}")

    return redirect("lokhung:phuong_phap_detail", pk=phuong_phap_id)

@login_required
def monthly_performance_report(request):
    """Báo cáo hiệu suất phương pháp trong tháng"""
    # Lấy tham số từ request
    year = request.GET.get('year', timezone.now().year)
    month = request.GET.get('month', timezone.now().month)
    
    try:
        year = int(year)
        month = int(month)
    except (ValueError, TypeError):
        year = timezone.now().year
        month = timezone.now().month
    
    # Tính ngày đầu và cuối tháng
    first_day = date(year, month, 1)
    import calendar
    _, last_day_num = calendar.monthrange(year, month)
    last_day = date(year, month, last_day_num)
    
    # Lấy tất cả phương pháp của user
    phuong_phap_list = PhuongPhapTinhToan.objects.filter(nguoi_tao=request.user)
    
    # Dữ liệu tổng hợp cho từng phương pháp
    method_performance_data = []
    daily_data = {}
    
    for phuong_phap in phuong_phap_list:
        # Lấy tất cả dự đoán trong tháng
        du_doan_thang = DuDoan.objects.filter(
            phuong_phap=phuong_phap,
            ngay_du_doan__range=[first_day, last_day]
        ).order_by('ngay_du_doan')
        
        tong_du_doan = du_doan_thang.count()
        du_doan_trung = du_doan_thang.filter(trang_thai='trung').count()
        du_doan_truot = du_doan_thang.filter(trang_thai='truot').count()
        du_doan_cho = du_doan_thang.filter(trang_thai='cho_ket_qua').count()
        
        ty_le_thanh_cong = (du_doan_trung / tong_du_doan * 100) if tong_du_doan > 0 else 0
        
        # Tính điểm hiệu quả trung bình
        diem_hieu_qua_tb = du_doan_thang.aggregate(Avg('diem_tin_cay'))['diem_tin_cay__avg'] or 0
        
        method_data = {
            'phuong_phap': phuong_phap,
            'tong_du_doan': tong_du_doan,
            'du_doan_trung': du_doan_trung,
            'du_doan_truot': du_doan_truot,
            'du_doan_cho': du_doan_cho,
            'ty_le_thanh_cong': round(ty_le_thanh_cong, 2),
            'diem_hieu_qua_tb': round(diem_hieu_qua_tb, 2),
            'du_doan_list': du_doan_thang,
        }
        
        # Tính dữ liệu theo ngày
        daily_stats = {}
        current_date = first_day
        while current_date <= last_day:
            du_doan_ngay = du_doan_thang.filter(ngay_du_doan=current_date)
            daily_stats[current_date.day] = {
                'count': du_doan_ngay.count(),
                'hit': du_doan_ngay.filter(trang_thai='trung').count(),
                'miss': du_doan_ngay.filter(trang_thai='truot').count(),
            }
            current_date += timedelta(days=1)
        
        method_data['daily_stats'] = daily_stats
        method_performance_data.append(method_data)
    
    # Thống kê tổng hợp
    total_predictions = sum(data['tong_du_doan'] for data in method_performance_data)
    total_hits = sum(data['du_doan_trung'] for data in method_performance_data)
    total_misses = sum(data['du_doan_truot'] for data in method_performance_data)
    overall_success_rate = (total_hits / total_predictions * 100) if total_predictions > 0 else 0
    
    # Top performers
    top_methods = sorted(method_performance_data, key=lambda x: x['ty_le_thanh_cong'], reverse=True)[:5]
    
    # Dữ liệu cho biểu đồ
    chart_data = {
        'method_names': [data['phuong_phap'].ten_phuong_phap for data in method_performance_data],
        'success_rates': [data['ty_le_thanh_cong'] for data in method_performance_data],
        'total_predictions': [data['tong_du_doan'] for data in method_performance_data],
        'daily_labels': list(range(1, last_day_num + 1)),
    }
    
    # Lấy danh sách tháng/năm để chọn
    available_months = []
    for i in range(12):
        month_date = timezone.now().date().replace(day=1) - timedelta(days=i*30)
        available_months.append({
            'year': month_date.year,
            'month': month_date.month,
            'name': f"{month_date.strftime('%m/%Y')}"
        })
    
    context = {
        'year': year,
        'month': month,
        'month_name': calendar.month_name[month],
        'first_day': first_day,
        'last_day': last_day,
        'method_performance_data': method_performance_data,
        'total_predictions': total_predictions,
        'total_hits': total_hits,
        'total_misses': total_misses,
        'overall_success_rate': round(overall_success_rate, 2),
        'top_methods': top_methods,
        'chart_data': chart_data,
        'available_months': available_months,
        'current_date': timezone.now().date(),
    }
    
    return render(request, 'lokhung/bao_cao/monthly_performance.html', context)