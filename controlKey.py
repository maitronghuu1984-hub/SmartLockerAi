import cv2                          # Thư viện xử lý ảnh và video
import face_recognition             # Thư viện nhận dạng khuôn mặt
import requests                     # Gửi yêu cầu HTTP đến ESP8266
import time                         # Xử lý thời gian
import os                           # Dùng để phát âm thanh (macOS: dùng afplay)

# ==== Tải ảnh khuôn mặt đã lưu (ảnh mẫu) để nhận diện ====
known_face_path = "saved_face.jpg"
known_image = face_recognition.load_image_file(known_face_path)
known_face_encodings = face_recognition.face_encodings(known_image)

# Nếu không tìm thấy khuôn mặt trong ảnh mẫu → dừng chương trình
if not known_face_encodings:
    raise Exception("[ERROR] Không tìm thấy khuôn mặt trong ảnh mẫu!")

# Lưu encoding (đặc trưng khuôn mặt) đầu tiên để so sánh
known_face_encoding = known_face_encodings[0]
known_face_encodings = [known_face_encoding]
known_face_names = ["OK! Good!"]    # Tên hiển thị nếu nhận diện đúng

# Mở camera (camera mặc định)
video_capture = cv2.VideoCapture(0)

# ==== Biến điều khiển nhận diện liên tục ====
start_detect_time = None                     # Lưu thời điểm bắt đầu phát hiện đúng
UNLOCK_TRIGGER_DURATION = 3                  # Cần nhận diện đúng liên tục 3 giây để mở khóa
unlock_sent = False                          # Biến đánh dấu đã gửi lệnh mở khoá hay chưa

print("[INFO] Bắt đầu quét camera. Nhấn 'q' để thoát.")

# ==== Vòng lặp chính: xử lý khung hình từ camera ====
while True:
    ret, frame = video_capture.read()        # Đọc khung hình từ camera
    if not ret:
        print("[ERROR] Không đọc được camera.")
        break

  
    # Tìm khuôn mặt và mã hóa khuôn mặt trong khung hình
    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
    face_names = []

    face_matched = False  # Biến kiểm tra có khớp với khuôn mặt đã lưu không

    # So sánh từng khuôn mặt tìm thấy với khuôn mặt mẫu
    for face_encoding in face_encodings:
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.45)
        name = "Sorry!"  # Nếu không khớp sẽ gán tên này

        if best_match_index is not None and matches[best_match_index]:
            name = known_face_names[best_match_index]
            face_matched = True  # ✅ Đã nhận diện đúng khuôn mặt

        face_names.append(name)

    # ==== Kiểm tra thời gian nhận diện liên tục ====
    current_time = time.time()

    if face_matched:
        if start_detect_time is None:
            start_detect_time = current_time  # Ghi thời gian bắt đầu nhận diện đúng

        elif current_time - start_detect_time >= UNLOCK_TRIGGER_DURATION and not unlock_sent:
            try:
                # Gửi yêu cầu HTTP đến ESP8266 để mở khóa
                response = requests.get("http://192.168.38.132/unlock")
                if response.status_code == 200:
                    print("[SUCCESS] Mở khóa sau 3 giây nhận diện.")
                    os.system("afplay mokhoa.mp3 &")  # 🔊 Phát âm thanh xác nhận mở khóa (macOS)
                else:
                    print(f"[WARNING] ESP8266 trả về mã lỗi: {response.status_code}")
                unlock_sent = True  # Đã gửi yêu cầu thành công
            except Exception as e:
                print("[ERROR] Gửi yêu cầu mở khoá thất bại:", e)
    else:
        start_detect_time = None   # Reset lại nếu khuôn mặt không khớp
        unlock_sent = False        # Cho phép gửi lại lệnh sau

    # ==== Vẽ khung quanh khuôn mặt và hiển thị tên ====
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        # Phóng to lại vì ảnh đã bị resize trước đó
        top *= 2
        right *= 2
        bottom *= 2
        left *= 2

        color = (0, 255, 0) if name == "OK! Good!" else (0, 0, 255)  # Xanh nếu khớp, đỏ nếu không
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)  # Vẽ khung
        cv2.rectangle(frame, (left, bottom - 25), (right, bottom), color, cv2.FILLED)  # Nền cho chữ
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.6, (255, 255, 255), 1)

    # Hiển thị thời gian đếm khi đang nhận diện đúng
    if start_detect_time and not unlock_sent:
        elapsed = int(current_time - start_detect_time)
        cv2.putText(frame, f"Test face... {elapsed}/3s",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

    # Hiển thị khung hình lên cửa sổ
    cv2.imshow('Face Unlock - Nhấn q để thoát', frame)

    # Nhấn 'q' để thoát chương trình
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("[INFO] Đóng chương trình...")
        break

# ==== Giải phóng tài nguyên sau khi thoát ====
video_capture.release()
cv2.destroyAllWindows()
