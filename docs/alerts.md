# Template Alert và Runbook

Mỗi alert phải dựa trên triệu chứng người dùng hoặc SLO, không dựa trực tiếp vào tên implementation nội bộ.

## Alert 1

- Tên: `HighLatencyP95`
- Severity: `warning`
- Duration: `5m`
- Kênh thông báo: Slack `#k4-l3b-alerts`
- SLI/SLO liên quan: Latency P95 của `response_sent.latency_ms`
- Điều kiện và thời gian duy trì: `p95(latency_ms) > 3000ms` trong 5 phút
- Ảnh hưởng tới người dùng: Người dùng phải chờ lâu hơn trước khi nhận được câu trả lời, làm giảm khả năng đáp ứng của hệ thống.
- Ba bước kiểm tra đầu tiên:
  1. Mở dashboard latency để xác nhận P95/P99 và xác định khoảng thời gian latency tăng.
  2. Lọc `data/logs.jsonl` trong khoảng thời gian đó và lấy một `correlation_id` có `latency_ms` cao.
  3. Mở trace tương ứng với `correlation_id` trên Langfuse và so sánh các span chính để xác định bước nào bất thường.
- Mitigation tạm thời: Dựa trên evidence thực tế để rollback prompt hoặc cấu hình liên quan; nếu cần, tắt practice scenario hoặc giảm tải khi demo.
- Owner: `student-2A202603017`

## Alert 2

- Tên: `HighErrorRate`
- Severity: `critical`
- Duration: `5m`
- Kênh thông báo: Slack `#k4-l3b-alerts`
- SLI/SLO liên quan: Error rate guardrail, với ngưỡng tối đa `2%`
- Điều kiện và thời gian duy trì: `error_rate > 2%` trong 5 phút
- Ảnh hưởng tới người dùng: Một phần người dùng có thể không nhận được câu trả lời hoặc yêu cầu có thể thất bại, làm giảm độ tin cậy của dịch vụ.
- Ba bước kiểm tra đầu tiên:
  1. Mở dashboard Error Rate để xác nhận tỷ lệ lỗi và xác định thời điểm lỗi bắt đầu tăng.
  2. Lọc `data/logs.jsonl` theo `event == "request_failed"` trong khoảng thời gian đó và kiểm tra `error_type` cùng `correlation_id`.
  3. Mở các trace tương ứng trên Langfuse để xác định lỗi xảy ra ở bước nào và kiểm tra xem lỗi có tập trung vào một loại request hay không.
- Mitigation tạm thời: Dựa trên loại lỗi thực tế để rollback thay đổi gần nhất hoặc khôi phục cấu hình ổn định; giảm tải hoặc tạm dừng practice scenario nếu lỗi tiếp tục tăng.
- Owner: `student-2A202603017`

## Alert 3

- Tên: `LowQualityOrRetrievalSuccess`
- Severity: `warning`
- Duration: `10m`
- Kênh thông báo: Slack `#k4-l3b-alerts`
- SLI/SLO liên quan: Quality score trung bình tối thiểu `0.75` và Retrieval Success Rate tối thiểu `90%`
- Điều kiện và thời gian duy trì: `quality_score_avg < 0.75` hoặc `retrieval_success_rate < 90%` trong 10 phút
- Ảnh hưởng tới người dùng: Người dùng có thể nhận được câu trả lời có chất lượng thấp hoặc câu trả lời thiếu thông tin do quá trình retrieval không thành công.
- Ba bước kiểm tra đầu tiên:
  1. Mở dashboard Quality và Retrieval Success để xác định metric nào vượt ngưỡng và khoảng thời gian xảy ra vấn đề.
  2. Lọc `data/logs.jsonl` trong khoảng thời gian đó và kiểm tra `quality_score`, `tool_success`, `event` và `correlation_id`.
  3. Mở các trace tương ứng trên Langfuse để kiểm tra các bước retrieval và nội dung đầu vào/đầu ra, đồng thời xác định xem lỗi có tập trung ở một nhóm request hay không.
- Mitigation tạm thời: Nếu retrieval success giảm, khôi phục cấu hình retrieval gần nhất đã biết là ổn định hoặc tạm thời giảm phạm vi practice scenario. Nếu quality score giảm, kiểm tra và rollback thay đổi prompt/configuration khi evidence cho thấy thay đổi đó liên quan.
- Owner: `student-2A202603017`
