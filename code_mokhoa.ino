#include <ESP8266WiFi.h>           // Thư viện kết nối WiFi cho ESP8266
#include <ESP8266WebServer.h>      // Thư viện tạo Web Server nội bộ

// ==== Thông tin WiFi cần kết nối ====
const char* ssid = "giamy";         // Tên WiFi
const char* password = "21122009";  // Mật khẩu WiFi

// ==== Chân điều khiển relay (nối với khoá điện) ====
#define relayPin 12  // GPIO12 tương ứng chân D6 trên NodeMCU


// ==== Biến trạng thái mở khóa ====
bool unlocking = false;                  // Biến cờ đánh dấu đang mở khóa
unsigned long unlockStartTime = 0;       // Thời gian bắt đầu mở khóa
const unsigned long unlockDuration = 5000; // Thời gian mở khóa là 5 giây

// ==== Hàm xử lý khi nhận yêu cầu mở khoá (/unlock) ====
void handleUnlock() {
  Serial.println("[INFO] Nhận lệnh mở khoá!");

  digitalWrite(relayPin, HIGH);       // Bật relay (mức HIGH → mở khoá)
  unlocking = true;                   // Đánh dấu trạng thái đang mở khoá
  unlockStartTime = millis();         // Ghi lại thời điểm bắt đầu mở

  Serial.println("[INFO] Relay ON");

  // Phản hồi lại cho client khi nhận yêu cầu mở khóa thành công
  server.send(200, "text/plain", "Unlock successful!!");
}

// ==== Hàm thiết lập ban đầu (chạy 1 lần khi khởi động ESP) ====
void setup() {
  Serial.begin(115200);               // Khởi động Serial Monitor ở baudrate 115200
  delay(100);

  Serial.println();
  Serial.println("[INFO] Đang kết nối WiFi...");
  WiFi.begin(ssid, password);         // Kết nối tới WiFi với SSID và Password

  // Chờ kết nối WiFi (tối đa 20 giây)
  int retry = 0;
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
    if (++retry > 40) {
      Serial.println("\n[ERROR] Không kết nối WiFi sau 20s. Kiểm tra SSID/PASSWORD.");
      return;
    }
  }

  Serial.println("\n[INFO] Đã kết nối WiFi!");
  Serial.print("[INFO] IP Address: ");
  Serial.println(WiFi.localIP());     // In ra địa chỉ IP để truy cập server

  // Cấu hình chân relay là OUTPUT và tắt relay ban đầu
  pinMode(relayPin, OUTPUT);
  digitalWrite(relayPin, LOW);        // Tắt relay (mức LOW)

  server.on("/unlock", HTTP_GET, handleUnlock);  // Đường dẫn để điều khiển mở khóa

  server.begin();                     // Bắt đầu chạy Web Server
  Serial.println("[INFO] Web server đã khởi động!");
}

// ==== Vòng lặp chính (chạy liên tục) ====
void loop() {
  server.handleClient();              // Lắng nghe và xử lý các yêu cầu HTTP

  // Kiểm tra nếu đang mở khóa và đã hết thời gian mở (5 giây)
  if (unlocking && millis() - unlockStartTime >= unlockDuration) {
    digitalWrite(relayPin, LOW);      // Tắt relay (đóng khoá lại)
    unlocking = false;                // Cập nhật lại trạng thái
    Serial.println("[INFO] Relay OFF sau 5 giây.");
  }
}
