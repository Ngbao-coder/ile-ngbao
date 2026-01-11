import os
import re
import json
import time
import base64
import random
import requests
from typing import Dict, Any

def get_guid():
    section_length = int(time.time() * 1000)
    
    def replace_func(c):
        nonlocal section_length
        r = (section_length + random.randint(0, 15)) % 16
        section_length //= 16
        return hex(r if c == "x" else (r & 7) | 8)[2:]

    return "".join(replace_func(c) if c in "xy" else c for c in "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx")

def normalize_cookie(cookie, domain='www.facebook.com'):
    headers = {
        'Cookie': cookie,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (like Gecko) Chrome/122.0.0.0 Safari/537.36'
    }
    try:
        response = requests.get(f'https://{domain}/', headers=headers, timeout=10)
        if response.status_code == 200:
            set_cookie = response.headers.get('Set-Cookie', '')
            new_tokens = re.findall(r'([a-zA-Z0-9_-]+)=[^;]+', set_cookie)
            cookie_dict = dict(re.findall(r'([a-zA-Z0-9_-]+)=([^;]+)', cookie))
            for token in new_tokens:
                if token not in cookie_dict:
                    cookie_dict[token] = ''
            return ';'.join(f'{k}={v}' for k, v in cookie_dict.items() if v)
    except:
        pass
    return cookie

def get_uid_fbdtsg(ck):
    try:
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US,en;q=0.9,vi;q=0.8',
            'Connection': 'keep-alive',
            'Cookie': ck,
            'Host': 'www.facebook.com',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (like Gecko) Chrome/122.0.0.0 Safari/537.36'
        }
        
        try:
            response = requests.get('https://www.facebook.com/', headers=headers)
            
            if response.status_code != 200:
                print(f"Status Code >> {response.status_code}")
                return None, None, None, None, None, None
                
            html_content = response.text
            
            user_id = None
            fb_dtsg = None
            jazoest = None
            
            script_tags = re.findall(r'<script id="__eqmc" type="application/json[^>]*>(.*?)</script>', html_content)
            for script in script_tags:
                try:
                    json_data = json.loads(script)
                    if 'u' in json_data:
                        user_param = re.search(r'__user=(\d+)', json_data['u'])
                        if user_param:
                            user_id = user_param.group(1)
                            break
                except:
                    continue
            
            fb_dtsg_match = re.search(r'"f":"([^"]+)"', html_content)
            if fb_dtsg_match:
                fb_dtsg = fb_dtsg_match.group(1)
            
            jazoest_match = re.search(r'jazoest=(\d+)', html_content)
            if jazoest_match:
                jazoest = jazoest_match.group(1)
            
            revision_match = re.search(r'"server_revision":(\d+),"client_revision":(\d+)', html_content)
            rev = revision_match.group(1) if revision_match else ""
            
            a_match = re.search(r'__a=(\d+)', html_content)
            a = a_match.group(1) if a_match else "1"
            
            req = "1b"
                
            return user_id, fb_dtsg, rev, req, a, jazoest
                
        except requests.exceptions.RequestException as e:
            print(f"Lỗi Kết Nối Khi Lấy UID/FB_DTSG: {e}")
            return get_uid_fbdtsg(ck)
            
    except Exception as e:
        print(f"Lỗi: {e}")
        return None, None, None, None, None, None

def get_info(uid: str, cookie: str, fb_dtsg: str, a: str, req: str, rev: str) -> Dict[str, Any]:
    try:
        form = {
            "ids[0]": uid,
            "fb_dtsg": fb_dtsg,
            "__a": a,
            "__req": req,
            "__rev": rev
        }
        
        headers = {
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9,vi;q=0.8',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cookie': cookie,
            'Origin': 'https://www.facebook.com',
            'Referer': 'https://www.facebook.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (like Gecko) Chrome/122.0.0.0 Safari/537.36'
        }
        
        response = requests.post(
            "https://www.facebook.com/chat/user_info/",
            headers=headers,
            data=form
        )
        
        if response.status_code != 200:
            return {"error": f"Lỗi Kết Nối: {response.status_code}"}
        
        try:
            text_response = response.text
            if text_response.startswith("for (;;);"):
                text_response = text_response[9:]
            
            res_data = json.loads(text_response)
            
            if "error" in res_data:
                return {"error": res_data.get("error")}
            
            if "payload" in res_data and "profiles" in res_data["payload"]:
                return format_data(res_data["payload"]["profiles"])
            else:
                return {"error": f"Không Tìm Thấy Thông Tin Của {uid}"}
                
        except json.JSONDecodeError:
            return {"error": "Lỗi Khi Phân Tích JSON"}
            
    except Exception as e:
        print(f"Lỗi Khi Get Info: {e}")
        return {"error": str(e)}

def format_data(profiles):
    if not profiles:
        return {"error": "Không Có Data"}
    
    first_profile_id = next(iter(profiles))
    profile = profiles[first_profile_id]
    
    return {
        "id": first_profile_id,
        "name": profile.get("name", ""),
        "url": profile.get("url", ""),
        "thumbSrc": profile.get("thumbSrc", ""),
        "gender": profile.get("gender", "")
    }

def cmt_gr_pst(cookie, grid, postIDD, ctn, user_id, fb_dtsg, rev, req, a, jazoest, uidtag=None, nametag=None):
    try:
        if not all([user_id, fb_dtsg, jazoest]):
            print("Thiếu user_id, fb_dtsg hoặc jazoest")
            return False
            
        pstid_enc = base64.b64encode(f"feedback:{postIDD}".encode()).decode()
        
        client_mutation_id = str(round(random.random() * 19))
        session_id = get_guid()  
        crt_time = int(time.time() * 1000)
        
        variables = {
            "feedLocation": "DEDICATED_COMMENTING_SURFACE",
            "feedbackSource": 110,
            "groupID": grid,
            "input": {
                "client_mutation_id": client_mutation_id,
                "actor_id": user_id,
                "attachments": None,
                "feedback_id": pstid_enc,
                "formatting_style": None,
                "message": {
                    "ranges": [],
                    "text": ctn
                },
                "attribution_id_v2": f"SearchCometGlobalSearchDefaultTabRoot.react,comet.search_results.default_tab,tap_search_bar,{crt_time},775647,391724414624676,,",
                "vod_video_timestamp": None,
                "is_tracking_encrypted": True,
                "tracking": [],
                "feedback_source": "DEDICATED_COMMENTING_SURFACE",
                "session_id": session_id
            },
            "inviteShortLinkKey": None,
            "renderLocation": None,
            "scale": 3,
            "useDefaultActor": False,
            "focusCommentID": None,
            "__relay_internal__pv__IsWorkUserrelayprovider": False
        }
        
        if uidtag and nametag:
            name_position = ctn.find(nametag)
            if name_position != -1:
                variables["input"]["message"]["ranges"] = [
                    {
                        "entity": {
                            "id": uidtag
                        },
                        "length": len(nametag),
                        "offset": name_position
                    }
                ]
            
        payload = {
            'av': user_id,
            '__crn': 'comet.fbweb.CometGroupDiscussionRoute',
            'fb_dtsg': fb_dtsg,
            'jazoest': jazoest,
            'fb_api_caller_class': 'RelayModern',
            'fb_api_req_friendly_name': 'useCometUFICreateCommentMutation',
            'variables': json.dumps(variables),
            'server_timestamps': 'true',
            'doc_id': '24323081780615819'
        }
        
        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'identity',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cookie': cookie,
            'Origin': 'https://www.facebook.com',
            'Referer': f'https://www.facebook.com/groups/{grid}',
            'User-Agent': 'python-http/0.27.0'
        }
        
        response = requests.post('https://www.facebook.com/api/graphql', data=payload, headers=headers)
        print(f"Mã trạng thái cho bài {postIDD}: {response.status_code}")
        print(f"Phản hồi: {response.text[:500]}...")  
        
        if response.status_code == 200:
            try:
                json_response = response.json()
                if 'errors' in json_response:
                    print(f"Lỗi GraphQL: {json_response['errors']}")
                    return False
                if 'data' in json_response and 'comment_create' in json_response['data']:
                    print("Bình luận đã được đăng")
                    return True
                print("Không tìm thấy comment_create trong phản hồi")
                return False
            except ValueError:
                print("Phản hồi JSON không hợp lệ")
                return False
        else:
            return False
    except Exception as e:
        print(f"Lỗi khi gửi bình luận: {e}")
        return False

def extract_post_group_id(post_link):
    post_match = re.search(r'facebook\.com/.+/permalink/(\d+)', post_link)
    group_match = re.search(r'facebook\.com/groups/(\d+)', post_link)
    if not post_match or not group_match:
        return None, None
    return post_match.group(1), group_match.group(1)

def run_nhaytop_tool():
    cookie = input("Nhập cookie Facebook: ").strip()
    delay = float(input("Nhập thời gian delay (giây): ").strip())
    post_link = input("Nhập link bài viết trong group: ").strip()
    file_name = input("Nhập tên file chứa nội dung spam (vd: file.txt): ").strip()

    if not os.path.exists(file_name):
        print(f"Không tìm thấy file '{file_name}'")
        return

    post_id, group_id = extract_post_group_id(post_link)
    if not post_id or not group_id:
        print("Link không hợp lệ hoặc không lấy được post/group ID")
        return

    cookie = normalize_cookie(cookie)
    user_id, fb_dtsg, rev, req, a, jazoest = get_uid_fbdtsg(cookie)
    if not user_id or not fb_dtsg or not jazoest:
        print("Cookie không hợp lệ hoặc không thể lấy dữ liệu")
        return

    with open(file_name, 'r', encoding='utf-8') as f:
        content = f.read().strip()
    if not content:
        print(f"File '{file_name}' rỗng")
        return

    # ✅ Thêm lựa chọn tag người dùng
    tag_option = input("Bạn có muốn tag người nào trong comment không? (y/n): ").strip().lower()
    uidtag = None
    nametag = None

    if tag_option == 'y':
        uidtag = input("Nhập UID của người cần tag: ").strip()
        user_info = get_info(uidtag, cookie, fb_dtsg, a, req, rev)

        if "error" in user_info:
            print(f"Lỗi khi lấy tên từ UID: {user_info['error']}")
            return
        nametag = user_info["name"]

    print(f"\n🔁 Đang bắt đầu nhây vào bài viết mỗi {delay} giây... (Toàn bộ nội dung trong file)")
    while True:
        if tag_option == 'y' and nametag:
            # Ghép tên vào nội dung
            if random.choice([True, False]):
                content_tagged = f"{nametag} {content}"
            else:
                content_tagged = f"{content} {nametag}"
            success = cmt_gr_pst(cookie, group_id, post_id, content_tagged, user_id, fb_dtsg, rev, req, a, jazoest, uidtag, nametag)
        else:
            success = cmt_gr_pst(cookie, group_id, post_id, content, user_id, fb_dtsg, rev, req, a, jazoest)

        if success:
            print("[✓] Đã gửi thành công.")
        else:
            print("[✗] Gửi thất bại.")
        time.sleep(delay)

if __name__ == "__main__":
    run_nhaytop_tool()