import time
import threading
from instagrapi import Client
from getpass import getpass

SPAM_TASKS = {}

def parse_cookie_str(cookie_str):
    return dict(item.strip().split('=') for item in cookie_str.split(';') if '=' in item)

def spam_loop(acc_id):
    info = SPAM_TASKS.get(acc_id)
    if not info:
        return

    cl = info["client"]
    targets = info["targets"]
    message = info["message"]
    delay = info["delay"]

    while True:
        for target in targets:
            try:
                if target.isdigit():
                    if target not in info["stop_targets"]:
                        cl.direct_send(message, thread_ids=[target])
                else:
                    user_id = cl.user_id_from_username(target)
                    if str(user_id) not in info["stop_targets"]:
                        cl.direct_send(message, [user_id])
                print(f"[+] Gửi thành công tới: {target}")
            except Exception as e:
                print(f"[!] Lỗi gửi {target}: {e}")
        time.sleep(delay)

def login_by_cookie(cookie_str):
    cl = Client()
    cookie_dict = parse_cookie_str(cookie_str)
    sessionid = cookie_dict.get("sessionid")
    if not sessionid:
        raise Exception("Thiếu sessionid trong cookie.")
    cl.login_by_sessionid(sessionid=sessionid)
    return cl

def login_by_password(username, password):
    cl = Client()
    cl.login(username, password)
    return cl

def main():
    print("Tool Spam Instagram")
    print("1. Đăng nhập bằng cookie")
    print("2. Đăng nhập bằng username & password")
    mode = input("Chọn chế độ (1 hoặc 2): ").strip()

    accounts = []
    if mode == "1":
        raw = input("Nhập các cookie IG (phân cách dấu phẩy):\n> ").strip()
        cookies = [x.strip() for x in raw.split(",") if x.strip()]
        for cookie in cookies:
            try:
                cl = login_by_cookie(cookie)
                accounts.append(cl)
                print("[+] Đăng nhập bằng cookie thành công.")
            except Exception as e:
                print(f"[!] Lỗi đăng nhập cookie: {e}")
    elif mode == "2":
        try:
            n = int(input("Nhập số lượng tài khoản: ").strip())
        except:
            return print("Số lượng không hợp lệ.")
        for i in range(n):
            print(f"\n--- Tài khoản {i+1} ---")
            username = input("Username: ").strip()
            password = getpass("Password: ")
            try:
                cl = login_by_password(username, password)
                accounts.append(cl)
                print("[+] Đăng nhập tài khoản thành công.")
            except Exception as e:
                print(f"[!] Lỗi đăng nhập tài khoản: {e}")
    else:
        return print("Chế độ không hợp lệ.")

    if not accounts:
        return print("Không có tài khoản nào đăng nhập thành công.")

    raw_targets = input("\nNhập danh sách ID box hoặc username IG (phân cách dấu phẩy):\n> ").strip()
    targets = [x.strip() for x in raw_targets.split(",") if x.strip()]
    if not targets:
        return print("Không có target nào.")

    file_path = input("Nhập đường dẫn file nội dung (file.txt):\n> ").strip()
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            message = f.read().strip()
    except:
        return print("Không thể đọc file nội dung.")

    try:
        delay = float(input("Nhập delay (số giây):\n> ").strip())
    except:
        return print("Delay không hợp lệ.")

    for idx, cl in enumerate(accounts, start=1):
        spam_info = {
            "thread": None,
            "start_time": time.time(),
            "targets": targets,
            "message": message,
            "delay": delay,
            "client": cl,
            "stop_targets": set()
        }
        thread = threading.Thread(target=spam_loop, args=(idx,))
        thread.daemon = True
        spam_info["thread"] = thread
        SPAM_TASKS[idx] = spam_info
        thread.start()
        print(f"[+] Tài khoản {idx} đã bắt đầu spam.")

    print("\nĐang spam IG... Nhấn Ctrl+C để thoát.")
    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        print("\nĐã dừng tool.")

if __name__ == "__main__":
    main()