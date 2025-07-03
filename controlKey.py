import tkinter as tk
from tkinter import messagebox
import cv2
import face_recognition
import json
import os
import time
import requests


# ====== Hàm hỗ trợ ======

def save_user_data(name, password, image_path):
    if not os.path.exists("user_data.json"):
        with open("user_data.json", "w") as f:
            json.dump({}, f)

    with open("user_data.json", "r") as f:
        data = json.load(f)

    data[name] = {
        "password": password,
        "image": image_path
    }

    with open("user_data.json", "w") as f:
        json.dump(data, f, indent=4)


# ====== Chức năng chụp ảnh và lưu ======

def open_camera_save():
    def capture_and_save():
        username = entry_name.get().strip()
        password = entry_password.get().strip()
        if not username or not password:
            messagebox.showerror("Lỗi", "Vui lòng nhập tên và mật khẩu.")
            return

        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            messagebox.showerror("Lỗi", "Không mở được camera.")
            return

        messagebox.showinfo("Hướng dẫn", "Nhấn 's' để lưu ảnh, 'q' để thoát.")
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            cv2.imshow("Chụp ảnh", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('s'):
                if not os.path.exists("faces"):
                    os.makedirs("faces")
                file_path = f"faces/{username}.jpg"
                cv2.imwrite(file_path, frame)
                save_user_data(username, password, file_path)
                messagebox.showinfo("Thành công", "Đã lưu thông tin người dùng.")
                break
            elif key == ord('q'):
                break
        cap.release()
        cv2.destroyAllWindows()

    # Hiển thị input
    top = tk.Toplevel(root)
    top.geometry("400x320")
    top.title("📷 Lưu ảnh người dùng")
    tk.Label(top, text="👤 Tên người dùng", fg="blue", font=("Arial", 12, "bold")).pack()
    entry_name = tk.Entry(top)
    entry_name.pack()
    tk.Label(top, text="🔐 Mật khẩu",fg="blue", font=("Arial", 12, "bold")).pack()
    entry_password = tk.Entry(top, show="*")
    entry_password.pack()
    tk.Button(top, text="Mở Camera & Lưu", font=("Arial", 12, "bold"), command=capture_and_save).pack(pady=10)


# ====== Chức năng nhận diện gương mặt ======

def open_camera_recognition():
    def start_recognition():
        try:
            known_image = face_recognition.load_image_file(user_data["image"])
            known_encoding = face_recognition.face_encodings(known_image)[0]
        except:
            messagebox.showerror("Lỗi", "Không thể tải ảnh mẫu.")
            return

        cap = cv2.VideoCapture(0)
        matched = False
        start_time = None

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            faces = face_recognition.face_locations(rgb)
            encodings = face_recognition.face_encodings(rgb, faces)

            for encoding in encodings:
                result = face_recognition.compare_faces([known_encoding], encoding, tolerance=0.45)
                if result[0]:
                    matched = True
                    if start_time is None:
                        start_time = time.time()
                    elif time.time() - start_time >= 3:
                        cap.release()
                        cv2.destroyAllWindows()
                        confirm_identity()
                        return
                else:
                    start_time = None

            for (top, right, bottom, left) in faces:
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0) if matched else (0, 0, 255), 2)

            cv2.imshow("Nhận diện", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

    def confirm_identity():
        def check_credentials():
            entered_name = entry_name.get().strip()
            entered_pass = entry_password.get().strip()

            if entered_name in data and data[entered_name]["password"] == entered_pass:
                try:
                    response = requests.get("http://192.168.0.114/unlock")
                    if response.status_code == 200:
                        os.system("start mokhoa.mp3")
                        messagebox.showinfo("✅", "Mở khoá thành công!")
                    else:
                        messagebox.showerror("ESP8266", "Lỗi từ thiết bị.")
                except Exception as e:
                    messagebox.showerror("Lỗi", f"Không gửi được yêu cầu: {e}")
            else:
                messagebox.showerror("Sai thông tin", "Tên hoặc mật khẩu không đúng.")

        win = tk.Toplevel(root)
        win.title("🔓 Xác nhận người dùng")
        tk.Label(win, text="👤 Tên người dùng").pack()
        entry_name = tk.Entry(win)
        entry_name.pack()
        tk.Label(win, text="🔓 Mật khẩu").pack()
        entry_password = tk.Entry(win, show="*")
        entry_password.pack()
        tk.Button(win, text="Xác nhận mở khoá", command=check_credentials).pack(pady=10)

    # Tải dữ liệu người dùng
    if not os.path.exists("user_data.json"):
        messagebox.showerror("Lỗi", "Chưa có dữ liệu người dùng.")
        return

    with open("user_data.json", "r") as f:
        data = json.load(f)

    # Mở giao diện yêu cầu chọn tên đã có
    top = tk.Toplevel(root)
    top.geometry("400x320")
    top.title("🔍 Nhận diện gương mặt")
    tk.Label(top, text="Chọn người dùng:", font=("Arial", 12, "bold")).pack()
    var = tk.StringVar(top)
    var.set(list(data.keys())[0])  # giá trị mặc định

    tk.OptionMenu(top, var, *data.keys()).pack(pady=5)

    def proceed():
        global user_data
        user_data = data[var.get()]
        top.destroy()
        start_recognition()

    tk.Button(top, text="Bắt đầu nhận diện", font=("Arial", 12, "bold"), command=proceed).pack(pady=10)


# ====== Giao diện chính ======

root = tk.Tk()
root.title("🔐 Smart Locker AI")
root.geometry("400x320")
root.resizable(False, False)

tk.Label(root, text="SMART LOCKER", font=("Arial", 20, "bold")).pack(pady=15)

tk.Button(root,
          text="📷 Mở Camera & Lưu Ảnh",
          font=("Arial", 12,"bold"),
          width=30,
          command=open_camera_save).pack(pady=10)

tk.Button(root,
          text="🔓 Nhận Diện & Mở Khóa",
          font=("Arial", 12,"bold"),
          width=30,
          bg="green",
          fg="white",
          command=open_camera_recognition).pack(pady=10)

tk.Button(root,
          text="❌ Thoát",
          font=("Arial", 12,"bold"),
          width=30,
          bg="red", fg="white",
          command=root.quit).pack(pady=20)

root.mainloop()

