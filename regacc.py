import tls_client
import requests
import time
import re
import random
import string
import json
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from nacl.public import SealedBox, PublicKey
import nacl.utils
import threading
from bs4 import BeautifulSoup
import os

def get_domains():
    # Sử dụng API công khai từ 1secmail để lấy danh sách domains
    url = "https://www.1secmail.com/api/v1/?action=getDomainList"
    try:
        session = tls_client.Session(client_identifier="chrome_112")
        r = session.get(url)
        if r.status_code == 200:
            domains = r.json()
            if not domains:
                print("Danh sách domain trống.")
            return domains
        else:
            print(f"Lỗi HTTP khi lấy domains: {r.status_code}")
    except Exception as e:
        print(f"Lỗi khi lấy domains: {e}")
    # Fallback: Danh sách domains tĩnh từ 1secmail (cập nhật 2025)
    fallback_domains = [
        "1secmail.com", "1secmail.org", "1secmail.net", "wwjmp.com",
        "yagerz.com", "example.com", "emailondeck.com", "gustr.com",
        "sharklasers.com", "guerrillamail.com", "tempmail.org"
    ]
    print("Sử dụng danh sách domains fallback.")
    return fallback_domains

def generate_random_email(domain):
    length = 8
    chars = string.ascii_lowercase + string.digits
    name = ''.join(random.choices(chars, k=length))
    return f"{name}@{domain}"

def Encrypt_Password(public_key_data, password):
    try:
        current_time = str(int(time.time()))
        key_id = int(public_key_data['keyId'])
        public_key = bytes.fromhex(public_key_data['publicKey'])
        if len(public_key) != 32:
            raise ValueError('PublicKey không hợp lệ')
        password_bytes = password.encode('utf-8')
        timestamp_bytes = current_time.encode('utf-8')
        key = nacl.utils.random(32)
        aes_gcm = AESGCM(key)
        encrypted_data = aes_gcm.encrypt(bytes(12), password_bytes, timestamp_bytes)
        sealed_box = SealedBox(PublicKey(public_key))
        sealed_key = sealed_box.encrypt(key)
        t = bytearray(48 + 2 + len(sealed_key) + len(encrypted_data))
        u = 0
        t[u] = 1
        u += 1
        t[u] = key_id
        u += 1
        t[u:u+2] = len(sealed_key).to_bytes(2, 'little')
        u += 2
        t[u:u+len(sealed_key)] = sealed_key
        u += len(sealed_key)
        t[u:u+16] = encrypted_data[-16:]
        u += 16
        t[u:] = encrypted_data[:-16]
        hashed_password = base64.b64encode(t).decode('utf-8')
        return f"#PWD_BROWSER:5:{current_time}:{hashed_password}"
    except Exception as err:
        print(f"Lỗi mã hóa mật khẩu: {err}")
        return None

class ProxyHandler:
    def __init__(self, file_path):
        self.proxies = []
        self.lock = threading.Lock()
        self.current_line = 0
        
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    self.proxies = [line.strip() for line in f if line.strip()]
            except Exception as e:
                print(f"Lỗi đọc file proxy: {e}")
        
        if not self.proxies:
            print("Không có proxy khả dụng, chạy không dùng proxy")

    def get_next_proxy(self):
        with self.lock:
            if not self.proxies:
                return None, None, None
            proxy_line = self.proxies[self.current_line]
            self.current_line = (self.current_line + 1) % len(self.proxies)
            parts = proxy_line.split(':')
            if len(parts) == 2:
                ip, port = parts
                proxy_hostport = f"{ip}:{port}"
                return proxy_hostport, None, None
            elif len(parts) == 4:
                ip, port, user, pwd = parts
                proxy_hostport = f"{ip}:{port}"
                return proxy_hostport, user, pwd
            else:
                print(f"Định dạng proxy không hợp lệ: {proxy_line}")
                return None, None, None

def Check_Live_Fb(uid):
    url = f"https://graph2.facebook.com/v3.3/{uid}/picture?redirect=0"
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        if not data.get('data', {}).get('height') or not data.get('data', {}).get('width'):
            return 'DIE'
        return 'LIVE'
    except Exception as e:
        print(f"Lỗi kiểm tra trạng thái FB sống: {e}")
        return 'ERROR'

def check_otp_mail_api(email, max_attempts=30, delay=5):
    # Chuyển sang API công khai từ 1secmail để kiểm tra OTP
    domain = email.split('@')[1]
    username = email.split('@')[0]
    url = f"https://www.1secmail.com/api/v1/?action=getMessages&login={username}&domain={domain}"
    session = tls_client.Session(client_identifier="chrome_112")
    for attempt in range(max_attempts):
        try:
            r = session.get(url)
            if r.status_code == 200:
                messages = r.json()
                if messages:
                    # Lấy ID của message mới nhất
                    msg_id = messages[-1]['id']
                    # Lấy nội dung message
                    msg_url = f"https://www.1secmail.com/api/v1/?action=readMessage&login={username}&domain={domain}&id={msg_id}"
                    msg_r = session.get(msg_url)
                    if msg_r.status_code == 200:
                        msg_data = msg_r.json()
                        subject = msg_data.get("subject", "")
                        text = msg_data.get("textBody", "") + msg_data.get("htmlBody", "")
                        if "FB-" in subject or "code" in text.lower():
                            # Trích xuất OTP từ subject hoặc body (giả sử 5-6 chữ số)
                            otp_match = re.search(r'\b(\d{5,6})\b', subject + text)
                            if otp_match:
                                otp = otp_match.group(1)
                                print(f"Tìm thấy OTP: {otp}")
                                return otp
                else:
                    print("API trả về thất bại khi lấy mail.")
            else:
                print(f"Lỗi HTTP lấy mail: {r.status_code}")
        except Exception as e:
            print(f"Lỗi lấy OTP: {e}")
        print(f"Thử lại lần {attempt+1}/{max_attempts} sau {delay} giây...")
        time.sleep(delay)
    print("Không tìm thấy OTP sau số lần thử tối đa.")
    return None

def get_headers_base():
    return {
        'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
    }

def verify_otp_new_api(session, otp, email, c_user, fb_dtsg, lsd, jazoest, spin_r, spin_t, hsi, dyn, hsdp, hblp, s):
    try:
        confirm_page_url = f"https://www.facebook.com/confirmemail.php?next=https%3A%2F%2Fwww.facebook.com%2F%3Flocale%3Dvi_VN"
        
        confirm_headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'accept-encoding': 'gzip, deflate',
            'accept-language': 'vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5',
            'referer': 'https://www.facebook.com/',
            'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36'
        }
        
        print("Đang lấy trang xác nhận email...")
        confirm_response = session.get(confirm_page_url, headers=confirm_headers)
        
        if confirm_response.status_code != 200:
            print(f"Không thể lấy trang xác nhận: {confirm_response.status_code}")
            return False
            
        soup = BeautifulSoup(confirm_response.text, 'html.parser')
        hidden_inputs = soup.find_all('input', {'type': 'hidden'})
        confirm_data = {tag.get('name'): tag.get('value', '') for tag in hidden_inputs}
        
        if confirm_data.get('fb_dtsg'):
            fb_dtsg = confirm_data.get('fb_dtsg')
        if confirm_data.get('lsd'):
            lsd = confirm_data.get('lsd')
        if confirm_data.get('jazoest'):
            jazoest = confirm_data.get('jazoest')
            
        print("Lấy trang xác nhận email thành công")
        
        verify_url = f"https://www.facebook.com/confirm_code/dialog/submit/?next=https%3A%2F%2Fwww.facebook.com%2F%3Flocale%3Dvi_VN&cp={email}&from_cliff=1&conf_surface=hard_cliff&event_location=cliff"
        
        verify_headers = {
            'accept': '*/*',
            'accept-encoding': 'gzip, deflate',
            'accept-language': 'vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://www.facebook.com',
            'priority': 'u=1, i',
            'referer': confirm_page_url,
            'sec-ch-prefers-color-scheme': 'light',
            'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
            'sec-ch-ua-full-version-list': '"Not)A;Brand";v="8.0.0.0", "Chromium";v="138.0.7204.158", "Google Chrome";v="138.0.7204.158"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-model': '""',
            'sec-ch-ua-platform': '"Windows"',
            'sec-ch-ua-platform-version': '"7.0.0"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36'
        }
        
        verify_data = {
            'next': 'https://www.facebook.com/?locale=vi_VN',
            'cp': email,
            'from_cliff': '1',
            'conf_surface': 'hard_cliff',
            'event_location': 'cliff',
            'jazoest': jazoest,
            'fb_dtsg': fb_dtsg,
            'code': otp,
            'source_verified': 'www_reg',
            'confirm': '1',
            '__user': c_user,
            '__a': '1',
            '__req': '5',
            'dpr': '1',
            '__ccg': 'EXCELLENT',
            '__rev': '1025303927',
            'lsd': lsd,
            '__spin_r': spin_r,
            '__spin_b': 'trunk',
            '__spin_t': spin_t
        }
        
        print(f"Đang xác minh OTP: {otp}")
        response = session.post(verify_url, headers=verify_headers, data=verify_data)
        
        if response.status_code == 200:
            response_text = response.text
            if response_text.startswith('for (;;);'):
                response_text = response_text[9:]
            
            try:
                json_response = json.loads(response_text)
                if 'error' in json_response:
                    error_code = json_response.get('error', 'Không rõ')
                    error_description = json_response.get('errorDescription', 'Không có mô tả')
                    print(f"Xác minh OTP thất bại - Lỗi {error_code}: {error_description}")
                    return False
                else:
                    print("Xác minh OTP thành công")
                    return True
            except json.JSONDecodeError:
                print(f"Không thể phân tích phản hồi JSON: {response_text}")
                return False
        else:
            print(f"Lỗi HTTP trong quá trình xác minh OTP: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"Lỗi trong quá trình xác minh OTP: {e}")
        return False

def Facebook_Register(ho, ten, email, password, proxy_handler):
    proxy, proxy_user, proxy_pass = proxy_handler.get_next_proxy()
    
    session = tls_client.Session(client_identifier="chrome_112", random_tls_extension_order=True)
    
    if proxy:
        if proxy_user and proxy_pass:
            proxy_url = f"http://{proxy_user}:{proxy_pass}@{proxy}"
        else:
            proxy_url = f"http://{proxy}"
        
        session.proxies = {
            'http': proxy_url,
            'https': proxy_url
        }
        print(f"Đang sử dụng proxy: {proxy}")
    else:
        print("Chạy không dùng proxy")

    headers_base = get_headers_base()

    headers_get = {
        'sec-ch-ua': headers_base['sec-ch-ua'],
        'sec-ch-ua-mobile': headers_base['sec-ch-ua-mobile'],
        'sec-ch-ua-platform': headers_base['sec-ch-ua-platform'],
        'upgrade-insecure-requests': '1',
        'user-agent': headers_base['user-agent'],
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'document',
        'referer': 'https://www.facebook.com/',
    }

    try:
        url_home = "https://www.facebook.com/"
        print(f"Gửi yêu cầu GET tới: {url_home}")
        r1 = session.get(url_home, headers=headers_get)
        if r1.status_code != 200:
            print(f"Lỗi HTTP khi lấy trang chủ Facebook: {r1.status_code}")
            return "REQUEST_FAILED"

        pk_pattern = r'"publicKey":"([a-fA-F0-9]+)"'
        kid_pattern = r'"keyId":(\d+)'

        pk_match = re.search(pk_pattern, r1.text)
        kid_match = re.search(kid_pattern, r1.text)
        if not pk_match or not kid_match:
            print("Không thể trích xuất PublicKey hoặc KeyId.")
            return "KEY_EXTRACTION_FAILED"

        public_key_data = {
            'publicKey': pk_match.group(1),
            'keyId': int(kid_match.group(1))
        }

        encrypted_password = Encrypt_Password(public_key_data, password)
        if not encrypted_password:
            print("Mã hóa mật khẩu thất bại.")
            return "PASSWORD_ENCRYPTION_FAILED"

        url_reg_page = "https://www.facebook.com/r.php?entry_point=login"
        print(f"Gửi yêu cầu GET tới: {url_reg_page}")
        r2 = session.get(url_reg_page, headers=headers_get)
        if r2.status_code != 200:
            print(f"Lỗi HTTP khi lấy trang đăng ký Facebook: {r2.status_code}")
            return "REQUEST_FAILED"

        soup = BeautifulSoup(r2.text, 'html.parser')
        hidden_inputs = soup.find_all('input', {'type': 'hidden'})
        form_data = {tag.get('name'): tag.get('value', '') for tag in hidden_inputs}

        fb_dtsg = form_data.get('fb_dtsg', '')
        lsd = form_data.get('lsd', '')
        jazoest = form_data.get('jazoest', '')
        spin_r = form_data.get('__spin_r', '') or (re.search(r'"__spin_r":(\d+)', r2.text).group(1) if re.search(r'"__spin_r":(\d+)', r2.text) else '')
        spin_t = form_data.get('__spin_t', '') or (re.search(r'"__spin_t":(\d+)', r2.text).group(1) if re.search(r'"__spin_t":(\d+)', r2.text) else '')
        hsi = re.search(r'"hsi":"(\d+)"', r2.text).group(1) if re.search(r'"hsi":"(\d+)"', r2.text) else '7453027861273714271'
        dyn = re.search(r'"__dyn":"([^"]+)"', r2.text).group(1) if re.search(r'"__dyn":"([^"]+)"', r2.text) else '7xe6EsK36Q5E5ObwKBWg5S1Dxu13wqovzEdEc8uw9-3K0lW4o3Bw5VCwjE3awdu0FE2awpUO0n24o5-0me1Fw5uwbO0KU3mwaS0zE5W08HwSyE1582ZwrU1Xo1UU3jwea'
        hsdp = re.search(r'"hsdp":"([^"]+)"', r2.text).group(1) if re.search(r'"hsdp":"([^"]+)"', r2.text) else 'gH4Ebhy4i2R5q5448qqlx8xXxybBoyE7EMvUtwTGfxe2S6ho4G224Eae0qq0ZUF0lo1MEHwhUtx8w'
        hblp = re.search(r'"hblp":"([^"]+)"', r2.text).group(1) if re.search(r'"hblp":"([^"]+)"', r2.text) else '0Vwb21RxS0nyU2Awuo1_U2Rwce780wm0cFw2qE6q0u201lpwb2awgJKWiyaDgCbCg0wm0ge0fKw0zbw36E'
        s = re.search(r'"__s":"([^"]+)"', r2.text).group(1) if re.search(r'"__s":"([^"]+)"', r2.text) else 'lxucyo:t0561u:xdnp5s'

        data_post = {
            'jazoest': jazoest,
            'lsd': lsd,
            'lastname': ho,
            'firstname': ten,
            'birthday_day': str(random.randint(1, 28)),
            'birthday_month': str(random.randint(1, 12)),
            'birthday_year': str(random.randint(1988, 2006)),
            'birthday_age': '',
            'did_use_age': 'false',
            'sex': str(random.randint(1, 2)),
            'preferred_pronoun': '',
            'custom_gender': '',
            'reg_email__': email,
            'reg_email_confirmation__': '',
            'reg_passwd__': encrypted_password,
            'referrer': '',
            'asked_to_login': '0',
            'use_custom_gender': '',
            'terms': 'on',
            'ns': '0',
            'ri': form_data.get('ri', ''),
            'action_dialog_shown': '',
            'invid': '',
            'a': '',
            'oi': '',
            'locale': form_data.get('locale', ''),
            'app_bundle': '',
            'app_data': '',
            'reg_data': '',
            'app_id': '',
            'fbpage_id': '',
            'reg_oid': '',
            'reg_instance': form_data.get('reg_instance', ''),
            'openid_token': '',
            'uo_ip': '',
            'guid': '',
            'key': '',
            're': '',
            'mid': '',
            'fid': '',
            'reg_dropoff_id': '',
            'reg_dropoff_code': '',
            'ignore': 'captcha|reg_email_confirmation__',
            'captcha_persist_data': form_data.get('captcha_persist_data', ''),
            'captcha_response': '',
            '__user': '0',
            '__a': '1',
            '__req': '6',
            '__hs': hsi,
            'dpr': '1',
            '__ccg': 'EXCELLENT',
            '__rev': '1019085267',
            '__s': s,
            '__hsi': hsi,
            '__dyn': dyn,
            '__csr': '',
            '__spin_r': spin_r,
            '__spin_b': 'trunk',
            '__spin_t': spin_t,
        }

        headers_post = {
            'x-asbd-id': '129477',
            'sec-ch-ua-platform': '"Windows"',
            'x-fb-lsd': lsd,
            'user-agent': headers_base['user-agent'],
            'sec-ch-ua': headers_base['sec-ch-ua'],
            'content-type': 'application/x-www-form-urlencoded',
            'sec-ch-ua-mobile': '?0',
            'accept': '*/*',
            'origin': 'https://www.facebook.com',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': url_reg_page,
            'priority': 'u=1, i'
        }

        url_post = "https://www.facebook.com/ajax/register.php"
        print(f"Gửi yêu cầu POST đăng ký tới: {url_post}")
        r_post = session.post(url_post, headers=headers_post, data=data_post)
        if r_post.status_code != 200:
            print(f"Lỗi HTTP đăng ký Facebook: {r_post.status_code}")
            return "REQUEST_FAILED"

        if "registration_succeeded" in r_post.text:
            json_text = r_post.text.replace("for (;;);", "")
            resp = json.loads(json_text)
            if resp.get("payload", {}).get("registration_succeeded"):
                cookies = session.cookies
                cookie_string = ''.join(f"{c.name}={c.value};" for c in cookies)
                start = cookie_string.find('c_user=') + 7
                end = cookie_string.find(';', start)
                c_user = cookie_string[start:end]
                full_name = f"{ho} {ten}"

                print(f"Đăng ký thành công: {c_user}")

                check_live = Check_Live_Fb(c_user)
                if check_live == 'DIE':
                    print(f"Tài khoản bị checkpoint: {c_user}")
                    return f"{c_user}|CHECKPOINT"

                with open("success.txt", "a", encoding="utf-8") as f:
                    f.write(f"{c_user}|{password}|{cookie_string}|{email}|{full_name}\n")
                print(f"Đã lưu thông tin tài khoản thành công: {c_user}")

                print("Bắt đầu lấy OTP từ mail...")
                otp = check_otp_mail_api(email, max_attempts=30, delay=5)
                if otp:
                    print(f"Đã lấy OTP: {otp}")
                    verify_result = verify_otp_new_api(session, otp, email, c_user, fb_dtsg, lsd, jazoest, spin_r, spin_t, hsi, dyn, hsdp, hblp, s)
                    if verify_result:
                        print(f"Xác minh OTP thành công cho tài khoản {c_user}")
                        return f"{c_user}|SUCCESS"
                    else:
                        print(f"Xác minh OTP thất bại cho tài khoản {c_user}")
                        return f"{c_user}|VERIFY_FAILED"
                else:
                    print("Không thể lấy OTP để xác minh")
                    return f"{c_user}|NO_OTP"

        else:
            print("Đăng ký thất bại, phản hồi:")
            print(r_post.text)
            return "REGISTRATION_FAILED"

    except Exception as err:
        print(f"Lỗi chung: {err}")
        return "GENERAL_ERROR"

def main():
    proxy_handler = ProxyHandler('proxies.txt')
    domains = get_domains()
    if not domains:
        print("Không thể lấy domains mail giả, thoát.")
        return

    selected_domain = domains[0]  # Chọn domain đầu tiên (bỏ logic 'ploveqmail' vì không cần thiết)
    print(f"Đang sử dụng domain: {selected_domain}")

    print("Nhập thông tin để đăng ký Facebook:")
    ho = input("Nhập họ: ").strip()
    ten = input("Nhập tên: ").strip()
    if not ho or not ten:
        print("Vui lòng nhập đầy đủ họ và tên.")
        return

    while True:
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=15))
        email = generate_random_email(selected_domain)
        print(f"Đang đăng ký với: Họ={ho}, Tên={ten}, Email={email}, Mật khẩu={password}")
        result = Facebook_Register(ho, ten, email, password, proxy_handler)
        print(f"Kết quả đăng ký: {result}")
        time.sleep(random.uniform(5, 10))

if __name__ == "__main__":
    main()