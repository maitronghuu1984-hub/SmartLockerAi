import cv2  # Nhập thư viện OpenCV để xử lý hình ảnh và video

# Mở webcam mặc định (camera số 0)
video_capture = cv2.VideoCapture(0)

print("[INFO] Camera mở thành công. Nhấn 's' để lưu hình, 'q' để thoát.")

# Vòng lặp chính để hiển thị hình ảnh từ webcam
while True:
    ret, frame = video_capture.read()  # Đọc một khung hình từ camera
    if not ret:
        print("[ERROR] Không đọc được camera.")  # Báo lỗi nếu không nhận được hình ảnh
        break

    cv2.imshow('Capture Face', frame)  # Hiển thị khung hình lên cửa sổ

    key = cv2.waitKey(1) & 0xFF  # Đợi người dùng nhấn phím (mỗi 1ms)

    if key == ord('s'):
        # Nếu nhấn phím 's' → lưu ảnh hiện tại thành file
        cv2.imwrite("saved_face.jpg", frame)
        print("[INFO] Đã lưu hình ảnh thành 'saved_face.jpg'")

    elif key == ord('q'):
        # Nếu nhấn phím 'q' → thoát chương trình
        print("[INFO] Đang đóng chương trình...")
        break

# Giải phóng camera và đóng tất cả cửa sổ OpenCV sau khi thoát
video_capture.release()
cv2.destroyAllWindows()
