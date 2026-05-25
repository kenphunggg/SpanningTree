# Spanning Tree Protocol (STP) Simulation in OMNeT++

Dự án này mô phỏng hoạt động của giao thức Spanning Tree Protocol (STP - IEEE 802.1D) sử dụng phần mềm mô phỏng mạng OMNeT++ kết hợp cùng thư viện INET Framework.

## Yêu cầu hệ thống
- Hệ điều hành: Windows, macOS hoặc Linux.
- **OMNeT++**: Phiên bản 6.4.0.
- **INET Framework**: Phiên bản 4.6.

---

## Hướng dẫn Cài đặt & Thiết lập

### Bước 1: Cài đặt OMNeT++ 6.4.0
1. Truy cập trang chủ [OMNeT++ Download](https://omnetpp.org/download/) và tải bản `omnetpp-6.4.0-windows-x86_64.zip` (nếu bạn dùng Windows).
2. Giải nén vào một thư mục dễ nhớ, không có khoảng trắng hoặc ký tự tiếng Việt (Ví dụ: `D:\DownloadD\omnetpp-6.4.0-windows-x86_64\`).
3. Truy cập vào thư mục `omnetpp-6.4.0`, click đúp vào file `mingwenv.cmd` để mở môi trường dòng lệnh (Terminal) của OMNeT++.
4. Chạy lệnh để cấu hình:
   ```bash
   ./configure
   ```
5. Sau khi cấu hình xong, chạy lệnh để biên dịch phần mềm:
   ```bash
   make
   ```
   *(Quá trình này có thể mất từ 10 - 20 phút tùy thuộc vào cấu hình máy).*
6. Sau khi biên dịch xong, gõ lệnh `omnetpp` để khởi động OMNeT++ IDE. 

### Bước 2: Cài đặt thư viện INET 4.6
1. Ngay khi mở OMNeT++ IDE lần đầu, hệ thống thường sẽ hiển thị một hộp thoại gợi ý cài đặt các model mô phỏng. Hãy tick chọn **INET Framework** và tải về.
2. Nếu hộp thoại không tự hiện, trên thanh menu của IDE, chọn **Help** -> **Install Simulation Models...**.
3. Chọn phiên bản **INET 4.6** và nhấn Install để IDE tự tải về.
4. Dự án `inet` hoặc `inet4.6` sẽ xuất hiện trong cửa sổ *Project Explorer* (bên trái IDE).
5. Nhấn chuột phải vào dự án `inet4.6` -> chọn **Build Project** (quá trình này cũng tốn một khoảng thời gian).

### Bước 3: Tải (Clone) và Cài đặt dự án STPSimulation
1. Mở cửa sổ dòng lệnh (hoặc terminal trên IDE) và clone dự án này từ GitHub về máy:
   ```bash
   git clone https://github.com/SangNmd2004/SpanningTree.git STPSimulation
   ```
2. Trên OMNeT++ IDE, chọn **File** -> **Import...**.
3. Mở rộng mục **General** -> chọn **Existing Projects into Workspace** -> nhấn **Next**.
4. Tại mục *Select root directory*, nhấn **Browse** và trỏ tới thư mục `STPSimulation` mà bạn vừa tải về -> nhấn **Finish**.
5. Liên kết dự án với INET: 
   - Nhấn chuột phải vào dự án `STPSimulation` trong *Project Explorer*, chọn **Properties**.
   - Mở mục **Project References**.
   - Đánh dấu tick (✔) vào dự án `inet4.6` (hoặc `inet`) để khai báo sự phụ thuộc. Nhấn **Apply and Close**.
6. Nhấn chuột phải vào dự án `STPSimulation` -> chọn **Build Project** để biên dịch mã nguồn mạng của dự án.

---

## Hướng dẫn Chạy Mô phỏng

1. Trong cửa sổ *Project Explorer*, mở rộng cấu trúc thư mục của dự án: `STPSimulation` -> `simulations`.
2. Tại đây bạn sẽ thấy các file chạy cấu hình như `omnetpp.ini` và file mô tả mạng `scenario.xml`.
3. Nhấn đúp vào file `omnetpp.ini` để xem các kịch bản mô phỏng đã được thiết lập (ví dụ cấu hình băng thông, độ trễ, vị trí đứt liên kết giả lập, v.v).
4. Để bắt đầu chạy:
   - Nhấn chuột phải vào file `omnetpp.ini`.
   - Chọn **Run As** -> **OMNeT++ Simulation**.
5. Cửa sổ đồ họa (Qtenv) sẽ bật lên.
6. Nhấn **Run** (biểu tượng `>`) hoặc **Fast** (biểu tượng `>>`) ở góc trên cùng bên trái để chạy mô phỏng.
7. Quan sát kết quả: Các thiết bị Switch trong mạng sẽ bắt đầu trao đổi gói tin BPDU để bầu chọn Root Bridge, sau đó chuyển trạng thái các cổng mạng thành BLOCKING hoặc FORWARDING để tạo ra mô hình dạng cây, loại bỏ vòng lặp (loop) trong mạng lưới.
