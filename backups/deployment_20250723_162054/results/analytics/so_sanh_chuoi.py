# Hai chuỗi đầu vào
str1 = " '72', '30', '58', '94', '64', '57', '45', '68', '69', '81', '11', '12', '15', '09', '10', '08', '17', '99', '54', '50'"
str2 = " 64 31 30 45 72 69 58 68 81 57"

# # Tách các số thành danh sách và chuyển thành tập hợp
set1 = set(str1.split())
set2 = set(str2.split())

# Tìm các số khác nhau
only_in_str1 = set1 - set2  # Số chỉ có trong str1
only_in_str2 = set2 - set1  # Số chỉ có trong str2
common_numbers = set1 & set2  # Số có trong cả set1 và set2
# In kết quả
print("Số chỉ có trong str1:", sorted(only_in_str1))
print("Số chỉ có trong str2:", sorted(only_in_str2))
print("Tất cả số khác nhau:", sorted(only_in_str1 | only_in_str2))
print("Số có trong cả set1 và set2:", sorted(common_numbers))