import socket
import threading
import datetime
from tkinter import Tk, Text, Button, END, Scrollbar, Entry, StringVar

# Hàm gửi tin nhắn từ GUI server đến client
def send_message(server_socket, client_socket, message_var, log_display):
    message = message_var.get()  # Lấy nội dung tin nhắn từ Entry widget
    if message.strip():  # Kiểm tra tin nhắn không rỗng
        # Hiển thị tin nhắn trên màn hình server với timestamp
        log_display.insert(END, f"[{datetime.datetime.now()}] Server: {message}\n")
        log_display.see(END)  # Tự động cuộn xuống tin nhắn mới nhất
        # Gửi tin nhắn tới client
        client_socket.send(message.encode('utf-8'))
        # Xóa nội dung trong ô nhập
        message_var.set("")

# Hàm xử lý kết nối của mỗi client trong một thread riêng
def handle_client(client_socket, client_address, log_display):
    # Hiển thị thông báo có client kết nối mới
    log_display.insert(END, f"[{datetime.datetime.now()}] Kết nối từ {client_address}\n")
    log_display.see(END)

    while True:
        try:
            # Nhận tin nhắn từ client (tối đa 1024 bytes)
            message = client_socket.recv(1024).decode('utf-8')
            
            # Kiểm tra client ngắt kết nối hoặc gửi lệnh thoát
            if not message or message.lower() == 'exit':
                log_display.insert(END, f"[{datetime.datetime.now()}] Client {client_address} đã ngắt kết nối.\n")
                log_display.see(END)
                break

            # Hiển thị tin nhắn từ client
            log_display.insert(END, f"[{datetime.datetime.now()}] Client {client_address}: {message}\n")
            log_display.see(END)

        except Exception as e:
            # Xử lý các lỗi phát sinh
            log_display.insert(END, f"[{datetime.datetime.now()}] Lỗi: {e}\n")
            log_display.see(END)
            break
    
    # Đóng kết nối sau khi kết thúc
    client_socket.close()

# Hàm khởi tạo server và giao diện GUI
def start_server_gui():
    # Hàm khởi động server trong thread riêng
    def start_server_thread(log_display, message_var, send_button):
        try:
            # Tạo socket TCP
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Bind socket với địa chỉ và cổng
            server_socket.bind(('localhost', 8080))
            # Lắng nghe kết nối (tối đa 1 client)
            server_socket.listen(1)
            
            log_display.insert(END, f"[{datetime.datetime.now()}] Server đang lắng nghe trên cổng 8080...\n")
            log_display.see(END)

            # Chấp nhận kết nối từ client
            client_socket, client_address = server_socket.accept()
            log_display.insert(END, f"[{datetime.datetime.now()}] Client {client_address} đã kết nối.\n")
            log_display.see(END)

            # Tạo thread mới để xử lý client
            threading.Thread(target=handle_client, 
                           args=(client_socket, client_address, log_display)).start()

            # Cấu hình nút gửi tin nhắn
            send_button.config(command=lambda: send_message(server_socket, 
                                                          client_socket, 
                                                          message_var, 
                                                          log_display))

        except Exception as e:
            log_display.insert(END, f"[{datetime.datetime.now()}] Lỗi: {e}\n")
            log_display.see(END)

    # Tạo cửa sổ giao diện chính
    root = Tk()
    root.title("Server Chat - TCP Socket")

    # Tạo vùng hiển thị log chat
    log_display = Text(root, height=20, width=80, wrap="word")
    log_display.pack(side="left", fill="both", expand=True)

    # Thêm thanh cuộn cho vùng log
    scrollbar = Scrollbar(root, command=log_display.yview)
    scrollbar.pack(side="right", fill="y")
    log_display.config(yscrollcommand=scrollbar.set)

    # Tạo vùng nhập tin nhắn
    message_var = StringVar()
    message_entry = Entry(root, textvariable=message_var, width=60)
    message_entry.pack(pady=10, side="left", fill="x", expand=True)

    # Tạo nút gửi tin nhắn
    send_button = Button(root, text="Gửi")
    send_button.pack(pady=10, side="left")

    # Tạo nút khởi động server
    start_button = Button(root, 
                         text="Khởi động Server", 
                         command=lambda: threading.Thread(
                             target=start_server_thread,
                             args=(log_display, message_var, send_button)
                         ).start())
    start_button.pack(pady=10)

    # Khởi chạy vòng lặp sự kiện GUI
    root.mainloop()

# Khởi chạy server khi chạy file trực tiếp
if __name__ == '__main__':
    start_server_gui()