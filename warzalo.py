import multiprocessing
import time
import json
import requests
import random
import os
from zlapi import *
from zlapi.models import *
from gtts import gTTS

def print_log(text):
    print(text)

def read_file_content(filename, mode="lines"):
    try:
        with open(filename, "r", encoding="utf-8") as file:
            if mode == "lines":
                return [line.strip() for line in file if line.strip()]
            else:
                return file.read().strip()
    except Exception as e:
        print_log(f"Lỗi đọc file {filename}: {e}")
        return "" if mode == "text" else []

def read_account_file(filename):
    accounts = []
    try:
        with open(filename, "r", encoding="utf-8") as file:
            lines = [line.strip() for line in file if line.strip()]
            if len(lines) % 2 != 0:
                print_log("File tài khoản không hợp lệ, số dòng phải là số chẵn!")
                return []
            for i in range(0, len(lines), 2):
                imei = lines[i]
                try:
                    cookie = eval(lines[i + 1])
                    if not isinstance(cookie, dict):
                        print_log(f"Cookie cho tài khoản {i//2 + 1} không phải dictionary, bỏ qua!")
                        continue
                except:
                    print_log(f"Cookie không hợp lệ cho tài khoản {i//2 + 1}, bỏ qua!")
                    continue
                accounts.append({"imei": imei, "cookie": cookie})
        print_log(f"Tìm thấy {len(accounts)} tài khoản trong file!")
        return accounts
    except Exception as e:
        print_log(f"Lỗi đọc file tài khoản: {e}")
        return []

def parse_selection(input_str, max_index):
    try:
        numbers = [int(i.strip()) for i in input_str.split(',')]
        return [n for n in numbers if 1 <= n <= max_index]
    except:
        print_log("Định dạng không hợp lệ!")
        return []

def get_random_image_from_folder(folder):
    image_files = [f for f in os.listdir(folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    if not image_files:
        return None
    return os.path.join(folder, random.choice(image_files))

def convert_text_to_mp3(text):
    try:
        tts = gTTS(text=text, lang='vi')
        mp3_file = 'voice.mp3'
        tts.save(mp3_file)
        return mp3_file
    except Exception as e:
        print_log(f"Lỗi chuyển văn bản thành giọng nói: {e}")
        return None

def upload_to_host(file_name):
    try:
        with open(file_name, 'rb') as file:
            files = {'files[]': file}
            response = requests.post('https://uguu.se/upload', files=files).json()
            if response['success']:
                return response['files'][0]['url']
        return False
    except Exception as e:
        print_log(f"Lỗi tải file lên: {e}")
        return False

class Bot(ZaloAPI):
    def __init__(self, api_key, secret_key, imei, session_cookies, mode="nhaytag", delay_min=0, delay_max=None, tag_multiple=False, tag_random=False, message_text="", repeat_count=0, image_folder="", sticker_count=0, tagged_users=None, join_link="", accounts=None):
        super().__init__(api_key, secret_key, imei, session_cookies)
        self.mode = mode
        self.delay_min = delay_min
        self.delay_max = delay_max if delay_max is not None else delay_min
        self.tag_multiple = tag_multiple
        self.tag_random = tag_random
        self.message_text = message_text
        self.repeat_count = repeat_count
        self.image_folder = image_folder
        self.sticker_count = sticker_count
        self.tagged_users = tagged_users or {}
        self.join_link = join_link
        self.accounts = accounts or []
        self.message_lines = read_file_content("nhayhoa.txt", mode="lines") if mode in ["nhaytag", "doitennhom", "spamvoice", "spamcard"] else []
        self.call_delay = 0.5 if mode == "spamcall" else 0
        self.running_flags = {}
        self.processes = {}
        self.image_index = {}
        self.tagged_users_internal = {}

    def start_spam(self, thread_id, thread_type, tagged_users=None):
        if self.mode == "nhaytag" and not self.message_lines:
            print_log("File nhayhoa.txt rỗng hoặc không đọc được!")
            return
        if self.mode == "treongon" and not self.message_text:
            print_log("Nội dung spam rỗng!")
            return
        if self.mode == "spamcall" and not tagged_users:
            print_log("Không có thành viên để gọi!")
            return
        if self.mode == "treoanh" and not os.path.isdir(self.image_folder):
            print_log(f"Thư mục ảnh {self.image_folder} không tồn tại!")
            return
        if self.mode in ["doitennhom", "spamvoice", "spamcard"] and not self.message_lines:
            print_log("File nhayhoa.txt rỗng hoặc không đọc được!")
            return
        if self.mode == "doianhnhom" and not os.path.isdir(self.image_folder):
            print_log(f"Thư mục ảnh {self.image_folder} không tồn tại!")
            return
        if self.mode == "spamsticker" and self.sticker_count <= 0:
            print_log("Số lượng sticker phải lớn hơn 0!")
            return
        if self.mode == "spamcard" and not self.tagged_users.get(thread_id):
            print_log("Không có thành viên để spam danh thiếp!")
            return
        if thread_id not in self.running_flags:
            self.running_flags[thread_id] = multiprocessing.Value('b', False)
        if thread_id not in self.processes:
            self.processes[thread_id] = None
        if thread_id not in self.image_index:
            self.image_index[thread_id] = 0
        if thread_id not in self.tagged_users_internal:
            self.tagged_users_internal[thread_id] = tagged_users or []
        if not self.running_flags[thread_id].value:
            initial_message = f""
            self.send(Message(text=initial_message), thread_id, thread_type, ttl=60000)
            self.running_flags[thread_id].value = True
            if self.mode == "nhaytag":
                self.processes[thread_id] = multiprocessing.Process(
                    target=self.spam_messages_with_tag,
                    args=(thread_id, thread_type, self.running_flags[thread_id])
                )
            elif self.mode == "treongon":
                self.processes[thread_id] = multiprocessing.Process(
                    target=self.spam_messages_treongon,
                    args=(thread_id, thread_type, self.running_flags[thread_id])
                )
            elif self.mode == "spamcall":
                for user_id in tagged_users:
                    try:
                        user_info = self.fetchUserInfo(user_id)
                        user_name = user_info.changed_profiles[user_id]['displayName'] if user_info else "Không xác định"
                        start_msg = Message(
                            text=f"Bắt đầu spam call @{user_name}...",
                            mention=MultiMention([Mention(user_id, length=len(f"@{user_name}"), offset=22)])
                        )
                        self.send(start_msg, thread_id=thread_id, thread_type=thread_type)
                    except Exception as e:
                        print_log(f"Lỗi gửi thông báo bắt đầu cho user {user_id}: {e}")
                self.processes[thread_id] = multiprocessing.Process(
                    target=self.spam_call,
                    args=(thread_id, thread_type, self.running_flags[thread_id])
                )
            elif self.mode == "treoanh":
                self.processes[thread_id] = multiprocessing.Process(
                    target=self.spam_images,
                    args=(thread_id, thread_type, self.running_flags[thread_id])
                )
            elif self.mode == "doitennhom":
                self.processes[thread_id] = multiprocessing.Process(
                    target=self.change_group_name,
                    args=(thread_id, thread_type, self.running_flags[thread_id])
                )
            elif self.mode == "doianhnhom":
                self.processes[thread_id] = multiprocessing.Process(
                    target=self.change_group_avatar,
                    args=(thread_id, thread_type, self.running_flags[thread_id])
                )
            elif self.mode == "spamsticker":
                self.processes[thread_id] = multiprocessing.Process(
                    target=self.spam_sticker,
                    args=(thread_id, thread_type, self.running_flags[thread_id])
                )
            elif self.mode == "spamvoice":
                self.processes[thread_id] = multiprocessing.Process(
                    target=self.spam_voice,
                    args=(thread_id, thread_type, self.running_flags[thread_id])
                )
            else:
                self.processes[thread_id] = multiprocessing.Process(
                    target=self.spam_card,
                    args=(thread_id, thread_type, self.running_flags[thread_id])
                )
            self.processes[thread_id].start()

    def spam_messages_with_tag(self, thread_id, thread_type, running_flag):
        user_index = 0
        while running_flag.value and self.tagged_users_internal[thread_id]:
            if not self.message_lines:
                self.message_lines = read_file_content("nhayhoa.txt", mode="lines")
                if not self.message_lines:
                    print_log("File nhayhoa.txt rỗng!")
                    running_flag.value = False
                    break
            raw_msg = random.choice(self.message_lines)
            if self.tag_multiple:
                valid_users = []
                mention_names = []
                users_to_tag = self.tagged_users_internal[thread_id].copy()
                if self.tag_random:
                    random.shuffle(users_to_tag)
                for user_id in users_to_tag:
                    try:
                        user_info = self.fetchUserInfo(user_id)
                        if not user_info or user_id not in user_info.changed_profiles:
                            print_log(f"Thành viên {user_id} không còn trong nhóm, loại bỏ!")
                            continue
                        user_name = user_info.changed_profiles[user_id]['displayName']
                        valid_users.append(user_id)
                        mention_names.append(user_name)
                    except Exception as e:
                        print_log(f"Lỗi lấy thông tin user {user_id}: {e}")
                        continue
                self.tagged_users_internal[thread_id] = valid_users
                if not self.tagged_users_internal[thread_id]:
                    print_log("Không còn thành viên để tag, dừng bot!")
                    running_flag.value = False
                    break
                msg = raw_msg + " "
                mentions = []
                for user_name in mention_names:
                    msg += "@Member "
                final_msg = msg
                for i, user_name in enumerate(mention_names):
                    placeholder = "@Member "
                    final_msg = final_msg.replace(placeholder, f"@{user_name} ", 1)
                    offset = final_msg.find(f"@{user_name}")
                    mentions.append(Mention(valid_users[i], length=len(f"@{user_name}"), offset=offset, auto_format=False))
                try:
                    self.setTyping(thread_id, thread_type)
                    time.sleep(1)
                    message_to_send = Message(text=final_msg.strip(), mention=MultiMention(mentions))
                    self.send(message_to_send, thread_id=thread_id, thread_type=thread_type)
                    print_log(f"Đã gửi tin nhắn tới nhóm {thread_id}: {final_msg[:30]}...")
                except Exception as e:
                    print_log(f"Lỗi gửi tin nhắn: {e}")
                    time.sleep(3)
                    continue
            else:
                if self.tag_random:
                    user_id = random.choice(self.tagged_users_internal[thread_id])
                else:
                    user_id = self.tagged_users_internal[thread_id][user_index]
                try:
                    user_info = self.fetchUserInfo(user_id)
                    if not user_info or user_id not in user_info.changed_profiles:
                        print_log(f"Thành viên {user_id} không còn trong nhóm, loại bỏ!")
                        self.tagged_users_internal[thread_id].remove(user_id)
                        if not self.tagged_users_internal[thread_id]:
                            print_log("Không còn thành viên để tag, dừng bot!")
                            running_flag.value = False
                            break
                        continue
                    user_name = user_info.changed_profiles[user_id]['displayName']
                    msg = f"{raw_msg} @{user_name}"
                    offset_mention = len(raw_msg) + 1
                    mention = Mention(user_id, offset=offset_mention, length=len(f"@{user_name}"))
                    self.setTyping(thread_id, thread_type)
                    time.sleep(0.1)
                    self.send(Message(text=msg, mention=mention), thread_id, thread_type)
                    print_log(f"Đã gửi tin nhắn tới nhóm {thread_id}: {msg[:30]}...")
                except Exception as e:
                    print_log(f"Lỗi gửi tin nhắn: {e}")
                    time.sleep(3)
                    continue
                if not self.tag_random:
                    user_index = (user_index + 1) % len(self.tagged_users_internal[thread_id])
            delay = random.uniform(self.delay_min, self.delay_max)
            print_log(f"Delay {delay:.2f} giây trước tin nhắn tiếp theo")
            time.sleep(delay)

    def spam_messages_treongon(self, thread_id, thread_type, running_flag):
        while running_flag.value:
            mention = Mention("-1", length=len(self.message_text), offset=0)
            try:
                self.setTyping(thread_id, thread_type)
                time.sleep(4)
                self.send(Message(text=self.message_text, mention=mention), thread_id, thread_type)
                print_log(f"Đã gửi tin nhắn tới nhóm {thread_id}!")
            except Exception as e:
                print_log(f"Lỗi gửi tin nhắn: {e}")
            time.sleep(self.delay_min)

    def spam_call(self, thread_id, thread_type, running_flag):
        call_count = {user_id: 0 for user_id in self.tagged_users_internal[thread_id]}
        while running_flag.value and self.tagged_users_internal[thread_id]:
            valid_users = []
            for user_id in self.tagged_users_internal[thread_id]:
                if call_count[user_id] >= self.repeat_count:
                    continue
                try:
                    user_info = self.fetchUserInfo(user_id)
                    if not user_info or user_id not in user_info.changed_profiles:
                        print_log(f"Thành viên {user_id} không còn trong nhóm, loại bỏ!")
                        continue
                    user_name = user_info.changed_profiles[user_id]['displayName']
                    valid_users.append(user_id)
                    call_count[user_id] += 1
                    self.sendCall(user_id)
                    call_msg = Message(
                        text=f"Đã gửi {call_count[user_id]} lần call đến @{user_name}!",
                        mention=MultiMention([Mention(user_id, length=len(f"@{user_name}"), offset=20)])
                    )
                    self.send(call_msg, thread_id=thread_id, thread_type=thread_type)
                    print_log(f"Đã gọi {user_name} (lần {call_count[user_id]}/{self.repeat_count}) trong nhóm {thread_id}")
                    time.sleep(self.call_delay)
                except Exception as e:
                    print_log(f"Lỗi gọi user {user_id}: {e}")
                    time.sleep(3)
                    continue
            self.tagged_users_internal[thread_id] = valid_users
            if not any(call_count[user_id] < self.repeat_count for user_id in self.tagged_users_internal[thread_id]):
                print_log(f"Đã gọi đủ {self.repeat_count} lần cho tất cả thành viên trong nhóm {thread_id}, dừng bot!")
                self.send(Message(text="Đã hoàn tất spam call!"), thread_id, thread_type)
                running_flag.value = False
                break

    def spam_images(self, thread_id, thread_type, running_flag):
        image_files = [f for f in os.listdir(self.image_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        if not image_files:
            print_log("Không tìm thấy ảnh trong thư mục!")
            running_flag.value = False
            return
        while running_flag.value:
            try:
                image_path = os.path.join(self.image_folder, image_files[self.image_index[thread_id]])
                self.setTyping(thread_id, thread_type)
                time.sleep(4)
                self.sendLocalImage(
                    thread_id=thread_id,
                    thread_type=thread_type,
                    message=Message(text=""),
                    imagePath=image_path,
                    width=828,
                    height=1792
                )
                print_log(f"Đã gửi ảnh: {image_path}")
                self.image_index[thread_id] = (self.image_index[thread_id] + 1) % len(image_files)
                time.sleep(self.delay_min)
            except Exception as e:
                print_log(f"Lỗi gửi ảnh: {e}")
                time.sleep(3)

    def change_group_name(self, thread_id, thread_type, running_flag):
        while running_flag.value:
            for content in self.message_lines:
                if not running_flag.value:
                    break
                try:
                    self.changeGroupName(content.strip(), thread_id)
                    print_log(f"Đã đổi tên nhóm thành: {content.strip()}")
                    time.sleep(self.delay_min)
                except Exception as e:
                    print_log(f"Lỗi đổi tên nhóm: {e}")
                    time.sleep(3)

    def change_group_avatar(self, thread_id, thread_type, running_flag):
        for _ in range(self.repeat_count):
            if not running_flag.value:
                break
            try:
                image_path = get_random_image_from_folder(self.image_folder)
                if not image_path:
                    print_log("Không tìm thấy ảnh trong thư mục!")
                    running_flag.value = False
                    break
                self.changeGroupAvatar(groupId=thread_id, filePath=image_path)
                print_log(f"Đã đổi ảnh đại diện nhóm: {image_path}")
                time.sleep(self.delay_min)
            except Exception as e:
                print_log(f"Lỗi đổi ảnh đại diện: {e}")
                time.sleep(3)
        print_log(f"Hoàn thành đổi ảnh đại diện {self.repeat_count} lần!")
        running_flag.value = False

    def spam_sticker(self, thread_id, thread_type, running_flag):
        sticker_type = 3
        sticker_id = "23339"
        category_id = "10425"
        for _ in range(self.sticker_count):
            if not running_flag.value:
                break
            try:
                response = self.sendSticker(sticker_type, sticker_id, category_id, thread_id, thread_type)
                if not response:
                    print_log("Không thể gửi sticker!")
                    time.sleep(3)
                    continue
                print_log("Đã gửi một sticker!")
                time.sleep(self.delay_min)
            except Exception as e:
                print_log(f"Lỗi gửi sticker: {e}")
                time.sleep(3)
        print_log("Hoàn thành spam sticker!")
        running_flag.value = False

    def spam_voice(self, thread_id, thread_type, running_flag):
        while running_flag.value:
            for message in self.message_lines:
                if not running_flag.value:
                    break
                try:
                    self.setTyping(thread_id, thread_type)
                    time.sleep(4)
                    mp3_file = convert_text_to_mp3(message)
                    if mp3_file:
                        voice_url = upload_to_host(mp3_file)
                        if voice_url:
                            file_size = os.path.getsize(mp3_file)
                            self.sendRemoteVoice(voice_url, thread_id, fileSize=file_size, thread_type=thread_type)
                            print_log(f"Đã gửi voice: {message[:30]}...")
                        else:
                            print_log("Lỗi upload voice!")
                    else:
                        print_log("Lỗi tạo voice!")
                    time.sleep(self.delay_min)
                except Exception as e:
                    print_log(f"Lỗi gửi voice: {e}")
                    time.sleep(3)

    def spam_card(self, thread_id, thread_type, running_flag):
        while running_flag.value:
            for user_id in self.tagged_users.get(thread_id, []):
                if not running_flag.value:
                    break
                for content in self.message_lines:
                    if not running_flag.value:
                        break
                    try:
                        self.setTyping(thread_id, thread_type)
                        time.sleep(4)
                        user_info = self.fetchUserInfo(user_id).changed_profiles.get(user_id)
                        avatar_url = user_info.get('avatar') if user_info else None
                        if not avatar_url:
                            print_log(f"Không tìm thấy ảnh đại diện của user {user_id}!")
                            continue
                        self.sendBusinessCard(
                            userId=user_id,
                            phone=content.strip(),
                            qrCodeUrl=avatar_url,
                            thread_id=thread_id,
                            thread_type=thread_type
                        )
                        print_log(f"Đã gửi danh thiếp: {content[:30]}...")
                        time.sleep(self.delay_min)
                    except Exception as e:
                        print_log(f"Lỗi gửi danh thiếp: {e}")
                        time.sleep(3)

    def join_group(self, running_flag):
        error_messages = {
            0: "Tham gia nhóm thành công!",
            240: "Duyệt bé vào nhóm ngay đây..!",
            178: "Bé đã là thành viên rồi..!",
            227: "Nhóm hoặc link không tồn tại!",
            175: "Bé bị Block rồi, thật đáng tiếc..!",
            1003: "Full Members rồi, em xin lỗi!",
            1004: "Giới hạn thành viên kìaa rồi!",
            1022: "Đã yêu cầu tham gia trước đó rồi anh"
        }
        for idx, account in enumerate(self.accounts, 1):
            if not running_flag.value:
                break
            try:
                client = ZaloAPI('api_key', 'secret_key', account['imei'], account['cookie'])
                join_result = client.joinGroup(self.join_link)
                if join_result:
                    if isinstance(join_result, dict) and 'error_code' in join_result:
                        error_code = join_result['error_code']
                        msg = error_messages.get(error_code, "Lỗi, thử lại sau nhé!")
                    else:
                        msg = "Lỗi không xác định!"
                else:
                    msg = "Lỗi không xác định!"
                print_log(f"Tài khoản {idx}: {msg}")
                time.sleep(self.delay_min)
            except ZaloAPIException as e:
                print_log(f"Tài khoản {idx}: Lỗi tham gia: {e}")
                time.sleep(3)
            except Exception as e:
                print_log(f"Tài khoản {idx}: Lỗi không xác định: {e}")
                time.sleep(3)

    def onMessage(self, *args, **kwargs):
        pass

    def onEvent(self, *args, **kwargs):
        pass

    def onAdminMessage(self, *args, **kwargs):
        pass

    def fetch_groups(self):
        try:
            all_groups = self.fetchAllGroups()
            group_list = []
            for group_id, _ in all_groups.gridVerMap.items():
                group_info = self.fetchGroupInfo(group_id)
                group_name = group_info.gridInfoMap[group_id]["name"]
                group_list.append({
                    'id': group_id,
                    'name': group_name
                })
            return type('GroupObj', (), {'groups': [type('GroupItem', (), {'grid': g['id'], 'name': g['name']})() for g in group_list]})()
        except AttributeError as e:
            print_log(f"Lỗi: Phương thức hoặc thuộc tính không tồn tại: {e}")
            return None
        except ZaloAPIException as e:
            print_log(f"Lỗi API Zalo: {e}")
            return None
        except Exception as e:
            print_log(f"Lỗi không xác định khi lấy danh sách nhóm: {e}")
            return None

    def fetchGroupInfo(self, group_id):
        try:
            return super().fetchGroupInfo(group_id)
        except ZaloAPIException as e:
            print_log(f"Lỗi API Zalo khi lấy thông tin nhóm {group_id}: {e}")
            return None
        except Exception as e:
            print_log(f"Lỗi khi lấy thông tin nhóm {group_id}: {e}")
            return None

    def fetchGroupMembers(self, group_id):
        try:
            group_info = self.fetchGroupInfo(group_id)
            if not group_info or not hasattr(group_info, 'gridInfoMap') or group_id not in group_info.gridInfoMap:
                print_log(f"Không lấy được thông tin nhóm {group_id}")
                return []
            mem_ver_list = group_info.gridInfoMap[group_id]["memVerList"]
            member_ids = [mem.split("_")[0] for mem in mem_ver_list]
            members = []
            for user_id in member_ids:
                try:
                    user_info = self.fetchUserInfo(user_id)
                    user_data = user_info.changed_profiles[user_id]
                    members.append({
                        'id': user_data['userId'],
                        'name': user_data['displayName']
                    })
                except Exception as e:
                    print_log(f"Lỗi lấy thông tin user {user_id}: {e}")
                    members.append({
                        'id': user_id,
                        'name': f"[Lỗi: {user_id}]"
                    })
            return members
        except Exception as e:
            print_log(f"Lỗi lấy danh sách thành viên: {e}")
            return []

def start_bot_nhaytag(api_key, secret_key, imei, session_cookies, delay_min, delay_max, tag_multiple, tag_random, group_ids, tagged_users):
    bot = Bot(api_key, secret_key, imei, session_cookies, mode="nhaytag", delay_min=delay_min, delay_max=delay_max, tag_multiple=tag_multiple, tag_random=tag_random, tagged_users=tagged_users)
    for group_id in group_ids:
        print_log(f"Bắt đầu nhây tag nhóm {group_id}")
        bot.start_spam(group_id, ThreadType.GROUP, tagged_users.get(group_id, []))
    bot.listen(run_forever=True, thread=False, delay=1, type='requests')

def start_bot_treongon(api_key, secret_key, imei, session_cookies, message_text, delay, group_ids):
    bot = Bot(api_key, secret_key, imei, session_cookies, mode="treongon", delay_min=delay, message_text=message_text)
    for group_id in group_ids:
        print_log(f"Bắt đầu treo ngôn nhóm {group_id}")
        bot.start_spam(group_id, ThreadType.GROUP)
    bot.listen(run_forever=True, thread=False, delay=1, type='requests')

def start_bot_spamcall(api_key, secret_key, imei, session_cookies, group_ids, tagged_users, repeat_count):
    bot = Bot(api_key, secret_key, imei, session_cookies, mode="spamcall", repeat_count=repeat_count, tagged_users=tagged_users)
    for group_id in group_ids:
        print_log(f"Bắt đầu spam call nhóm {group_id}")
        bot.start_spam(group_id, ThreadType.GROUP, tagged_users.get(group_id, []))
    bot.listen(run_forever=True, thread=False, delay=1, type='requests')
    return True  

def start_bot_treoanh(api_key, secret_key, imei, session_cookies, image_folder, delay, group_ids):
    bot = Bot(api_key, secret_key, imei, session_cookies, mode="treoanh", delay_min=delay, image_folder=image_folder)
    for group_id in group_ids:
        print_log(f"Bắt đầu treo ảnh nhóm {group_id}")
        bot.start_spam(group_id, ThreadType.GROUP)
    bot.listen(run_forever=True, thread=False, delay=1, type='requests')

def start_bot_doitennhom(api_key, secret_key, imei, session_cookies, delay, group_ids):
    bot = Bot(api_key, secret_key, imei, session_cookies, mode="doitennhom", delay_min=delay)
    for group_id in group_ids:
        print_log(f"Bắt đầu đổi tên nhóm {group_id}")
        bot.start_spam(group_id, ThreadType.GROUP)
    bot.listen(run_forever=True, thread=False, delay=1, type='requests')

def start_bot_doianhnhom(api_key, secret_key, imei, session_cookies, image_folder, repeat_count, delay, group_ids):
    bot = Bot(api_key, secret_key, imei, session_cookies, mode="doianhnhom", image_folder=image_folder, repeat_count=repeat_count, delay_min=delay)
    for group_id in group_ids:
        print_log(f"Bắt đầu đổi avatar nhóm {group_id}")
        bot.start_spam(group_id, ThreadType.GROUP)
    bot.listen(run_forever=True, thread=False, delay=1, type='requests')

def start_bot_spamsticker(api_key, secret_key, imei, session_cookies, sticker_count, delay, group_ids):
    bot = Bot(api_key, secret_key, imei, session_cookies, mode="spamsticker", sticker_count=sticker_count, delay_min=delay)
    for group_id in group_ids:
        print_log(f"Bắt đầu spam sticker nhóm {group_id}")
        bot.start_spam(group_id, ThreadType.GROUP)
    bot.listen(run_forever=True, thread=False, delay=1, type='requests')

def start_bot_spamvoice(api_key, secret_key, imei, session_cookies, delay, group_ids):
    bot = Bot(api_key, secret_key, imei, session_cookies, mode="spamvoice", delay_min=delay)
    for group_id in group_ids:
        print_log(f"Bắt đầu spam voice nhóm {group_id}")
        bot.start_spam(group_id, ThreadType.GROUP)
    bot.listen(run_forever=True, thread=False, delay=1, type='requests')

def start_bot_spamcard(api_key, secret_key, imei, session_cookies, delay, group_ids, tagged_users):
    bot = Bot(api_key, secret_key, imei, session_cookies, mode="spamcard", delay_min=delay, tagged_users=tagged_users)
    for group_id in group_ids:
        print_log(f"Bắt đầu spam danh thiếp nhóm {group_id}")
        bot.start_spam(group_id, ThreadType.GROUP)
    bot.listen(run_forever=True, thread=False, delay=1, type='requests')

def start_bot_join(api_key, secret_key, accounts, delay, join_link):
    running_flag = multiprocessing.Value('b', True)
    bot = Bot(api_key, secret_key, '', {}, mode="join", delay_min=delay, join_link=join_link, accounts=accounts)
    print_log(f"Bắt đầu join nhóm với {len(accounts)} tài khoản")
    process = multiprocessing.Process(
        target=bot.join_group,
        args=(running_flag,)
    )
    process.start()
    process.join()  
    return True  

def start_multiple_accounts():
    while True:
        print_log("""
⢸⠉⣹⠋⠉⢉⡟⢩⢋⠋⣽⡻⠭⢽⢉⠯⠭⠭⠭⢽⡍⢹⡍⠙⣯⠉⠉⠉⠉⠉⣿⢫⠉⠉⠉⢉⡟⠉⢿⢹⠉⢉⣉⢿⡝⡉⢩⢿⣻⢍⠉⠉⠩⢹⣟⡏⠉⠹⡉⢻⡍⡇
⢸⢠⢹⠀⠀⢸⠁⣼⠀⣼⡝⠀⠀⢸⠘⠀⠀⠀⠀⠈⢿⠀⡟⡄⠹⣣⠀⠀⠐⠀⢸⡘⡄⣤⠀⡼⠁⠀⢺⡘⠉⠀⠀⠀⠫⣪⣌⡌⢳⡻⣦⠀⠀⢃⡽⡼⡀⠀⢣⢸⠸⡇
⢸⡸⢸⠀⠀⣿⠀⣇⢠⡿⠀⠀⠀⠸⡇⠀⠀⠀⠀⠀⠘⢇⠸⠘⡀⠻⣇⠀⠀⠄⠀⡇⢣⢛⠀⡇⠀⠀⣸⠇⠀⠀⠀⠀⠀⠘⠄⢻⡀⠻⣻⣧⠀⠀⠃⢧⡇⠀⢸⢸⡇⡇
⢸⡇⢸⣠⠀⣿⢠⣿⡾⠁⠀⢀⡀⠤⢇⣀⣐⣀⠀⠤⢀⠈⠢⡡⡈⢦⡙⣷⡀⠀⠀⢿⠈⢻⣡⠁⠀⢀⠏⠀⠀⠀⢀⠀⠄⣀⣐⣀⣙⠢⡌⣻⣷⡀⢹⢸⡅⠀⢸⠸⡇⡇
⢸⡇⢸⣟⠀⢿⢸⡿⠀⣀⣶⣷⣾⡿⠿⣿⣿⣿⣿⣿⣶⣬⡀⠐⠰⣄⠙⠪⣻⣦⡀⠘⣧⠀⠙⠄⠀⠀⠀⠀⠀⣨⣴⣾⣿⠿⣿⣿⣿⣿⣿⣶⣯⣿⣼⢼⡇⠀⢸⡇⡇⠇
⢸⢧⠀⣿⡅⢸⣼⡷⣾⣿⡟⠋⣿⠓⢲⣿⣿⣿⡟⠙⣿⠛⢯⡳⡀⠈⠓⠄⡈⠚⠿⣧⣌⢧⠀⠀⠀⠀⠀⣠⣺⠟⢫⡿⠓⢺⣿⣿⣿⠏⠙⣏⠛⣿⣿⣾⡇⢀⡿⢠⠀⡇
⢸⢸⠀⢹⣷⡀⢿⡁⠀⠻⣇⠀⣇⠀⠘⣿⣿⡿⠁⠐⣉⡀⠀⠁⠀⠀⠀⠀⠀⠀⠀⠀⠉⠓⠳⠄⠀⠀⠀⠀⠋⠀⠘⡇⠀⠸⣿⣿⠟⠀⢈⣉⢠⡿⠁⣼⠁⣼⠃⣼⠀⡇
⢸⠸⣀⠈⣯⢳⡘⣇⠀⠀⠈⡂⣜⣆⡀⠀⠀⢀⣀⡴⠇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢽⣆⣀⠀⠀⠀⣀⣜⠕⡊⠀⣸⠇⣼⡟⢠⠏⠀⡇
⢸⠀⡟⠀⢸⡆⢹⡜⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⠋⣾⡏⡇⡎⡇⠀⡇
⢸⠀⢃⡆⠀⢿⡄⠑⢽⣄⠀⠀⠀⢀⠂⠠⢁⠈⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠠⠂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀⠀⠄⡐⢀⠂⠀⠀⣠⣮⡟⢹⣯⣸⣱⠁⠀⡇
⠈⠉⠉⠉⠉⠉⠉⠉⠉⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠉⠉⠉⠉⠉⠉⠉⠉⠁
╔════════════════════════════════════════════════════╗
║                                                    ║
║     ZALO BOT - Admin: Nguyen hoang gia bao            ║
║     Ngày cập nhật: 01/10/2026                      ║
║                                                    ║
╚════════════════════════════════════════════════════╝
        """)
        
        
        print_log("""
╔═══════ MENU CHỨC NĂNG ═══════╗
║ 1. Nhây Tag                  ║
║ 2. Treo Ngôn                 ║
║ 3. Spam Call                 ║
║ 4. Treo Ảnh                  ║
║ 5. Đổi Tên Nhóm              ║
║ 6. Đổi Avatar Nhóm           ║
║ 7. Spam Sticker              ║
║ 8. Spam Voice                ║
║ 9. Spam Danh Thiếp           ║
║ 10. Join Nhóm                ║
╚══════════════════════════════╝
        """)
        
        try:
            num_accounts = int(input("Nhập số lượng tài khoản Zalo muốn chạy (trừ chế độ Join): "))
        except ValueError:
            print_log("Nhập sai, phải là số nguyên!")
            return
        processes = []
        restart_required = False
        for i in range(num_accounts):
            print(f"\nNhập thông tin cho tài khoản {i+1}")
            try:
                while True:
                    mode = input("Chọn chế độ: 1 (Nhây Tag), 2 (Treo Ngôn), 3 (Spam Call), 4 (Treo Ảnh), 5 (Đổi Tên Nhóm), 6 (Đổi Avatar Nhóm), 7 (Spam Sticker), 8 (Spam Voice), 9 (Spam Danh Thiếp), 10 (Join): ")
                    if mode in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']:
                        break
                    print_log("Vui lòng nhập 1, 2, 3, 4, 5, 6, 7, 8, 9 hoặc 10!")
                if mode == '10':  
                    account_file = input("Nhập tên file .txt chứa IMEI và cookie: ")
                    accounts = read_account_file(account_file)
                    if not accounts:
                        print_log("Không có tài khoản hợp lệ, bỏ qua chế độ Join!")
                        continue
                    while True:
                        try:
                            delay = float(input("Nhập delay giữa các lần join (giây): "))
                            if delay < 0:
                                print_log("Delay phải không âm!")
                                continue
                            break
                        except ValueError:
                            print_log("Delay phải là số!")
                    join_link = input("Nhập link nhóm Zalo (https://zalo.me/...): ")
                    if not join_link.startswith("https://zalo.me/"):
                        print_log("Link không hợp lệ, phải bắt đầu bằng https://zalo.me/!")
                        continue
                    restart_required = start_bot_join('api_key', 'secret_key', accounts, delay, join_link)
                    break  
                imei = input("Nhập IMEI của Zalo: ")
                cookie_str = input("Nhập Cookie: ")
                try:
                    session_cookies = eval(cookie_str)
                    if not isinstance(session_cookies, dict):
                        print_log("Cookie phải là dictionary!")
                        continue
                except:
                    print_log("Cookie không hợp lệ, dùng dạng {'key': 'value'}!")
                    continue
                bot = Bot('api_key', 'secret_key', imei, session_cookies, mode="nhaytag" if mode == '1' else "treongon" if mode == '2' else "spamcall" if mode == '3' else "treoanh" if mode == '4' else "doitennhom" if mode == '5' else "doianhnhom" if mode == '6' else "spamsticker" if mode == '7' else "spamvoice" if mode == '8' else "spamcard")
                groups = bot.fetch_groups()
                if not groups or not hasattr(groups, 'groups') or not groups.groups:
                    print_log("Không lấy được nhóm nào!")
                    continue
                print("Danh sách nhóm:")
                for idx, group in enumerate(groups.groups, 1):
                    print(f"{idx}. {group.name} ({group.grid})")
                raw = input("Nhập số nhóm muốn chạy (VD: 1,3): ")
                selected = parse_selection(raw, len(groups.groups))
                if not selected:
                    print_log("Không chọn nhóm nào!")
                    continue
                selected_ids = [groups.groups[i - 1].grid for i in selected]
                if mode == '1':  
                    delay_type = input("Delay cố định hay random? (Y/N): ").lower()
                    if delay_type == 'y':
                        while True:
                            try:
                                delay_min = float(input("Nhập delay ít nhất (giây): "))
                                if delay_min < 0:
                                    print_log("Delay min phải không âm!")
                                    continue
                                break
                            except ValueError:
                                print_log("Delay min phải là số!")
                        while True:
                            try:
                                delay_max = float(input("Nhập delay nhiều nhất (giây): "))
                                if delay_max < delay_min:
                                    print_log("Delay max phải lớn hơn hoặc bằng delay min!")
                                    continue
                                break
                            except ValueError:
                                print_log("Delay max phải là số!")
                    else:
                        while True:
                            try:
                                delay_min = float(input("Nhập delay cố định (giây): "))
                                if delay_min < 0:
                                    print_log("Delay phải không âm!")
                                    continue
                                break
                            except ValueError:
                                print_log("Delay phải là số!")
                        delay_max = delay_min
                    tag_multiple = input("Tag nhiều người trong 1 tin nhắn hay từng người? (Y/N): ").lower() == 'y'
                    tag_random = input("Réo ngẫu nhiên hay theo thứ tự? (Y/N): ").lower() == 'y'
                    tagged_users = {}
                    for group_id in selected_ids:
                        members = bot.fetchGroupMembers(group_id)
                        if not members:
                            print_log(f"Nhóm {group_id} không có thành viên!")
                            continue
                        print(f"Thành viên nhóm {group_id}:")
                        for idx, member in enumerate(members, 1):
                            print(f"{idx}. {member['name']} ({member['id']})")
                        raw = input("Nhập số thứ tự thành viên để tag (VD: 1,2,3, 0 để không tag): ")
                        if raw.strip() == "0":
                            tagged_users[group_id] = []
                        else:
                            selected_members = parse_selection(raw, len(members))
                            tagged_users[group_id] = [members[i - 1]['id'] for i in selected_members]
                    p = multiprocessing.Process(
                        target=start_bot_nhaytag,
                        args=('api_key', 'secret_key', imei, session_cookies, delay_min, delay_max, tag_multiple, tag_random, selected_ids, tagged_users)
                    )
                elif mode == '2':  
                    file_txt = input("Nhập tên file .txt chứa nội dung spam: ")
                    message_text = read_file_content(file_txt, mode="text")
                    if not message_text:
                        print_log("File rỗng hoặc không đọc được!")
                        continue
                    while True:
                        try:
                            delay = float(input("Nhập delay giữa các lần gửi (giây): "))
                            if delay < 0:
                                print_log("Delay phải không âm!")
                                continue
                            break
                        except ValueError:
                            print_log("Delay phải là số!")
                    p = multiprocessing.Process(
                        target=start_bot_treongon,
                        args=('api_key', 'secret_key', imei, session_cookies, message_text, delay, selected_ids)
                    )
                elif mode == '3':  
                    while True:
                        try:
                            repeat_count = int(input("Nhập số lần gọi cho mỗi thành viên: "))
                            if repeat_count <= 0:
                                print_log("Số lần gọi phải là số nguyên dương!")
                                continue
                            break
                        except ValueError:
                            print_log("Số lần gọi phải là số nguyên!")
                    tagged_users = {}
                    for group_id in selected_ids:
                        members = bot.fetchGroupMembers(group_id)
                        if not members:
                            print_log(f"Nhóm {group_id} không có thành viên!")
                            continue
                        print(f"Thành viên nhóm {group_id}:")
                        for idx, member in enumerate(members, 1):
                            print(f"{idx}. {member['name']} ({member['id']})")
                        raw = input("Nhập số thứ tự thành viên để gọi (VD: 1,2,3, 0 để không gọi): ")
                        if raw.strip() == "0":
                            tagged_users[group_id] = []
                        else:
                            selected_members = parse_selection(raw, len(members))
                            tagged_users[group_id] = [members[i - 1]['id'] for i in selected_members]
                    p = multiprocessing.Process(
                        target=start_bot_spamcall,
                        args=('api_key', 'secret_key', imei, session_cookies, selected_ids, tagged_users, repeat_count)
                    )
                    restart_required = True
                elif mode == '4':  
                    image_folder = input("Nhập đường dẫn thư mục chứa ảnh: ")
                    if not os.path.isdir(image_folder):
                        print_log("Thư mục không tồn tại!")
                        continue
                    while True:
                        try:
                            delay = float(input("Nhập delay giữa các lần gửi (giây): "))
                            if delay < 0:
                                print_log("Delay phải không âm!")
                                continue
                            break
                        except ValueError:
                            print_log("Delay phải là số!")
                    p = multiprocessing.Process(
                        target=start_bot_treoanh,
                        args=('api_key', 'secret_key', imei, session_cookies, image_folder, delay, selected_ids)
                    )
                elif mode == '5':  
                    while True:
                        try:
                            delay = float(input("Nhập delay giữa các lần đổi tên (giây): "))
                            if delay < 0:
                                print_log("Delay phải không âm!")
                                continue
                            break
                        except ValueError:
                            print_log("Delay phải là số!")
                    p = multiprocessing.Process(
                        target=start_bot_doitennhom,
                        args=('api_key', 'secret_key', imei, session_cookies, delay, selected_ids)
                    )
                elif mode == '6':  
                    image_folder = input("Nhập đường dẫn thư mục chứa ảnh: ")
                    if not os.path.isdir(image_folder):
                        print_log("Thư mục không tồn tại!")
                        continue
                    while True:
                        try:
                            repeat_count = int(input("Nhập số lần đổi avatar: "))
                            if repeat_count <= 0:
                                print_log("Số lần phải là số nguyên dương!")
                                continue
                            break
                        except ValueError:
                            print_log("Số lần phải là số nguyên!")
                    while True:
                        try:
                            delay = float(input("Nhập delay giữa các lần đổi (giây): "))
                            if delay < 0:
                                print_log("Delay phải không âm!")
                                continue
                            break
                        except ValueError:
                            print_log("Delay phải là số!")
                    p = multiprocessing.Process(
                        target=start_bot_doianhnhom,
                        args=('api_key', 'secret_key', imei, session_cookies, image_folder, repeat_count, delay, selected_ids)
                    )
                elif mode == '7':  
                    while True:
                        try:
                            sticker_count = int(input("Nhập số lượng sticker muốn spam: "))
                            if sticker_count <= 0:
                                print_log("Số lượng phải là số nguyên dương!")
                                continue
                            break
                        except ValueError:
                            print_log("Số lượng phải là số nguyên!")
                    while True:
                        try:
                            delay = float(input("Nhập delay giữa các lần gửi (giây): "))
                            if delay < 0:
                                print_log("Delay phải không âm!")
                                continue
                            break
                        except ValueError:
                            print_log("Delay phải là số!")
                    p = multiprocessing.Process(
                        target=start_bot_spamsticker,
                        args=('api_key', 'secret_key', imei, session_cookies, sticker_count, delay, selected_ids)
                    )
                elif mode == '8':  
                    while True:
                        try:
                            delay = float(input("Nhập delay giữa các lần gửi (giây): "))
                            if delay < 0:
                                print_log("Delay phải không âm!")
                                continue
                            break
                        except ValueError:
                            print_log("Delay phải là số!")
                    p = multiprocessing.Process(
                        target=start_bot_spamvoice,
                        args=('api_key', 'secret_key', imei, session_cookies, delay, selected_ids)
                    )
                else:  
                    while True:
                        try:
                            delay = float(input("Nhập delay giữa các lần gửi (giây): "))
                            if delay < 0:
                                print_log("Delay phải không âm!")
                                continue
                            break
                        except ValueError:
                            print_log("Delay phải là số!")
                    tagged_users = {}
                    for group_id in selected_ids:
                        members = bot.fetchGroupMembers(group_id)
                        if not members:
                            print_log(f"Nhóm {group_id} không có thành viên!")
                            continue
                        print(f"Thành viên nhóm {group_id}:")
                        for idx, member in enumerate(members, 1):
                            print(f"{idx}. {member['name']} ({member['id']})")
                        raw = input("Nhập số thứ tự thành viên để spam danh thiếp (VD: 1,2,3): ")
                        selected_members = parse_selection(raw, len(members))
                        if not selected_members:
                            print_log("Không chọn thành viên nào!")
                            continue
                        tagged_users[group_id] = [members[i - 1]['id'] for i in selected_members]
                    p = multiprocessing.Process(
                        target=start_bot_spamcard,
                        args=('api_key', 'secret_key', imei, session_cookies, delay, selected_ids, tagged_users)
                    )
                processes.append(p)
                p.start()
            except Exception as e:
                print_log(f"Lỗi nhập liệu: {e}")
                continue
        print_log("\nTẤT CẢ BOT ĐÃ KHỞI ĐỘNG THÀNH CÔNG")
        if restart_required:
            while True:
                restart = input("Bạn muốn dùng lại tool? (Y/N): ").lower()
                if restart in ['y', 'n']:
                    break
                print_log("Vui lòng nhập Y hoặc N!")
            if restart == 'y':
                continue
            else:
                print_log("\nChào tạm biệt! Cảm ơn bạn đã sử dụng tool của Nguyen hoang gia bao!")
                break
        break

if __name__ == "__main__":
    start_multiple_accounts()