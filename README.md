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

---

## Thu thập thời gian phản hồi của từng gói tin

Trong dự án này, thời gian phản hồi được đo bằng **RTT (Round-Trip Time)** của gói Ping:

```text
host1 gửi Ping Request → host2 nhận và trả Ping Reply → host1 nhận Reply
```

RTT bao gồm thời gian truyền theo cả hai chiều. Đây không phải là độ trễ một chiều.

### 1. Dữ liệu được ghi lại

File `simulations/omnetpp.ini` đã được cấu hình để chỉ ghi ba vector cần thiết:

```ini
*.host1.app[0].rtt:vector.vector-recording = true
*.host1.app[0].pingTxSeq:vector.vector-recording = true
*.host1.app[0].pingRxSeq:vector.vector-recording = true
**.vector-recording = false
```

Ý nghĩa của các vector:

- `pingTxSeq`: số thứ tự và thời điểm gửi của tất cả Ping Request.
- `pingRxSeq`: số thứ tự và thời điểm nhận Ping Reply.
- `rtt`: RTT của các gói nhận phản hồi thành công.

Việc kết hợp cả ba vector cho phép xác định thời gian phản hồi của từng gói và phát hiện các gói không nhận được phản hồi.

### 2. Chạy mô phỏng

1. Mở `simulations/omnetpp.ini` trong OMNeT++ IDE.
2. Chọn cấu hình cần chạy, ví dụ:
   - `General`
   - `KichBan1_DutCap`
   - `Kich_Ban_Sap_Root`
3. Chạy mô phỏng và đợi mô phỏng kết thúc.
4. Các file kết quả `.vec`, `.vci` và `.sca` sẽ được tạo trong thư mục `simulations/results`.

> **Lưu ý:** Nếu dừng mô phỏng ngay sau khi một gói vừa được gửi, script sẽ xem gói chưa kịp nhận phản hồi đó là `LOST`. Khi thay đổi thời gian mô phỏng, nên đặt `stopTime` của `PingApp` nhỏ hơn `sim-time-limit` để chừa thời gian cho phản hồi cuối cùng. Ví dụ:
>
> ```ini
> sim-time-limit = 200s
> *.host1.app[0].stopTime = 199s
> ```

#### Chạy nhiều kịch bản khác nhau

Mỗi cấu hình `[Config ...]` có một tên riêng, vì vậy OMNeT++ sẽ tạo bộ file kết quả riêng cho từng kịch bản. Ví dụ, sau khi chạy hai cấu hình:

```ini
[Config KichBan1_DutCap]
[Config Kich_Ban_Sap_Root]
```

thư mục `simulations/results` có thể chứa:

```text
KichBan1_DutCap-#0.vec
KichBan1_DutCap-#0.vci
KichBan1_DutCap-#0.sca
Kich_Ban_Sap_Root-#0.vec
Kich_Ban_Sap_Root-#0.vci
Kich_Ban_Sap_Root-#0.sca
```

Hai kịch bản có tên config khác nhau nên không ghi đè kết quả của nhau. Tuy nhiên, nếu chạy lại cùng một config và cùng số lần lặp `#0`, OMNeT++ sẽ ghi đè file cũ của config đó.

Nếu cần chạy lặp lại một kịch bản nhiều lần, có thể thêm:

```ini
repeat = 2
seed-set = ${repetition}
```

Khi đó OMNeT++ tạo các file như:

```text
KichBan1_DutCap-#0.vec
KichBan1_DutCap-#1.vec
```

`#0`, `#1`, ... là số lần lặp của cấu hình, không phải bộ đếm số lần nhấn nút **Run**.

### 3. Xuất kết quả sang CSV

Script `scripts/export_response_times.py` sử dụng thư viện chuẩn của Python, không cần cài thêm package.

Từ thư mục gốc của dự án, chạy:

**Windows:**

```powershell
py scripts\export_response_times.py
```

**Linux hoặc macOS:**

```bash
python3 scripts/export_response_times.py
```

Theo mặc định, script sẽ:

- Đọc tất cả file `simulations/results/*.vec`.
- Ghép các vector theo số thứ tự gói Ping.
- Tạo file `simulations/results/response-times.csv`.
- Ghi một dòng cho mỗi Ping Request, kể cả gói bị mất.
- Gộp kết quả của tất cả kịch bản và tất cả lần lặp đang có trong thư mục `results`.

Script **không append mù** vào CSV cũ. Mỗi lần chạy, nó tạo lại `response-times.csv` từ toàn bộ file `.vec` hiện có. Vì vậy:

- Không tạo dòng trùng khi chạy lại script nhiều lần.
- File `.vec` nào còn trong `simulations/results` thì kết quả của file đó sẽ có trong CSV.
- Nếu một file `.vec` bị OMNeT++ ghi đè, CSV lần sau chỉ chứa dữ liệu mới của file đó.
- Các kịch bản được phân biệt bằng các cột `config`, `run` và `source_file`.

Ví dụ thông báo thành công:

```text
Wrote 5 packet rows from 1 vector file(s) to simulations/results/response-times.csv (4 received, 0 received without RTT, 1 lost).
```

Nếu thư mục chứa hai file:

```text
KichBan1_DutCap-#0.vec
Kich_Ban_Sap_Root-#0.vec
```

thì cùng một file `response-times.csv` sẽ chứa các dòng của cả hai kịch bản, ví dụ:

```csv
config,source_file,sequence,response_time_ms,status
KichBan1_DutCap,KichBan1_DutCap-#0.vec,0,0.8704,RECEIVED
KichBan1_DutCap,KichBan1_DutCap-#0.vec,1,,LOST
Kich_Ban_Sap_Root,Kich_Ban_Sap_Root-#0.vec,0,1.71648,RECEIVED
```

Để chỉ xử lý một file kết quả và chọn tên file CSV:

```powershell
py scripts\export_response_times.py "simulations/results/General-#0.vec" -o "simulations/results/general-response-times.csv"
```

### 4. Cấu trúc file CSV

| Cột | Ý nghĩa |
| --- | --- |
| `run` | Định danh đầy đủ của lần chạy mô phỏng |
| `config` | Tên cấu hình OMNeT++ |
| `network` | Tên topology NED được sử dụng |
| `lambda_pps` | Giá trị lambda được đọc từ biến lặp `${lambda=...}`; để trống nếu run không có metadata này |
| `repetition` | Số lần lặp của config |
| `source_file` | File `.vec` chứa dữ liệu nguồn |
| `module` | Module `PingApp` thực hiện phép đo |
| `destination` | Host đích |
| `sequence` | Số thứ tự của gói Ping |
| `send_time_s` | Thời điểm gửi Request, đơn vị giây mô phỏng |
| `receive_time_s` | Thời điểm nhận Reply, đơn vị giây mô phỏng |
| `response_time_s` | RTT tính bằng giây |
| `response_time_ms` | RTT tính bằng mili giây |
| `status` | Trạng thái của gói |

Các trạng thái có thể xuất hiện:

- `RECEIVED`: nhận được phản hồi và tính được RTT.
- `LOST`: không nhận được phản hồi.
- `RECEIVED_NO_RTT`: nhận được phản hồi nhưng INET không còn đủ dữ liệu để tính RTT. Trạng thái này hiếm khi xuất hiện.

Các trường thời gian phản hồi của gói `LOST` được để trống.

---

## Ma trận 4 phép so sánh đã chuẩn bị

Tám config dưới đây đã được khai báo trong `simulations/omnetpp.ini`. Mỗi cặp config tạo thành một phép so sánh.

`lambda1` và `lambda2` biểu diễn hai profile tải cần so sánh. Để kết quả có ý nghĩa, mỗi profile phải giữ nguyên cách phát gói, kích thước gói và các tham số traffic khác trong tất cả config sử dụng profile đó.

### So sánh 1: Lambda khi đứt cáp

| Config | Lambda | Topology | Sự cố |
| --- | ---: | --- | --- |
| `SoSanh1_DutCap_Lambda1` | `lambda1` | Hiện tại | Đứt cáp |
| `SoSanh1_DutCap_Lambda2` | `lambda2` | Hiện tại | Đứt cáp |

### So sánh 2: Lambda khi Root Bridge sập

| Config | Lambda | Topology | Sự cố |
| --- | ---: | --- | --- |
| `SoSanh2_SapRoot_Lambda1` | `lambda1` | Hiện tại | Sập root |
| `SoSanh2_SapRoot_Lambda2` | `lambda2` | Hiện tại | Sập root |

### So sánh 3: Độ phức tạp topology khi đứt cáp

| Config | Lambda | Topology | Sự cố |
| --- | ---: | --- | --- |
| `SoSanh3_DutCap_TopoHienTai` | `lambda1` | 4 switch, 4 link | Đứt cáp |
| `SoSanh3_DutCap_TopoPhucTap` | `lambda1` | 8 switch, 9 link | Đứt cáp |

### So sánh 4: Độ phức tạp topology khi Root Bridge sập

| Config | Lambda | Topology | Sự cố |
| --- | ---: | --- | --- |
| `SoSanh4_SapRoot_TopoHienTai` | `lambda1` | 4 switch, 4 link | Sập root |
| `SoSanh4_SapRoot_TopoPhucTap` | `lambda1` | 8 switch, 9 link | Sập root |

Hai config trong so sánh 3 phải dùng cùng profile `lambda1`; tương tự, hai config trong so sánh 4 cũng phải dùng cùng profile `lambda1`. Nếu đồng thời thay đổi cả topology lẫn traffic, kết quả không thể hiện riêng ảnh hưởng của độ phức tạp topology.

### Thiết kế topology để so sánh công bằng

- Topology hiện tại: 4 switch và 4 liên kết liên-switch, tạo một vòng.
- Topology phức tạp: 8 switch và 9 liên kết liên-switch, tạo hai vòng và có đường kính miền STP lớn hơn.
- `host1` vẫn nối vào `sw1`; `host2` vẫn nối vào `sw3`.
- Khoảng cách vật lý ngắn nhất từ `sw1` đến `sw3` vẫn là 2 hop ở cả hai topology.
- Sau khi liên kết `sw1-sw2` đứt hoặc `sw2` sập, vẫn có đường `sw1-sw4-sw3` dài 2 hop.

Thiết kế này hạn chế việc RTT thay đổi chỉ vì hai host bị đặt xa nhau hơn. Khác biệt quan sát được sẽ phản ánh rõ hơn ảnh hưởng của số bridge, số vòng dự phòng và quá trình STP hội tụ lại.

Trong nhóm thí nghiệm, `sw2` được ép làm Root Bridge. `sw2` không nối trực tiếp với host nào, vì vậy khi root sập, hai host không bị cô lập vật lý và mạng có thể bầu root mới.

### Mốc thời gian của sự cố

- Sự cố xảy ra tại `100s`.
- Với kịch bản đứt cáp, cáp được khôi phục tại `160s`.
- Với kịch bản sập root, `sw2` giữ trạng thái hỏng đến hết mô phỏng.
- Mô phỏng kết thúc tại `220s`.

Traffic nên bắt đầu sau khi STP đã hội tụ và dừng trước `220s` để gói cuối còn đủ thời gian nhận phản hồi. Cùng một phép so sánh phải sử dụng chung thời điểm bắt đầu, thời điểm kết thúc và seed policy.

Root không được khởi động lại vì thao tác `startup` switch trong topology này yêu cầu lifecycle hook của `L2NetworkConfigurator` mà mô hình hiện tại không sử dụng. Việc giữ root ở trạng thái hỏng cũng giúp đo trực tiếp quá trình bầu root mới và trạng thái ổn định sau hội tụ.

### Chạy ma trận thí nghiệm

Trong OMNeT++ IDE, chạy lần lượt tám config ở bảng trên. Mỗi config tạo file `.vec` riêng trong `simulations/results`.

Tên file thông thường có dạng:

```text
SoSanh1_DutCap_Lambda1-#0.vec
SoSanh1_DutCap_Lambda2-#0.vec
```

Khi lambda được khai báo bằng biến lặp `${lambda=...}`, OMNeT++ tự thêm giá trị đó vào tên file và exporter ghi nó vào cột `lambda_pps`.

Với traffic ngẫu nhiên, nên tăng số lần lặp trong `[Config ExperimentBase]`:

```ini
repeat = 5
seed-set = ${repetition}
```

Mỗi config khi đó được chạy năm lần với seed khác nhau. Script vẽ sẽ gộp dữ liệu của toàn bộ các lần lặp theo cửa sổ thời gian.

Sau khi chạy xong các config, tạo lại CSV:

```powershell
py scripts\export_response_times.py
```

---

## Vẽ biểu đồ thời gian phản hồi

Script `scripts/plot_experiment_comparisons.py` tự động tạo bốn biểu đồ so sánh.

Cài đặt thư viện một lần:

```powershell
py -m pip install pandas matplotlib
```

Sau khi đã tạo `response-times.csv`, chạy:

```powershell
py scripts\plot_experiment_comparisons.py
```

Kết quả được lưu trong `simulations/results/plots`:

```text
01_dutcap_lambda.png
02_saproot_lambda.png
03_dutcap_topology.png
04_saproot_topology.png
experiment-summary.csv
```

Mỗi ảnh có hai phần:

- Biểu đồ trên: RTT trung vị trong từng cửa sổ 2 giây; vùng màu quanh đường là khoảng tứ phân vị 25%–75%.
- Biểu đồ dưới: tỷ lệ gói `LOST` trong từng cửa sổ 2 giây.
- Trục thời gian mặc định bắt đầu tại `100s`, đúng lúc sự cố xảy ra, để làm nổi bật quá trình hội tụ lại và ảnh hưởng sau sự cố.
- Vạch đỏ tại `100s`: thời điểm gây sự cố.
- Vạch xanh tại `160s`: thời điểm nối lại cáp, chỉ có trong kịch bản đứt cáp.

Phần dữ liệu trước `100s` không xuất hiện trên PNG nhưng vẫn được giữ trong `response-times.csv` và `experiment-summary.csv`. Bảng tổng hợp tiếp tục chứa số liệu trước sự cố để dùng làm baseline khi tính mức thay đổi.

### Vì sao biểu đồ chỉ tập trung từ thời điểm sự cố?

Trước `100s`, mạng đang ở trạng thái ổn định nên RTT thường ít biến động. Nếu vẽ toàn bộ giai đoạn này, đoạn ổn định chiếm nhiều diện tích và làm các thay đổi quan trọng sau sự cố khó quan sát hơn.

Việc bắt đầu trục X tại `100s` giúp làm rõ:

- Khoảng thời gian mất gói ngay sau khi topology thay đổi.
- Mức tăng RTT trong lúc STP hội tụ lại.
- Thời điểm mạng bắt đầu chuyển tiếp ổn định trở lại.
- Khác biệt giữa hai profile lambda hoặc hai mức độ phức tạp topology.
- Ảnh hưởng của việc khôi phục cáp tại `160s`.

Dữ liệu trước sự cố vẫn cần được thu thập để xác định trạng thái bình thường của mạng. Phần này được giữ trong CSV và bảng tổng hợp, nhưng không chiếm không gian trên biểu đồ chính.

Có thể thay độ rộng cửa sổ thời gian, ví dụ 5 giây:

```powershell
py scripts\plot_experiment_comparisons.py --bin-width 5
```

Nếu cần xem lại cả giai đoạn trước sự cố, truyền thời điểm bắt đầu:

```powershell
py scripts\plot_experiment_comparisons.py --start-time 40
```

Để vừa lưu vừa hiển thị biểu đồ:

```powershell
py scripts\plot_experiment_comparisons.py --show
```

Script nhận diện config bằng tên đã liệt kê trong ma trận. Khi cột `lambda_pps` chưa có giá trị, biểu đồ dùng nhãn `λ1` và `λ2`. Khi lambda được ghi bằng biến lặp `${lambda=...}`, script tự dùng giá trị thật làm nhãn.

> Thư mục `simulations/results` được khai báo trong `.gitignore`, vì vậy các file kết quả và biểu đồ sinh ra sẽ không được đưa lên Git.
