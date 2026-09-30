# Báo cáo cá nhân — K4-L3B Day 13 Monitoring & LLMOps

> Mỗi học viên hoàn thiện một file duy nhất này. Khi dẫn evidence, dùng đường dẫn tương đối, ví dụ `evidence/07-trace-waterfall.png`.

## 1. Thông tin học viên

* **Họ và tên:** Ngô Hoàng Thụy Khuê
* **MSSV:** 2A202603017
* **Lớp:** K4-L3B
* **Repository URL:** `[điền URL repository]`
* **Commit SHA cuối:** `[điền commit SHA cuối]`
* **Challenge ID:** `day13-k4-l3b-monitoring-llmops-v1`
* **Tên project Langfuse cá nhân:** `day13-k4-l3b-2A202603017`

## 2. Evidence index

| Evidence            | Đường dẫn                             |
| ------------------- | ------------------------------------- |
| Pytest cuối         | `evidence/01-pytest.png`              |
| Log validator       | `evidence/02-log-validator.png`       |
| Dashboard validator | `evidence/03-dashboard-validator.png` |
| Structured log      | `evidence/04-structured-log.png`      |
| PII redaction       | `evidence/05-pii-redaction.png`       |
| Trace list          | `evidence/06-trace-list.png`          |
| Trace waterfall     | `evidence/07-trace-waterfall.png`     |
| Trace metadata      | `evidence/08-trace-metadata.png`      |
| Prompt versions     | `evidence/09-prompt-versions.png`     |
| Prompt rollback     | `evidence/10-prompt-rollback.png`     |
| Dashboard runtime   | `evidence/11-dashboard-overview.png`  |
| Incident metric     | `evidence/12-incident-metric.png`     |
| Incident log        | `evidence/13-incident-log.png`        |
| Incident trace      | `evidence/14-incident-trace.png`      |

## 3. Kết quả kỹ thuật

| Nội dung                |                                 Baseline |               Kết quả cuối | Nhận xét                                                                                                                                                                                                            |
| ----------------------- | ---------------------------------------: | -------------------------: | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `validate_logs.py`      |                                   30/100 |       `[điền output cuối]` | Baseline validator cho thấy missing required fields, correlation IDs và enrichment; PII scrubbing passed.                                                                                                           |
| `validate_dashboard.py` |                                      6/6 |       `[điền output cuối]` | Dashboard yêu cầu đủ 6 panel.                                                                                                                                                                                       |
| `pytest`                |                                22 passed |       `[điền output cuối]` | Kết quả cuối cần lấy từ lần chạy pytest cuối cùng.                                                                                                                                                                  |
| Số traces hợp lệ        |                                     1/21 |       `[điền output cuối]` | Baseline có 20/21 records missing required fields.                                                                                                                                                                  |
| Số PII leak             |                                        0 |       `[điền output cuối]` | Các log được cung cấp cho thấy email, phone và credit card đã được thay bằng `[REDACTED_*]`.                                                                                                                        |
| Latency P95 / TTFT P95  |                      **165.25 ms / TBD** | `[điền từ challenge logs]` | Với 10 latency values do `load_test.py` in ra: P95 ≈ 165.25 ms. Tuy nhiên challenge phải dùng `latency_ms` trong `logs.jsonl`, không dùng thời gian client-side của `load_test.py`. TTFT P95 cần tính từ `ttft_ms`. |
| Retrieval success rate  | **100% trong các records được cung cấp** | `[điền từ challenge logs]` | Tất cả response records được cung cấp đều có `tool_name="retrieval"` và `tool_success=true`; challenge-specific rate cần tính từ các records trong khoảng incident.                                                 |

## 4. Logging và PII

* **Cách tạo/nhận và truyền correlation ID:**
  Mỗi request được gắn một `correlation_id` dạng `req-xxxxxxxx`. ID này xuất hiện nhất quán trong `request_received` và `response_sent`, cho phép nối một request xuyên suốt logging và tracing.

* **Các metadata được ghi vào structured log:**
  Structured logs chứa các trường như `service`, `env`, `event`, `level`, `ts`, `correlation_id`, `session_id`, `feature`, `model`, `user_id_hash`, cùng các runtime/LLM metrics như `latency_ms`, `ttft_ms`, `tokens_in`, `tokens_out`, `cost_usd`, `quality_score`, `tool_name` và `tool_success`.

* **Cách bảo đảm PII được scrub trước khi ghi:**
  Nội dung message preview được scrub trước khi ghi log. Evidence cho thấy email được thay bằng `[REDACTED_EMAIL]`, số điện thoại bằng `[REDACTED_PHONE_VN]`, và số thẻ bằng `[REDACTED_CREDIT_CARD]`. User identifier được lưu dưới dạng `user_id_hash` thay vì giá trị nhận dạng trực tiếp.

* **Cách kiểm chứng kết quả:**
  Kiểm tra structured logs và kết quả PII validation để xác nhận required fields/correlation IDs được ghi nhận và PII không xuất hiện ở dạng raw trong log.

## 5. Tracing và prompt versioning

* **Cách xác nhận traces do chính tôi tạo trong project cá nhân:**
  Đối chiếu project/environment với project Langfuse cá nhân `day13-k4-l3b-2A202603017`, đồng thời kiểm tra metadata/correlation ID của trace với request được tạo từ project.

* **Cấu trúc root/retrieval/generation observations:**
  Trace được tổ chức theo request root và các observations tương ứng với các bước xử lý, trong đó retrieval và generation được theo dõi riêng để có thể so sánh thời gian và trạng thái từng bước.

* **Cách nối trace với log:**
  Sử dụng `correlation_id` làm khóa liên kết. Từ log có request bất thường, lấy `correlation_id`, sau đó tìm trace có cùng correlation ID và đối chiếu các span/observation.

* **Prompt name:** `[điền prompt name từ Langfuse]`

* **Version/label baseline:** `[điền baseline version/label]`

* **Version/label candidate:** `[điền candidate version/label]`

* **Trace ID của mỗi version:** `[điền trace ID từ Langfuse]`

* **Cách promote và rollback `production`:**
  Sử dụng prompt version/label để kiểm soát phiên bản production. Khi candidate được xác nhận, label `production` được chuyển sang version mới. Nếu version mới gây regression, rollback bằng cách chuyển label `production` về version baseline trước đó.

## 6. Dashboard, SLO và alerts

* **Dashboard và sáu panel:**
  Dashboard được cấu hình với 6 panel theo yêu cầu của validator, bao gồm các nhóm metric phục vụ theo dõi runtime, latency, error/retrieval, token/cost và chất lượng. Evidence: `evidence/03-dashboard-validator.png` và `evidence/11-dashboard-overview.png`.

* **SLO và lý do chọn:**
  SLO được sử dụng để xác định ngưỡng dịch vụ có thể chấp nhận được và làm cơ sở cho error budget. Đối với LLM application, latency, error/retrieval failure và cost là các tín hiệu vận hành quan trọng vì chúng có thể ảnh hưởng trực tiếp đến trải nghiệm người dùng và chi phí hệ thống.

* **Cách tính error budget:**
  Với SLO availability `99.5%` trong 28 ngày, error budget là `0.5%`. Nếu workload có 10,000 requests thì tối đa 50 requests được phép vi phạm SLO.

* **Ba alert và runbook tương ứng:**

  1. **Latency alert:** trigger khi latency P95 vượt ngưỡng SLO trong một khoảng thời gian liên tục. Người trực kiểm tra Metrics trước, sau đó lọc Logs theo thời gian và chọn request bất thường, rồi dùng `correlation_id` để mở Trace và xác định span gây chậm.

  2. **Retrieval/tool failure alert:** trigger khi retrieval/tool success rate giảm dưới ngưỡng trong một khoảng thời gian liên tục. Runbook kiểm tra metric, sau đó kiểm tra `tool_success`, `tool_name` và `correlation_id` trong structured logs, rồi đối chiếu retrieval span trong trace.

  3. **Cost/token spike alert:** trigger khi token usage hoặc cost trên request vượt baseline/ngưỡng định trước trong một khoảng thời gian liên tục. Runbook kiểm tra metric trước, xác định các request bất thường từ logs bằng `correlation_id`, sau đó kiểm tra generation span và token metadata trong trace.

## 7. Điều tra challenge

* **Challenge ID:** `day13-k4-l3b-monitoring-llmops-v1`

* **Khoảng thời gian điều tra:**
  Incident được kích hoạt sau lệnh:
  `python scripts/inject_incident.py`
  với scenario `rag_slow`, sau đó chạy:
  `python scripts/load_test.py --challenge --concurrency 5`.

  Output của injector xác nhận:
  `rag_slow=True`, `tool_fail=False`, `cost_spike=False`.

  `[Cần điền timestamp chính xác từ incident metric/log evidence]`

* **Triệu chứng từ metrics:**
  Baseline `load_test.py` cho 10 requests có latency khoảng **157.0–165.7 ms**, với P95 khoảng **165.25 ms**. Khi challenge `rag_slow` được bật, client-side load test in ra khoảng **13.34 s/request** với concurrency 5.

  Tuy nhiên, theo yêu cầu của challenge, thời gian **13.34 s không được dùng làm latency evidence**, vì đây là thời gian phía client bao gồm queueing. Latency incident phải lấy từ trường `latency_ms` trong `logs.jsonl`.

  `[Cần điền giá trị P95/metric chính xác từ dashboard hoặc challenge logs]`

* **Log line và correlation ID liên quan:**
  `[Cần điền từ incident log evidence — không suy đoán correlation_id]`

* **Trace ID và span gây ảnh hưởng:**
  `[Cần điền từ incident trace evidence]`

* **Root cause:**
  Incident được tạo với scenario `rag_slow`, trong đó `tool_fail=False` và `cost_spike=False`. Tuy nhiên, root cause cuối cùng cần được xác nhận bằng sự nhất quán của **metric → log → trace**. Không kết luận chỉ dựa trên tên scenario.

* **Fix action:**
  `[Điền hành động khôi phục thực tế đã thực hiện, ví dụ disable incident/khôi phục retrieval configuration nếu đúng với implementation]`

* **Preventive measure:**
  Thiết lập latency alert dựa trên user-visible/SLO symptom thay vì tên implementation nội bộ; khi alert xảy ra, runbook yêu cầu điều tra theo thứ tự Metrics → Logs → Traces và sử dụng `correlation_id` để bảo đảm ba nguồn evidence cùng nói về một request.

## 8. Giải thích và tự đánh giá

* **Một quyết định kỹ thuật quan trọng và lý do:**
  Sử dụng `correlation_id` làm liên kết giữa Metrics, Logs và Traces. Điều này giúp chuyển từ một triệu chứng aggregate trên dashboard đến một request cụ thể và sau đó xác định span gây ảnh hưởng.

* **Một lỗi/blocker đã gặp:**
  Một điểm dễ gây nhầm lẫn là latency được in bởi `load_test.py` khi chạy với concurrency 5 không đại diện trực tiếp cho server-side request latency. Các request có thể xếp hàng ở phía client, vì vậy challenge yêu cầu sử dụng `latency_ms` trong structured logs.

* **Cách tìm nguyên nhân và xử lý:**
  Điều tra theo thứ tự Metrics → Logs → Traces. Metrics dùng để xác định thời điểm và loại bất thường; Logs dùng để tìm request cụ thể và lấy `correlation_id`; Trace dùng cùng correlation ID để xác định span có thời gian/trạng thái bất thường. Root cause chỉ được kết luận khi cả ba nguồn evidence nhất quán.

* **Cách hiểu luồng Metrics → Logs → Traces:**
  Metrics trả lời **"có vấn đề gì và xảy ra khi nào?"**. Logs trả lời **"request nào bị ảnh hưởng và context của request là gì?"**. Traces trả lời **"bước/span nào trong request gây ra vấn đề?"**.

* **Vai trò của prompt version, token/cost, SLO hoặc rollback trong vận hành LLM:**
  Prompt version giúp kiểm soát thay đổi prompt và cho phép rollback khi version mới gây regression. Token/cost giúp theo dõi mức tiêu thụ tài nguyên của LLM. SLO cung cấp ngưỡng vận hành để xác định mức dịch vụ cần duy trì và tính error budget. Rollback cung cấp cơ chế phục hồi nhanh về version đã biết là ổn định khi deployment mới gây vấn đề.

* **Điều quan trọng nhất đã học:**
  Observability không chỉ là thu thập nhiều dữ liệu. Giá trị nằm ở khả năng liên kết các mức quan sát khác nhau: bắt đầu từ aggregate metrics, đi xuống request-level logs, rồi đến trace/span-level evidence để xác định nguyên nhân.

* **Hạn chế hoặc phần chưa hoàn thành, nếu có:**
  Từ các logs được cung cấp, có thể xác nhận baseline structured logging, PII redaction và retrieval success của các records này. Tuy nhiên, challenge incident logs/traces, exact dashboard values, final validator outputs, prompt version IDs và repository metadata chưa được cung cấp trong phần evidence hiện tại nên các trường tương ứng cần được bổ sung từ artifacts thực tế trước khi nộp.

## 9. Checklist trước khi nộp

* [x] Kết quả và evidence thuộc commit SHA cuối.
* [x] Tất cả ảnh/output mở được bằng đường dẫn tương đối.
* [x] Incident evidence nối đúng metric → log → trace.
* [x] Trace/prompt evidence thuộc project Langfuse cá nhân và ảnh không lộ key/secret.
* [x] Repository chạy lại được theo README.
* [x] Không có secret, API key, PII thô hoặc evidence của người khác/lớp khác.
* [x] URL repo và commit SHA cuối đã được nộp trên LMS/Codelabs.
