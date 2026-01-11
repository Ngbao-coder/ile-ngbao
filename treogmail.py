import smtplib
import ssl
import time
from email.mime.text import MIMEText

def parse_accounts(input_str):
    accounts = []
    for entry in input_str.strip().split("/"):
        try:
            email, password = entry.strip().split("|")
            accounts.append({
                "server": "smtp.gmail.com",
                "port": 465,
                "email": email.strip(),
                "password": password.strip().replace(" ", ""),
                "active": True
            })
        except:
            print(f"[!] Lỗi định dạng account: {entry}")
    return accounts

def send_mail(smtp_info, to_email, content):
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_info["server"], smtp_info["port"], context=context) as server:
        server.login(smtp_info["email"], smtp_info["password"])
        msg = MIMEText(content)
        msg["From"] = smtp_info["email"]
        msg["To"] = to_email
        msg["Subject"] = " "  # Không tiêu đề
        server.sendmail(smtp_info["email"], to_email, msg.as_string())

def spam_loop(smtp_list, to_email, content, delay):
    acc_index = 0
    while True:
        active_accounts = [acc for acc in smtp_list if acc['active']]
        if not active_accounts:
            print("[!] Tất cả tài khoản đều bị lỗi. Reset lại toàn bộ.")
            for acc in smtp_list:
                acc['active'] = True
            acc_index = 0

        smtp_info = active_accounts[acc_index % len(active_accounts)]

        try:
            send_mail(smtp_info, to_email, content)
            print(f"[+] Gửi từ {smtp_info['email']} -> {to_email}")
        except smtplib.SMTPAuthenticationError as e:
            print(f"[!] Lỗi đăng nhập {smtp_info['email']}: {e}")
            smtp_info['active'] = False
        except smtplib.SMTPDataError as e:
            if b'Quota' in str(e).encode() or b'limit' in str(e).encode():
                print(f"[!] {smtp_info['email']} bị giới hạn quota. Chuyển tài khoản.")
                smtp_info['active'] = False
            else:
                print(f"[!] Lỗi SMTP từ {smtp_info['email']}: {e}")
        except Exception as e:
            print(f"[!] Lỗi không xác định từ {smtp_info['email']}: {e}")
        finally:
            acc_index += 1
            time.sleep(delay)

def main():
    try:
        account_input = input("Nhập danh sách tài khoản (email|pass/email|pass/...):\n")
        smtp_list = parse_accounts(account_input)

        to_email = input("Nhập Gmail người nhận: ")

        file_name = input("Nhập tên file chứa nội dung (ví dụ: file.txt): ")
        try:
            with open(file_name, "r", encoding="utf-8") as f:
                content = f.read().strip()
            if not content:
                print("[!] File không có nội dung.")
                return
        except FileNotFoundError:
            print(f"[!] Không tìm thấy file: {file_name}")
            return

        delay = int(input("Nhập delay giữa mỗi lần gửi (giây): "))

        spam_loop(smtp_list, to_email, content, delay)

    except KeyboardInterrupt:
        print("\n[!] Đã dừng bởi người dùng.")
    except Exception as e:
        print(f"[!] Lỗi không xác định trong main(): {e}")
        time.sleep(5)
        main()  # Tự động khởi chạy lại nếu có lỗi ngoài ý muốn

if __name__ == "__main__":
    main()