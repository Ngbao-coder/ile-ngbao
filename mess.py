import multiprocessing
import time
import json
import os
import random
import requests
import re
import ssl
import paho.mqtt.client as mqtt
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from threading import Event

console = Console()

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

# ==================== HELPER FUNCTIONS ====================
def generate_offline_threading_id():
    ret = int(time.time() * 1000)
    value = random.randint(0, 4294967295)
    binary_str = format(value, "022b")[-22:]
    msgs = bin(ret)[2:] + binary_str
    return str(int(msgs, 2))

def generate_session_id():
    return random.randint(1, 2 ** 53)

def generate_client_id():
    import string
    def gen(length):
        return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))
    return gen(8) + '-' + gen(4) + '-' + gen(4) + '-' + gen(4) + '-' + gen(12)

def parse_cookie_string(cookie_string):
    cookie_dict = {}
    cookies = cookie_string.split(";")
    for cookie in cookies:
        if "=" in cookie:
            key, value = cookie.strip().split("=", 1)
            cookie_dict[key] = value
    return cookie_dict

# ==================== CHECK COOKIE ====================
def check_live(cookie):
    try:
        if 'c_user=' not in cookie:
            return {"status": "failed", "msg": "Cookie không chứa user_id"}
        
        user_id = cookie.split('c_user=')[1].split(';')[0]
        headers = {'cookie': cookie, 'user-agent': 'Mozilla/5.0'}
        response = requests.get(f'https://m.facebook.com/profile.php?id={user_id}', headers=headers, timeout=10)
        name = response.text.split('<title>')[1].split('<')[0].strip()
        return {"status": "success", "name": name, "user_id": user_id}
    except Exception as e:
        return {"status": "failed", "msg": str(e)}

# ==================== TOKEN TO COOKIE ====================
def token_to_cookie(access_token):
    try:
        console.print("[yellow]⏳ Đang chuyển token thành cookie...[/]")
        url = f"https://graph.facebook.com/me?access_token={access_token}"
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            return None
        
        user_id = response.json().get('id')
        if not user_id:
            return None
        
        headers = {'user-agent': 'Mozilla/5.0'}
        get_cookie = requests.get(
            f'https://business.facebook.com/business_locations',
            params={'business_id': user_id},
            headers=headers,
            allow_redirects=True
        )
        
        cookies = get_cookie.cookies.get_dict()
        cookie_string = '; '.join([f'{key}={value}' for key, value in cookies.items()])
        
        if 'c_user' not in cookie_string:
            return None
        
        console.print("[green]✅ Chuyển token thành cookie thành công![/]")
        return cookie_string
    except:
        return None

# ==================== MESSENGER CLASS ====================
class Messenger:
    def __init__(self, cookie, token=None):
        self.cookie = cookie
        self.token = token
        self.user_id = self.get_user_id()
        self.fb_dtsg = None
        self.jazoest = None
        self.client_revision = None
        self.init_params()
        
        # MQTT
        self.mqtt = None
        self.mqtt_connected = False
        self.last_seq_id = None
        self.sync_token = None
        self.ws_req_number = 0
        self.ws_task_number = 0
        
        # Connection management
        self.should_reconnect = True
        self.reconnect_event = Event()
        self.last_activity = time.time()
        self.session_id = generate_session_id()

    THEMES = [
        {"id": "3650637715209675", "name": "Besties"},
        {"id": "769656934577391", "name": "Women's History Month"},
        {"id": "702099018755409", "name": "Dune: Part Two"},
        {"id": "952656233130616", "name": "J.Lo"},
        {"id": "741311439775765", "name": "Love"},
        {"id": "215565958307259", "name": "Bob Marley"},
        {"id": "194982117007866", "name": "Football"},
        {"id": "730357905262632", "name": "Mean Girls"},
        {"id": "1270466356981452", "name": "Wonka"},
        {"id": "292955489929680", "name": "Lollipop"},
        {"id": "195296273246380", "name": "Bubble Tea"},
        {"id": "390127158985345", "name": "Chill"},
        {"id": "339021464972092", "name": "Music"},
        {"id": "3190514984517598", "name": "Sky"},
        {"id": "3259963564026002", "name": "Default"},
    ]

    def get_user_id(self):
        try:
            return re.search(r"c_user=(\d+)", self.cookie).group(1)
        except:
            raise Exception("Cookie không hợp lệ")

    def init_params(self):
        headers = {'Cookie': self.cookie, 'User-Agent': 'Mozilla/5.0'}
        try:
            for url in ['https://www.facebook.com', 'https://mbasic.facebook.com']:
                response = requests.get(url, headers=headers, timeout=10)
                
                if 'login' in response.url.lower() and self.token:
                    console.print("[yellow]⚠️ Cookie die, đang chuyển token...[/]")
                    new_cookie = token_to_cookie(self.token)
                    if new_cookie:
                        self.cookie = new_cookie
                        headers['Cookie'] = new_cookie
                        response = requests.get(url, headers=headers, timeout=10)
                    else:
                        raise Exception("Không thể chuyển token")
                
                match_dtsg = re.search(r'name="fb_dtsg" value="(.*?)"', response.text)
                match_jazoest = re.search(r'name="jazoest" value="(\d+)"', response.text)
                match_rev = re.search(r'"client_revision":(\d+)', response.text)
                
                if match_dtsg and match_jazoest:
                    self.fb_dtsg = match_dtsg.group(1)
                    self.jazoest = match_jazoest.group(1)
                    self.client_revision = match_rev.group(1) if match_rev else "1015919737"
                    return
            
            raise Exception("Không tìm thấy fb_dtsg")
        except Exception as e:
            raise Exception(f"Lỗi init: {str(e)}")

    def get_last_seq_id(self):
        try:
            form_data = {
                "av": self.user_id,
                "__user": self.user_id,
                "fb_dtsg": self.fb_dtsg,
                "jazoest": self.jazoest,
                "__a": "1",
                "__req": "1b",
                "__rev": self.client_revision,
                "queries": json.dumps({
                    "o0": {
                        "doc_id": "3336396659757871",
                        "query_params": {
                            "limit": 20,
                            "before": None,
                            "tags": ["INBOX"],
                            "includeDeliveryReceipts": False,
                            "includeSeqID": True,
                        }
                    }
                }, separators=(",", ":"))
            }
            
            headers = {'Cookie': self.cookie, 'User-Agent': 'Mozilla/5.0'}
            response = requests.post(
                "https://www.facebook.com/api/graphqlbatch/",
                data=form_data,
                headers=headers,
                timeout=10
            )
            
            response_text = response.text
            if response_text.startswith("for(;;);"):
                response_text = response_text[9:]
            
            data = json.loads(response_text.split("\n")[0])
            self.last_seq_id = data["o0"]["data"]["viewer"]["message_threads"]["sync_sequence_id"]
            return True
        except Exception as e:
            console.print(f"[red]❌ Lỗi lấy seq_id: {e}[/]")
            return False

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.mqtt_connected = True
            self.last_activity = time.time()
        else:
            self.mqtt_connected = False

    def on_disconnect(self, client, userdata, rc):
        self.mqtt_connected = False
        if self.should_reconnect and rc != 0:
            self.reconnect_event.set()

    def on_message(self, client, userdata, msg):
        self.last_activity = time.time()

    def on_publish(self, client, userdata, mid):
        self.last_activity = time.time()

    def connect_mqtt(self):
        try:
            if not self.last_seq_id:
                if not self.get_last_seq_id():
                    return False
            
            user = {
                "u": self.user_id,
                "s": self.session_id,
                "chat_on": json.dumps(True, separators=(",", ":")),
                "fg": False,
                "d": generate_client_id(),
                "ct": "websocket",
                "aid": 219994525426954,
                "mqtt_sid": "",
                "cp": 3,
                "ecp": 10,
                "st": ["/t_ms"],
                "pm": [],
                "dc": "",
                "no_auto_fg": True,
                "gas": None,
                "pack": [],
            }

            self.mqtt = mqtt.Client(
                client_id="mqttwsclient",
                clean_session=True,
                protocol=mqtt.MQTTv31,
                transport="websockets",
            )

            self.mqtt.on_connect = self.on_connect
            self.mqtt.on_disconnect = self.on_disconnect
            self.mqtt.on_message = self.on_message
            self.mqtt.on_publish = self.on_publish

            self.mqtt.tls_set(cert_reqs=ssl.CERT_NONE, tls_version=ssl.PROTOCOL_TLSv1_2)
            self.mqtt.username_pw_set(username=json.dumps(user, separators=(",", ":")))
            
            host = "edge-chat.messenger.com"
            path = f"/chat?region=eag&sid={self.session_id}"
            
            self.mqtt.ws_set_options(
                path=path,
                headers={
                    "Cookie": self.cookie,
                    "Origin": "https://www.messenger.com",
                    "User-Agent": "Mozilla/5.0",
                },
            )

            self.mqtt.connect(host, 443, keepalive=60)
            self.mqtt.loop_start()
            
            for _ in range(10):
                if self.mqtt_connected:
                    return True
                time.sleep(0.5)
            
            return False
        except Exception as e:
            return False

    def reconnect_mqtt(self):
        try:
            if self.mqtt:
                try:
                    self.mqtt.loop_stop()
                    self.mqtt.disconnect()
                except:
                    pass
            
            time.sleep(2)
            self.session_id = generate_session_id()
            return self.connect_mqtt()
        except:
            return False

    def ensure_connected(self):
        if not self.mqtt_connected:
            return self.reconnect_mqtt()
        
        if time.time() - self.last_activity > 30:
            return self.reconnect_mqtt()
        
        return True

    def send_typing_mqtt(self, thread_id, is_typing=True):
        if not self.ensure_connected():
            return False
        
        try:
            self.ws_req_number += 1
            
            task_payload = {
                "thread_key": thread_id,
                "is_group_thread": 1,
                "is_typing": 1 if is_typing else 0,
                "attribution": 0,
            }
            
            content = {
                "app_id": "2220391788200892",
                "payload": json.dumps({
                    "label": "3",
                    "payload": json.dumps(task_payload, separators=(",", ":")),
                    "version": "25393437286970779",
                }, separators=(",", ":")),
                "request_id": self.ws_req_number,
                "type": 4,
            }
            
            self.mqtt.publish(
                topic="/ls_req",
                payload=json.dumps(content, separators=(",", ":")),
                qos=1,
                retain=False,
            )
            return True
        except:
            return False

    def send_message_mqtt(self, thread_id, content):
        if not self.ensure_connected():
            return False
        
        try:
            self.ws_req_number += 1
            self.ws_task_number += 1
            
            task_payload = {
                "initiating_source": 0,
                "multitab_env": 0,
                "otid": generate_offline_threading_id(),
                "send_type": 1,
                "skip_url_preview_gen": 0,
                "source": 0,
                "sync_group": 1,
                "text": content,
                "text_has_links": 0,
                "thread_id": int(thread_id),
            }
            
            task = {
                "failure_count": None,
                "label": "46",
                "payload": json.dumps(task_payload, separators=(",", ":")),
                "queue_name": str(thread_id),
                "task_id": self.ws_task_number,
            }
            
            payload_content = {
                "app_id": "2220391788200892",
                "payload": json.dumps({
                    "data_trace_id": None,
                    "epoch_id": int(generate_offline_threading_id()),
                    "tasks": [task],
                    "version_id": "7545284305482586",
                }, separators=(",", ":")),
                "request_id": self.ws_req_number,
                "type": 3,
            }
            
            self.mqtt.publish(
                topic="/ls_req",
                payload=json.dumps(payload_content, separators=(",", ":")),
                qos=1,
                retain=False,
            )
            return True
        except:
            return False

    def get_thread_list(self, limit=100):
        form_data = {
            "av": self.user_id,
            "__user": self.user_id,
            "fb_dtsg": self.fb_dtsg,
            "jazoest": self.jazoest,
            "__a": "1",
            "__req": "1b",
            "queries": json.dumps({
                "o0": {
                    "doc_id": "3336396659757871",
                    "query_params": {
                        "limit": limit,
                        "before": None,
                        "tags": ["INBOX"],
                    }
                }
            })
        }

        headers = {'Cookie': self.cookie, 'User-Agent': 'Mozilla/5.0'}
        try:
            response = requests.post(
                "https://www.facebook.com/api/graphqlbatch/",
                data=form_data,
                headers=headers,
                timeout=15
            )
            data_raw = response.text.split('{"successful_results"')[0]
            data = json.loads(data_raw)
            threads = data["o0"]["data"]["viewer"]["message_threads"]["nodes"]
            
            result = []
            for thread in threads:
                if thread.get("thread_key") and thread["thread_key"].get("thread_fbid"):
                    result.append({
                        "thread_id": thread["thread_key"]["thread_fbid"],
                        "thread_name": thread.get("name") or "Không có tên"
                    })
            return result
        except Exception as e:
            return {"error": str(e)}

    def send_message_http(self, recipient_id, content, list_tag, list_name_tag):
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Cookie': self.cookie,
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://www.facebook.com',
            'Referer': f'https://www.facebook.com/messages/t/{recipient_id}'
        }
        
        ts = str(int(time.time() * 1000))
        
        if list_tag and list_name_tag:
            full_content = content + " @mọi người"
            mention_offset = len(content) + 1
            mention_length = len("@mọi người")
        else:
            full_content = content
        
        payload = {
            "thread_fbid": recipient_id,
            "action_type": "ma-type:user-generated-message",
            "body": full_content,
            "client": "mercury",
            "author": f"fbid:{self.user_id}",
            "timestamp": ts,
            "offline_threading_id": ts,
            "message_id": ts,
            "source": "source:chat:web",
            "fb_dtsg": self.fb_dtsg,
            "jazoest": self.jazoest,
            "__user": self.user_id,
            "__a": '1',
            "__req": '1b',
            "source_tags[0]": "source:chat"
        }
        
        if list_tag and list_name_tag:
            for i in range(len(list_tag)):
                payload[f"profile_xmd[{i}][id]"] = list_tag[i]
                payload[f"profile_xmd[{i}][offset]"] = str(mention_offset)
                payload[f"profile_xmd[{i}][length]"] = str(mention_length)
                payload[f"profile_xmd[{i}][type]"] = "p"
        
        try:
            response = requests.post(
                "https://www.facebook.com/messaging/send/",
                headers=headers,
                data=payload,
                timeout=10
            )
            return "success" if response.status_code == 200 else "failed"
        except:
            return "failed"

    def change_theme_http(self, thread_id, theme_id=None):
        try:
            if not theme_id:
                selected_theme = random.choice(self.THEMES)
                theme_id = selected_theme["id"]
                theme_name = selected_theme["name"]
            else:
                selected_theme = next((t for t in self.THEMES if t["id"] == theme_id), None)
                if not selected_theme:
                    return False, "Theme ID không hợp lệ"
                theme_name = selected_theme["name"]

            form_data = {
                "thread_fbid": str(thread_id),
                "theme_fbid": theme_id,
                "fb_dtsg": self.fb_dtsg,
                "jazoest": self.jazoest,
                "__user": self.user_id,
                "__a": "1",
                "__req": "1",
                "__rev": self.client_revision
            }

            headers = {
                'Cookie': self.cookie,
                'User-Agent': 'Mozilla/5.0',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Origin': 'https://www.facebook.com'
            }

            response = requests.post(
                "https://www.facebook.com/messaging/set_theme/",
                data=form_data,
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                return True, f"Đã đổi theme: {theme_name}"
            return False, "Lỗi HTTP"
        except Exception as e:
            return False, str(e)

    def change_group_name_http(self, thread_id, new_name):
        try:
            message_id = generate_offline_threading_id()
            timestamp = int(time.time() * 1000)
            
            form_data = {
                "client": "mercury",
                "action_type": "ma-type:log-message",
                "author": f"fbid:{self.user_id}",
                "thread_id": str(thread_id),
                "timestamp": timestamp,
                "timestamp_relative": str(int(time.time())),
                "source": "source:chat:web",
                "source_tags[0]": "source:chat",
                "offline_threading_id": message_id,
                "message_id": message_id,
                "threading_id": generate_offline_threading_id(),
                "thread_fbid": str(thread_id),
                "thread_name": str(new_name),
                "log_message_type": "log:thread-name",
                "fb_dtsg": self.fb_dtsg,
                "jazoest": self.jazoest,
                "__user": str(self.user_id),
                "__a": "1",
                "__req": "1",
                "__rev": self.client_revision
            }

            headers = {
                'Cookie': self.cookie,
                'User-Agent': 'Mozilla/5.0',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Origin': 'https://www.facebook.com'
            }

            response = requests.post(
                "https://www.facebook.com/messaging/set_thread_name/",
                data=form_data,
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                return True, f"Đã đổi tên: {new_name}"
            return False, "Lỗi HTTP"
        except Exception as e:
            return False, str(e)

    def create_poll_http(self, thread_id, question, options):
        try:
            form_data = {
                "question_text": question,
                "thread_fbid": str(thread_id),
                "fb_dtsg": self.fb_dtsg,
                "jazoest": self.jazoest,
                "__user": self.user_id,
                "__a": "1",
                "__req": "1",
                "__rev": self.client_revision
            }

            for i, opt in enumerate(options):
                form_data[f"option_text_{i}"] = opt

            headers = {
                'Cookie': self.cookie,
                'User-Agent': 'Mozilla/5.0',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Origin': 'https://www.facebook.com'
            }

            response = requests.post(
                "https://www.facebook.com/messaging/group_polling/create_poll/",
                data=form_data,
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                return True, f"Đã tạo poll: {question}"
            return False, "Lỗi HTTP"
        except Exception as e:
            return False, str(e)

    def cleanup(self):
        self.should_reconnect = False
        if self.mqtt:
            try:
                self.mqtt.loop_stop()
                self.mqtt.disconnect()
            except:
                pass

# ==================== GET GROUP MEMBERS ====================
def get_group_members(messenger, thread_id):
    payload = {
        'queries': json.dumps({
            'o0': {
                'doc_id': '3449967031715030',
                'query_params': {
                    'id': str(thread_id),
                    'message_limit': 0,
                    'load_messages': False,
                    'load_read_receipts': False,
                    'before': None
                }
            }
        }),
        'batch_name': 'MessengerGraphQLThreadFetcher',
        'fb_dtsg': messenger.fb_dtsg,
        'jazoest': messenger.jazoest,
        '__user': messenger.user_id,
        '__a': '1',
    }

    headers = {
        'Cookie': messenger.cookie,
        'User-Agent': 'Mozilla/5.0',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    try:
        response = requests.post(
            'https://www.facebook.com/api/graphqlbatch/',
            headers=headers,
            data=payload,
            timeout=10
        )

        content = response.text.replace('for(;;);', '')
        data = json.loads(content.split('\n')[0])

        thread_data = data.get("o0", {}).get("data", {}).get("message_thread", {})
        all_participants = thread_data.get("all_participants", {}).get("edges", [])
        
        members = []
        for participant in all_participants:
            user = participant.get("node", {}).get("messaging_actor", {})
            members.append({
                "name": user.get("name", "Unknown"),
                "id": user.get("id", "")
            })
        
        return {"success": True, "members": members}
    except Exception as e:
        return {"error": f"Lỗi: {str(e)}"}

# ==================== SPAM FUNCTIONS ====================

def spam_messages(cookie, token, account_name, thread_ids, thread_names, delay, message_lines, use_typing, use_mqtt, tag_mode, tag_ids=None, tag_names=None):
    messenger = None
    try:
        messenger = Messenger(cookie, token)
        
        mqtt_ok = False
        if use_mqtt:
            mqtt_ok = messenger.connect_mqtt()
            if mqtt_ok:
                console.print(f"[bold green]✅ [{account_name}] MQTT connected![/]")
            else:
                console.print(f"[bold yellow]⚠️ [{account_name}] MQTT failed - Dùng HTTP[/]")
        else:
            console.print(f"[bold yellow]⚠️ [{account_name}] Dùng HTTP only[/]")
        
        message_index = 0
        consecutive_fails = 0
        
        while True:
            for thread_id, thread_name in zip(thread_ids, thread_names):
                try:
                    content = message_lines[message_index]
                    
                    # Fake typing
                    if use_typing and mqtt_ok:
                        messenger.send_typing_mqtt(thread_id, True)
                        time.sleep(random.uniform(1, 2))
                    
                    # Gửi tin nhắn
                    if tag_mode and tag_ids:
                        # Có tag @mọi người
                        status = messenger.send_message_http(thread_id, content, tag_ids, tag_names)
                        tag_info = " [cyan][@mọi người][/]"
                    else:
                        # Không tag
                        if mqtt_ok:
                            status = "success" if messenger.send_message_mqtt(thread_id, content) else "failed"
                        else:
                            status = messenger.send_message_http(thread_id, content, None, None)
                        tag_info = ""
                    
                    # Stop typing
                    if use_typing and mqtt_ok:
                        time.sleep(0.3)
                        messenger.send_typing_mqtt(thread_id, False)
                    
                    # Xử lý kết quả
                    if status == "success":
                        consecutive_fails = 0
                        status_icon = "✅"
                    else:
                        consecutive_fails += 1
                        status_icon = "❌"
                        
                        if consecutive_fails >= 5 and mqtt_ok:
                            console.print(f"[yellow]⚠️ [{account_name}] Nhiều lỗi, đang reconnect...[/]")
                            mqtt_ok = messenger.reconnect_mqtt()
                    
                    typing_info = " [yellow][⌨️][/]" if use_typing else ""
                    console.print(f"[bold]{status_icon} [{account_name}][/] → [magenta]{thread_name[:30]}[/]{tag_info}{typing_info}: [white]{content[:40]}[/]")
                    
                    message_index = (message_index + 1) % len(message_lines)
                    actual_delay = delay + random.uniform(-0.5, 0.5)
                    time.sleep(max(1, actual_delay))
                    
                except Exception as e:
                    console.print(f"[yellow]⚠️ [{account_name}] Lỗi: {str(e)[:50]}[/]")
                    time.sleep(2)
                    
    except KeyboardInterrupt:
        pass
    except Exception as e:
        console.print(f"[bold red]❌ Lỗi {account_name}: {str(e)}[/]")
    finally:
        if messenger:
            messenger.cleanup()

def change_theme_loop(cookie, token, account_name, thread_ids, thread_names, delay):
    messenger = None
    try:
        messenger = Messenger(cookie, token)
        console.print(f"[bold green]✅ [{account_name}] Sẵn sàng đổi theme![/]")
        
        theme_index = 0
        
        while True:
            for thread_id, thread_name in zip(thread_ids, thread_names):
                try:
                    theme = messenger.THEMES[theme_index % len(messenger.THEMES)]
                    theme_id = theme["id"]
                    theme_name_str = theme["name"]
                    
                    success, log = messenger.change_theme_http(thread_id, theme_id)
                    
                    if success:
                        console.print(f"[bold green]✅ [{account_name}][/] → [magenta]{thread_name[:30]}[/]: {log}")
                    else:
                        console.print(f"[bold red]❌ [{account_name}][/] → [magenta]{thread_name[:30]}[/]: {log}")
                    
                    theme_index += 1
                    time.sleep(delay)
                    
                except Exception as e:
                    console.print(f"[yellow]⚠️ [{account_name}] Lỗi: {str(e)[:50]}[/]")
                    time.sleep(2)
                    
    except KeyboardInterrupt:
        pass
    except Exception as e:
        console.print(f"[bold red]❌ Lỗi {account_name}: {str(e)}[/]")

def change_name_loop(cookie, token, account_name, thread_ids, thread_names, delay, name_lines):
    messenger = None
    try:
        messenger = Messenger(cookie, token)
        console.print(f"[bold green]✅ [{account_name}] Sẵn sàng nhảy tên![/]")
        
        name_index = 0
        
        while True:
            for thread_id, thread_name in zip(thread_ids, thread_names):
                try:
                    new_name = name_lines[name_index]
                    
                    success, log = messenger.change_group_name_http(thread_id, new_name)
                    
                    if success:
                        console.print(f"[bold green]✅ [{account_name}][/] → [magenta]{thread_name[:30]}[/]: {log}")
                    else:
                        console.print(f"[bold red]❌ [{account_name}][/] → [magenta]{thread_name[:30]}[/]: {log}")
                    
                    name_index = (name_index + 1) % len(name_lines)
                    time.sleep(delay)
                    
                except Exception as e:
                    console.print(f"[yellow]⚠️ [{account_name}] Lỗi: {str(e)[:50]}[/]")
                    time.sleep(2)
                    
    except KeyboardInterrupt:
        pass
    except Exception as e:
        console.print(f"[bold red]❌ Lỗi {account_name}: {str(e)}[/]")

def spam_poll_loop(cookie, token, account_name, thread_ids, thread_names, delay, poll_titles):
    messenger = None
    try:
        messenger = Messenger(cookie, token)
        console.print(f"[bold green]✅ [{account_name}] Sẵn sàng treo poll![/]")
        
        poll_index = 0
        
        while True:
            for thread_id, thread_name in zip(thread_ids, thread_names):
                try:
                    question = poll_titles[poll_index]
                    options = ["Có", "Không", "Có thể"]
                    
                    success, log = messenger.create_poll_http(thread_id, question, options)
                    
                    if success:
                        console.print(f"[bold green]✅ [{account_name}][/] → [magenta]{thread_name[:30]}[/]: {log}")
                    else:
                        console.print(f"[bold red]❌ [{account_name}][/] → [magenta]{thread_name[:30]}[/]: {log}")
                    
                    poll_index = (poll_index + 1) % len(poll_titles)
                    time.sleep(delay)
                    
                except Exception as e:
                    console.print(f"[yellow]⚠️ [{account_name}] Lỗi: {str(e)[:50]}[/]")
                    time.sleep(2)
                    
    except KeyboardInterrupt:
        pass
    except Exception as e:
        console.print(f"[bold red]❌ Lỗi {account_name}: {str(e)}[/]")

# ==================== MAIN FUNCTION ====================
def start_multiple_accounts():
    clear()
    
    console.print(Panel.fit(
        "[bold yellow]🚀 TOOL MESSENGER - BY NGUYỄN HOÀNG GIA BẢO V6 🚀[/]\n" +
        "[green]✨ 5 Chức năng với sub-menu chi tiết[/]",
        border_style="bold blue"
    ))
    
    # Menu chính
    console.print("\n[bold cyan]═══════════ MENU CHÍNH ═══════════[/]")
    console.print("[bold yellow]1.[/] TREO TIN NHẮN")
    console.print("[bold yellow]2.[/] RÉO TAG")
    console.print("[bold yellow]3.[/] ĐỔI THEME (HTTP only)")
    console.print("[bold yellow]4.[/] NHẢY TÊN BOX (HTTP only)")
    console.print("[bold yellow]5.[/] TREO POLL (HTTP only)")
    console.print("[bold cyan]═════════════════════════════════[/]")
    
    try:
        mode = int(Prompt.ask("\n[bold cyan]💠 Chọn chức năng (1-5)[/]", default="1"))
        if mode not in [1, 2, 3, 4, 5]:
            console.print("[red]❌ Chức năng không hợp lệ![/]")
            return
    except:
        console.print("[red]❌ Nhập số nguyên![/]")
        return

    # Sub-menu cho chức năng 1 và 2
    sub_mode = None
    if mode == 1:
        console.print("\n[bold cyan]═══════ SUB-MENU: TREO TIN NHẮN ═══════[/]")
        console.print("[bold yellow]1.[/] Treo @mọi người")
        console.print("[bold yellow]2.[/] Treo bình thường")
        console.print("[bold cyan]═════════════════════════════════════[/]")
        try:
            sub_mode = int(Prompt.ask("\n[bold cyan]💠 Chọn (1-2)[/]", default="2"))
            if sub_mode not in [1, 2]:
                console.print("[red]❌ Lựa chọn không hợp lệ![/]")
                return
        except:
            console.print("[red]❌ Nhập số nguyên![/]")
            return
    
    elif mode == 2:
        console.print("\n[bold cyan]═══════ SUB-MENU: RÉO TAG ═══════[/]")
        console.print("[bold yellow]1.[/] Réo @mọi người")
        console.print("[bold yellow]2.[/] Réo từng người")
        console.print("[bold yellow]3.[/] Réo bình thường")
        console.print("[bold cyan]══════════════════════════════════[/]")
        try:
            sub_mode = int(Prompt.ask("\n[bold cyan]💠 Chọn (1-3)[/]", default="1"))
            if sub_mode not in [1, 2, 3]:
                console.print("[red]❌ Lựa chọn không hợp lệ![/]")
                return
        except:
            console.print("[red]❌ Nhập số nguyên![/]")
            return

    try:
        num_accounts = int(Prompt.ask("\n[bold cyan]💠 Nhập số lượng acc[/]", default="1"))
        if num_accounts < 1:
            console.print("[red]❌ Phải ≥ 1 acc[/]")
            return
    except:
        console.print("[red]❌ Nhập số nguyên![/]")
        return

    processes = []
    
    for i in range(num_accounts):
        console.print(f"\n[bold]{'='*70}[/]")
        console.print(Panel.fit(
            f"[bold yellow]TÀI KHOẢN {i+1}/{num_accounts}[/]",
            border_style="yellow"
        ))
        
        cookie = Prompt.ask("[cyan]🍪 Cookie[/]").strip()
        if not cookie:
            console.print("[yellow]⚠️ Bỏ qua acc này[/]")
            continue
        
        token = Prompt.ask("[cyan]🔑 Token dự phòng (Enter bỏ qua)[/]", default="").strip()
        if not token:
            token = None
        
        with console.status("[bold green]Đang kiểm tra cookie..."):
            cl = check_live(cookie)
        
        if cl["status"] == "success":
            console.print(f"[bold green]✅ {cl['name']} (ID: {cl['user_id']}) - Cookie sống![/]")
        else:
            console.print(f"[bold red]❌ {cl['msg']}[/]")
            if token:
                with console.status("[bold yellow]⏳ Thử chuyển token..."):
                    cookie = token_to_cookie(token)
                if cookie:
                    cl = check_live(cookie)
                    if cl["status"] == "success":
                        console.print(f"[bold green]✅ {cl['name']} - Token OK![/]")
                    else:
                        console.print("[red]❌ Token cũng die![/]")
                        continue
                else:
                    console.print("[red]❌ Không thể chuyển token![/]")
                    continue
            else:
                continue
        
        try:
            messenger = Messenger(cookie, token)
            
            with console.status("[bold cyan]📦 Đang lấy danh sách nhóm..."):
                threads = messenger.get_thread_list(limit=50)
            
            if isinstance(threads, dict) and "error" in threads:
                console.print(f"[red]❌ {threads['error']}[/]")
                continue
            
            if not threads:
                console.print("[yellow]⚠️ Không tìm thấy nhóm nào[/]")
                continue
            
            table = Table(title=f"[bold magenta]DANH SÁCH {len(threads)} NHÓM[/]", border_style="cyan")
            table.add_column("STT", style="yellow", justify="right")
            table.add_column("Tên nhóm", style="cyan")
            table.add_column("ID", style="green")
            
            for idx, thread in enumerate(threads[:20], 1):
                name = thread['thread_name'][:50]
                table.add_row(str(idx), name, thread['thread_id'])
            
            console.print(table)
            
            raw = Prompt.ask("\n[cyan]🔸 Chọn nhóm (VD: 1,3,5 hoặc 1-10)[/]").strip()
            selected = []
            
            for part in raw.split(','):
                if '-' in part:
                    try:
                        start, end = map(int, part.split('-'))
                        selected.extend(range(start, end + 1))
                    except:
                        pass
                else:
                    try:
                        selected.append(int(part.strip()))
                    except:
                        pass
            
            if not selected:
                console.print("[yellow]⚠️ Không chọn nhóm nào![/]")
                continue
            
            selected_ids = [threads[i-1]['thread_id'] for i in selected if 1 <= i <= len(threads)]
            selected_names = [threads[i-1]['thread_name'] for i in selected if 1 <= i <= len(threads)]
            
            console.print(f"[green]✅ Đã chọn {len(selected_ids)} nhóm[/]")
            
            # Xử lý theo từng chức năng
            if mode == 1:  # Treo tin nhắn
                use_typing = Confirm.ask("\n[cyan]⌨️  Có muốn fake typing không?[/]")
                
                file_txt = Prompt.ask("\n[cyan]📂 File tin nhắn (.txt)[/]").strip()
                try:
                    with open(file_txt, 'r', encoding='utf-8') as f:
                        message_lines = [line.strip() for line in f if line.strip()]
                    console.print(f"[green]✅ Đã tải {len(message_lines)} tin nhắn[/]")
                except Exception as e:
                    console.print(f"[red]❌ {e}[/]")
                    continue
                
                try:
                    delay = int(Prompt.ask("[cyan]⏳ Delay (giây)[/]", default="3"))
                    if delay < 2:
                        delay = 2
                except:
                    delay = 3
                
                tag_ids = None
                tag_names = None
                tag_mode = False
                
                if sub_mode == 1:  # Treo @mọi người
                    with console.status("[bold cyan]🔍 Đang lấy danh sách thành viên..."):
                        result = get_group_members(messenger, selected_ids[0])
                    
                    if result.get("success"):
                        members = result["members"]
                        console.print(f"[green]✅ Tìm thấy {len(members)} thành viên[/]")
                        tag_ids = [m['id'] for m in members]
                        tag_names = [m['name'] for m in members]
                        tag_mode = True
                    else:
                        console.print(f"[red]❌ {result.get('error', 'Lỗi lấy thành viên')}[/]")
                        continue
                
                console.print(f"\n[bold green]🚀 Khởi động treo tin nhắn cho {cl['name']}...[/]")
                if sub_mode == 1:
                    console.print("[cyan]👥 Tag @mọi người: ACTIVE[/]")
                console.print("[magenta]📡 MQTT + Fake Typing: ACTIVE[/]")
                
                p = multiprocessing.Process(
                    target=spam_messages,
                    args=(cookie, token, f"Acc{i+1}", selected_ids, selected_names, delay, message_lines, use_typing, True, tag_mode, tag_ids, tag_names)
                )
                processes.append(p)
                p.start()
            
            elif mode == 2:  # Réo tag
                use_typing = Confirm.ask("\n[cyan]⌨️  Có muốn fake typing không?[/]")
                
                file_txt = Prompt.ask("\n[cyan]📂 File tin nhắn (.txt)[/]").strip()
                try:
                    with open(file_txt, 'r', encoding='utf-8') as f:
                        message_lines = [line.strip() for line in f if line.strip()]
                    console.print(f"[green]✅ Đã tải {len(message_lines)} tin nhắn[/]")
                except Exception as e:
                    console.print(f"[red]❌ {e}[/]")
                    continue
                
                try:
                    delay = int(Prompt.ask("[cyan]⏳ Delay (giây)[/]", default="5"))
                    if delay < 3:
                        delay = 3
                except:
                    delay = 5
                
                tag_ids = None
                tag_names = None
                tag_mode = False
                
                if sub_mode in [1, 2]:  # Réo @mọi người hoặc réo từng người
                    with console.status("[bold cyan]🔍 Đang lấy danh sách thành viên..."):
                        result = get_group_members(messenger, selected_ids[0])
                    
                    if result.get("success"):
                        members = result["members"]
                        console.print(f"[green]✅ Tìm thấy {len(members)} thành viên[/]")
                        tag_ids = [m['id'] for m in members]
                        tag_names = [m['name'] for m in members]
                        tag_mode = True
                    else:
                        console.print(f"[red]❌ {result.get('error', 'Lỗi lấy thành viên')}[/]")
                        continue
                
                console.print(f"\n[bold green]🚀 Khởi động réo tag cho {cl['name']}...[/]")
                if sub_mode == 1:
                    console.print("[cyan]👥 Réo @mọi người: ACTIVE[/]")
                elif sub_mode == 2:
                    console.print("[cyan]👤 Réo từng người: ACTIVE[/]")
                console.print("[magenta]📡 MQTT + Fake Typing: ACTIVE[/]")
                
                p = multiprocessing.Process(
                    target=spam_messages,
                    args=(cookie, token, f"Acc{i+1}", selected_ids, selected_names, delay, message_lines, use_typing, True, tag_mode, tag_ids, tag_names)
                )
                processes.append(p)
                p.start()
            
            elif mode == 3:  # Đổi theme
                try:
                    delay = int(Prompt.ask("[cyan]⏳ Delay (giây)[/]", default="3"))
                    if delay < 2:
                        delay = 2
                except:
                    delay = 3
                
                console.print(f"\n[bold green]🚀 Khởi động đổi theme cho {cl['name']}...[/]")
                console.print("[yellow]🎨 HTTP only - không dùng MQTT[/]")
                
                p = multiprocessing.Process(
                    target=change_theme_loop,
                    args=(cookie, token, f"Acc{i+1}", selected_ids, selected_names, delay)
                )
                processes.append(p)
                p.start()
            
            elif mode == 4:  # Nhảy tên
                file_txt = Prompt.ask("\n[cyan]📂 File tên nhóm (.txt)[/]").strip()
                try:
                    with open(file_txt, 'r', encoding='utf-8') as f:
                        name_lines = [line.strip() for line in f if line.strip()]
                    console.print(f"[green]✅ Đã tải {len(name_lines)} tên[/]")
                except Exception as e:
                    console.print(f"[red]❌ {e}[/]")
                    continue
                
                try:
                    delay = int(Prompt.ask("[cyan]⏳ Delay (giây)[/]", default="3"))
                    if delay < 2:
                        delay = 2
                except:
                    delay = 3
                
                console.print(f"\n[bold green]🚀 Khởi động nhảy tên cho {cl['name']}...[/]")
                console.print("[yellow]📝 HTTP only - không dùng MQTT[/]")
                
                p = multiprocessing.Process(
                    target=change_name_loop,
                    args=(cookie, token, f"Acc{i+1}", selected_ids, selected_names, delay, name_lines)
                )
                processes.append(p)
                p.start()
            
            elif mode == 5:  # Treo poll
                file_txt = Prompt.ask("\n[cyan]📂 File câu hỏi poll (.txt)[/]").strip()
                try:
                    with open(file_txt, 'r', encoding='utf-8') as f:
                        poll_titles = [line.strip() for line in f if line.strip()]
                    console.print(f"[green]✅ Đã tải {len(poll_titles)} câu hỏi[/]")
                except Exception as e:
                    console.print(f"[red]❌ {e}[/]")
                    continue
                
                try:
                    delay = int(Prompt.ask("[cyan]⏳ Delay (giây)[/]", default="5"))
                    if delay < 3:
                        delay = 3
                except:
                    delay = 5
                
                console.print(f"\n[bold green]🚀 Khởi động treo poll cho {cl['name']}...[/]")
                console.print("[yellow]📊 HTTP only - không dùng MQTT[/]")
                
                p = multiprocessing.Process(
                    target=spam_poll_loop,
                    args=(cookie, token, f"Acc{i+1}", selected_ids, selected_names, delay, poll_titles)
                )
                processes.append(p)
                p.start()
            
            console.print("[bold green]✅ Started![/]")
            time.sleep(1)
        
        except Exception as e:
            console.print(f"[bold red]❌ Lỗi: {str(e)}[/]")
            continue
    
    if not processes:
        console.print("\n[bold red]❌ Không có acc nào được khởi động![/]")
        return
    
    console.print("\n[bold]" + "="*70 + "[/]")
    
    feature_desc = {
        1: {
            1: "[cyan]📡 Treo tin nhắn + @mọi người[/]",
            2: "[cyan]📡 Treo tin nhắn bình thường[/]"
        },
        2: {
            1: "[cyan]📡 Réo tag @mọi người[/]",
            2: "[cyan]📡 Réo tag từng người[/]",
            3: "[cyan]📡 Réo tag bình thường[/]"
        },
        3: "[yellow]🎨 HTTP only - Đổi theme[/]",
        4: "[yellow]📝 HTTP only - Nhảy tên box[/]",
        5: "[yellow]📊 HTTP only - Treo poll[/]"
    }
    
    if mode in [1, 2]:
        desc = feature_desc[mode][sub_mode]
    else:
        desc = feature_desc[mode]
    
    console.print(Panel.fit(
        "[bold green]✅ TẤT CẢ BOT ĐÃ KHỞI ĐỘNG THÀNH CÔNG[/]\n" +
        desc + "\n" +
        "[magenta]🔐 Token backup: TỰ ĐỘNG CHUYỂN ĐỔI[/]\n" +
        "[green]🛡️  RATE LIMIT SAFE: Delay tối ưu + Random timing[/]\n" +
        "[red]⌨️  Nhấn Ctrl+C để dừng[/]",
        title="[bold yellow]🚀 TOOL ĐANG CHẠY - V6 FIXED[/]",
        border_style="bold green"
    ))
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        console.print("\n\n[bold yellow]👋 Đang dừng tất cả process...[/]")
        for p in processes:
            p.terminate()
            p.join(timeout=3)
        console.print("[bold green]✅ Đã dừng tool! Tạm biệt![/]")

if __name__ == "__main__":
    try:
        start_multiple_accounts()
    except KeyboardInterrupt:
        console.print("\n[bold yellow]👋 Tool đã dừng![/]")
    finally:
        os._exit(0)