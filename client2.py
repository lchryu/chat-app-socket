import socket
import threading
import datetime
from tkinter import Tk, Text, Button, Entry, END, Scrollbar, StringVar

# Hàm gửi tin nhắn từ client đến server
def send_message(client_socket, message_var, chat_display):
    message = message_var.get()  # Lấy nội dung tin nhắn từ Entry widget
    if message.strip():  # Kiểm tra tin nhắn không rỗng
        # Hiển thị tin nhắn đã gửi trên màn hình client
        chat_display.insert(END, f"[{datetime.datetime.now()}] Bạn: {message}\n")
        chat_display.see(END)  # Tự động cuộn xuống tin nhắn mới nhất
        # Gửi tin nhắn tới server
        client_socket.send(message.encode('utf-8'))
        # Xóa nội dung trong ô nhập
        message_var.set("")

# Hàm nhận tin nhắn từ server trong thread riêng
def receive_message(client_socket, chat_display):
    while True:
        try:
            # Nhận tin nhắn từ server (tối đa 1024 bytes)
            response = client_socket.recv(1024).decode('utf-8')
            # Hiển thị tin nhắn từ server
            chat_display.insert(END, f"[{datetime.datetime.now()}] Server: {response}\n")
            chat_display.see(END)
        except Exception:
            # Xử lý khi mất kết nối với server
            chat_display.insert(END, f"[{datetime.datetime.now()}] Mất kết nối với server.\n")
            chat_display.see(END)
            break

# Hàm khởi tạo client và giao diện GUI
def start_client_gui():
    try:
        # Tạo socket TCP
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Kết nối tới server
        client_socket.connect(('localhost', 8080))

        # Tạo cửa sổ giao diện chính
        root = Tk()
        root.title("Client Chat - TCP Socket")

        # Tạo vùng hiển thị chat
        chat_display = Text(root, height=20, width=80, wrap="word")
        chat_display.pack(side="left", fill="both", expand=True)

        # Thêm thanh cuộn cho vùng chat
        scrollbar = Scrollbar(root, command=chat_display.yview)
        scrollbar.pack(side="right", fill="y")
        chat_display.config(yscrollcommand=scrollbar.set)

        # Hiển thị thông báo kết nối thành công
        chat_display.insert(END, f"[{datetime.datetime.now()}] Đã kết nối tới server.\n")
        chat_display.see(END)

        # Tạo vùng nhập tin nhắn
        message_var = StringVar()
        message_entry = Entry(root, textvariable=message_var, width=60)
        message_entry.pack(pady=10, side="left", fill="x", expand=True)

        # Tạo nút gửi tin nhắn
        send_button = Button(root, 
                           text="Gửi", 
                           command=lambda: send_message(client_socket, 
                                                      message_var, 
                                                      chat_display))
        send_button.pack(pady=10, side="left")

        # Tạo thread nhận tin nhắn từ server
        threading.Thread(target=receive_message, 
                        args=(client_socket, chat_display)).start()

        # Khởi chạy vòng lặp sự kiện GUI
        root.mainloop()

        # Đóng kết nối khi thoát GUI
        client_socket.close()

    except Exception as e:
        print(f"[{datetime.datetime.now()}] Lỗi: {e}")

# Khởi chạy client khi chạy file trực tiếp
if __name__ == '__main__':
    start_client_gui()