import os
import requests
import asyncio
from time import sleep
from colorama import Fore, Style, init
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt

init(autoreset=True)
console = Console()

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    banner = """
[bold cyan]
┈┈┈┈╱▔▔▔▔╲┈┈┈┈
┈┈┈▕▕╲┊┊╱▏▏┈┈┈
┈┈┈▕▕▂╱╲▂▏▏┈┈┈
┈┈┈┈╲┊┊┊┊╱┈┈┈┈
┈┈┈┈▕╲▂▂╱▏┈┈┈┈
╱▔▔▔▔┊┊┊┊▔▔▔▔╲

[bold magenta]DISCORD  TOOL - Ngbao
[bold white]By Nguyen Hoang gia bao
    """
    console.print(Panel(banner, border_style="bold blue"))

class DiscordAPI:
    def __init__(self, token):
        self.token = token
        self.headers = {
            "Authorization": token,
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    
    def check_token(self):
        try:
            response = requests.get(
                "https://discord.com/api/v9/users/@me",
                headers=self.headers,
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                return True, data.get("username", "Unknown"), data.get("id", "Unknown")
            else:
                return False, None, None
        except Exception as e:
            console.print(f"[red]Lỗi kiểm tra token: {e}[/]")
            return False, None, None
    
    def get_guilds(self):
        try:
            response = requests.get(
                "https://discord.com/api/v9/users/@me/guilds",
                headers=self.headers,
                timeout=10
            )
            if response.status_code == 200:
                return response.json()
            else:
                console.print(f"[yellow]Lỗi lấy guilds: {response.status_code}[/]")
                return []
        except Exception as e:
            console.print(f"[red]Exception lấy guilds: {e}[/]")
            return []
    
    def get_channels(self, guild_id):
        try:
            response = requests.get(
                f"https://discord.com/api/v9/guilds/{guild_id}/channels",
                headers=self.headers,
                timeout=10
            )
            if response.status_code == 200:
                return response.json()
            else:
                return []
        except Exception as e:
            console.print(f"[red]Exception lấy channels: {e}[/]")
            return []
    
    def get_guild_members(self, guild_id, limit=1000):
        try:
            members = []
            after = 0
            
            while len(members) < limit:
                response = requests.get(
                    f"https://discord.com/api/v9/guilds/{guild_id}/members?limit=1000&after={after}",
                    headers=self.headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    batch = response.json()
                    if not batch:
                        break
                    
                    members.extend(batch)
                    after = batch[-1]['user']['id']
                    
                    if len(batch) < 1000:
                        break
                else:
                    break
            
            return members[:limit]
        except Exception as e:
            console.print(f"[red]Exception lấy members: {e}[/]")
            return []
    
    def send_message(self, channel_id, content):
        try:
            payload = {"content": content}
            response = requests.post(
                f"https://discord.com/api/v9/channels/{channel_id}/messages",
                headers=self.headers,
                json=payload,
                timeout=10
            )
            return response.status_code, response
        except Exception as e:
            return 0, str(e)

def load_tokens(file_path):
    try:
        if not os.path.exists(file_path):
            console.print(f"[red]❌ File {file_path} không tồn tại![/]")
            return []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            tokens = [line.strip() for line in f if line.strip()]
        
        if not tokens:
            console.print(f"[yellow]⚠️ File {file_path} trống![/]")
        
        return tokens
    except Exception as e:
        console.print(f"[red]❌ Lỗi đọc file token: {e}[/]")
        return []

def load_messages(file_path):
    try:
        if not os.path.exists(file_path):
            console.print(f"[red]❌ File {file_path} không tồn tại![/]")
            return []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            messages = [line.strip() for line in f if line.strip()]
        
        if not messages:
            console.print(f"[yellow]⚠️ File {file_path} trống![/]")
        
        return messages
    except Exception as e:
        console.print(f"[red]❌ Lỗi đọc file tin nhắn: {e}[/]")
        return []

def parse_selection(choice_str, max_value):
    selected = []
    
    try:
        for part in choice_str.split(','):
            part = part.strip()
            if '-' in part:
                try:
                    start, end = map(int, part.split('-'))
                    if start > 0 and end <= max_value and start <= end:
                        selected.extend(range(start, end + 1))
                except ValueError:
                    continue
            else:
                try:
                    num = int(part)
                    if 0 < num <= max_value:
                        selected.append(num)
                except ValueError:
                    continue
        
        return sorted(list(set(selected)))
    except Exception as e:
        console.print(f"[red]Lỗi parse selection: {e}[/]")
        return []

def select_members(api, guild_id, guild_name):
    console.print(f"\n[bold cyan]═══ CHỌN THÀNH VIÊN TRONG {guild_name} ═══[/]")
    
    with console.status(f"[bold green]Đang tải danh sách thành viên..."):
        members = api.get_guild_members(guild_id, limit=1000)
    
    if not members:
        console.print("[red]❌ Không lấy được danh sách thành viên![/]")
        return [], False
    
    console.print(f"[green]✅ Tìm thấy {len(members)} thành viên[/]")
    
    items_per_page = 20
    current_page = 0
    total_pages = (len(members) + items_per_page - 1) // items_per_page
    selected_members = []
    use_everyone = False
    
    while True:
        clear()
        print_banner()
        
        start_idx = current_page * items_per_page
        end_idx = min(start_idx + items_per_page, len(members))
        current_items = members[start_idx:end_idx]
        
        console.print(f"\n[bold magenta]THÀNH VIÊN - Trang {current_page + 1}/{total_pages}[/]\n")
        
        for idx, member in enumerate(current_items, start=start_idx + 1):
            user = member.get('user', {})
            username = user.get('username', 'Unknown')
            is_bot = " [red](BOT)[/]" if user.get('bot', False) else ""
            console.print(f"[bold yellow]{idx}[/] [cyan]{username}[/]{is_bot}")
        
        console.print(f"\n[bold cyan]{'─' * 70}[/]")
        everyone_status = "[bold green]✓ BẬT[/]" if use_everyone else "[bold red]✗ TẮT[/]"
        console.print(f"{everyone_status} [bold yellow]@everyone[/] [dim](Tag tất cả mọi người)[/]")
        console.print(f"[bold cyan]{'─' * 70}[/]")
        
        if selected_members:
            console.print(f"\n[bold green]✅ Đã chọn {len(selected_members)} thành viên[/]")
        
        console.print("\n[bold yellow]Lệnh:[/]")
        console.print("  • Nhập số (VD: 1,3,5 hoặc 1-20)")
        console.print("  • 'everyone' hoặc 'e' - Bật/tắt @everyone")
        console.print("  • 'next' - Trang tiếp | 'back' - Trang trước")
        console.print("  • 'all' - Chọn tất cả | 'done' - Hoàn tất")
        
        choice = Prompt.ask("\n[bold cyan]Lựa chọn[/]").strip().lower()
        
        if choice == 'done':
            break
        elif choice in ['everyone', 'e']:
            use_everyone = not use_everyone
            status = "BẬT" if use_everyone else "TẮT"
            console.print(f"[bold yellow]⚙️  Đã {status} @everyone[/]")
            sleep(1)
        elif choice == 'next':
            if current_page < total_pages - 1:
                current_page += 1
        elif choice == 'back':
            if current_page > 0:
                current_page -= 1
        elif choice == 'all':
            for member in members:
                user = member.get('user', {})
                if not user.get('bot', False):
                    member_id = user.get('id')
                    if not any(m['id'] == member_id for m in selected_members):
                        selected_members.append({
                            'id': member_id,
                            'username': user.get('username', 'Unknown')
                        })
            console.print(f"[green]✅ Đã chọn tất cả {len(selected_members)} thành viên[/]")
            sleep(2)
        else:
            selected_indices = parse_selection(choice, len(members))
            for idx in selected_indices:
                if 0 < idx <= len(members):
                    member = members[idx - 1]
                    user = member.get('user', {})
                    
                    if user.get('bot', False):
                        console.print(f"[yellow]⚠️ Bỏ qua bot: {user.get('username')}[/]")
                        continue
                    
                    member_id = user.get('id')
                    if not any(m['id'] == member_id for m in selected_members):
                        selected_members.append({
                            'id': member_id,
                            'username': user.get('username', 'Unknown')
                        })
                        console.print(f"[green]✅ Đã thêm: {user.get('username')}[/]")
    
    return selected_members, use_everyone

def select_guilds_and_channels(token, mode="spam"):
    """Chọn server và channel"""
    api = DiscordAPI(token)
    
    with console.status("[bold green]Đang kiểm tra token..."):
        valid, username, user_id = api.check_token()
    
    if not valid:
        console.print("[red]❌ Token không hợp lệ![/]")
        return []
    
    console.print(f"[green]✅ Token hợp lệ: {username} (ID: {user_id})[/]")
    
    with console.status("[bold cyan]Đang lấy danh sách server..."):
        guilds = api.get_guilds()
    
    if not guilds:
        console.print("[red]❌ Không tìm thấy server nào![/]")
        return []
    
    # ===== HIỂN THỊ DANH SÁCH SERVER =====
    console.print(f"\n[bold magenta]{'═' * 70}[/]")
    console.print(f"[bold magenta]  DANH SÁCH {len(guilds)} SERVER[/]")
    console.print(f"[bold magenta]{'═' * 70}[/]\n")
    
    for idx, guild in enumerate(guilds[:50], start=1):
        name = guild.get('name', 'Unknown')
        console.print(f"[bold yellow]{idx}[/] [cyan]{name}[/]")
    
    console.print(f"\n[bold cyan]{'─' * 70}[/]")
    
    guild_choice = Prompt.ask("\n[bold cyan]Chọn server (VD: 1,3,5 hoặc 1-10)[/]").strip()
    selected_guild_indices = parse_selection(guild_choice, len(guilds))
    
    if not selected_guild_indices:
        console.print("[yellow]⚠️ Không chọn server nào hợp lệ![/]")
        return []
    
    console.print(f"[green]✅ Đã chọn {len(selected_guild_indices)} server[/]")
    sleep(1)
    
    selected_channels = []
    guild_counter = 1
    
    for idx in selected_guild_indices:
        if idx < 1 or idx > len(guilds):
            continue
        
        guild = guilds[idx - 1]
        guild_name = guild.get('name', 'Unknown')
        guild_id = guild.get('id')
        
        console.print(f"\n[bold yellow]{'═' * 70}[/]")
        console.print(f"[bold yellow]  SERVER #{guild_counter}: {guild_name}[/]")
        console.print(f"[bold yellow]{'═' * 70}[/]")
        
        with console.status(f"[bold cyan]Đang lấy channel của {guild_name}..."):
            channels = api.get_channels(guild_id)
        
        text_channels = [c for c in channels if c.get('type') == 0]
        
        if not text_channels:
            console.print(f"[yellow]⚠️ Server {guild_name} không có text channel![/]")
            guild_counter += 1
            continue
        
        # ===== HIỂN THỊ DANH SÁCH CHANNEL =====
        console.print(f"\n[bold magenta]📋 {len(text_channels)} TEXT CHANNELS:[/]\n")
        
        for ch_idx, channel in enumerate(text_channels[:30], start=1):
            ch_name = channel.get('name', 'Unknown')
            console.print(f"[bold yellow]{ch_idx}[/] [cyan]#{ch_name}[/]")
        
        console.print(f"\n[bold green]{'─' * 70}[/]")
        
        ch_choice = Prompt.ask(
            f"\n[bold cyan]Chọn channel (VD: 1,2,3 hoặc 'all')[/]", 
            default="all"
        ).strip()
        
        # ===== XỬ LÝ MEMBERS/EVERYONE =====
        selected_members_for_guild = []
        use_everyone_for_guild = False
        
        if mode == "spam_everyone":
            console.print(f"\n[bold yellow]{'─' * 70}[/]")
            want_everyone = Prompt.ask(
                f"[bold yellow]📢 Tag @everyone trong {guild_name}? (y/n)[/]",
                choices=["y", "n"],
                default="n"
            ).lower()
            
            if want_everyone == 'y':
                use_everyone_for_guild = True
                console.print("[bold green]✅ Sẽ tag @everyone[/]")
            else:
                console.print("[bold red]❌ Không tag @everyone[/]")
            console.print(f"[bold yellow]{'─' * 70}[/]")
            sleep(1)
        
        elif mode == "reotag":
            console.print(f"\n[bold yellow]{'─' * 70}[/]")
            want_select_members = Prompt.ask(
                f"[bold yellow]👥 Chọn thành viên? (y/n)[/]",
                choices=["y", "n"],
                default="y"
            ).lower()
            
            if want_select_members == 'y':
                selected_members_for_guild, use_everyone_for_guild = select_members(api, guild_id, guild_name)
                
                # NẾU KHÔNG CÓ GÌ
                if not selected_members_for_guild and not use_everyone_for_guild:
                    console.print("\n[bold red]⚠️ Không có member và không @everyone[/]")
                    use_mention_all = Prompt.ask(
                        "[bold cyan]? lấy TẤT CẢ member? (y/n)[/]",
                        choices=["y", "n"],
                        default="y"
                    ).lower()
                    
                    if use_mention_all == 'y':
                        with console.status("[bold green]Đang lấy members..."):
                            all_members = api.get_guild_members(guild_id, limit=1000)
                        
                        for member in all_members:
                            user = member.get('user', {})
                            if not user.get('bot', False):
                                selected_members_for_guild.append({
                                    'id': user.get('id'),
                                    'username': user.get('username', 'Unknown')
                                })
                        
                        console.print(f"[bold green]✅ Đã thêm {len(selected_members_for_guild)} member[/]")
                        sleep(2)
                    else:
                        console.print("[bold yellow]⚠️ Sẽ gửi  (không tag)[/]")
                        sleep(1)
            
            console.print(f"[bold yellow]{'─' * 70}[/]")
        
        # ===== CHỌN CHANNEL =====
        selected_ch_indices = []
        if ch_choice.lower() == "all":
            selected_ch_indices = list(range(1, len(text_channels) + 1))
        else:
            selected_ch_indices = parse_selection(ch_choice, len(text_channels))
        
        channel_counter = 1
        for ch_idx in selected_ch_indices:
            if ch_idx < 1 or ch_idx > len(text_channels):
                continue
            
            channel = text_channels[ch_idx - 1]
            selected_channels.append({
                "guild_number": guild_counter,
                "channel_number": channel_counter,
                "guild_name": guild_name,
                "guild_id": guild_id,
                "channel_name": channel.get('name', 'Unknown'),
                "channel_id": channel.get('id'),
                "members": list(selected_members_for_guild),
                "use_everyone": use_everyone_for_guild
            })
            channel_counter += 1
        
        console.print(f"[green]✅ Đã thêm {len(selected_ch_indices)} channel[/]")
        sleep(1)
        guild_counter += 1
    
    return selected_channels

async def spam_full_task(token, channel_info, messages, delay, task_id):
    api = DiscordAPI(token)
    channel_id = channel_info['channel_id']
    channel_name = channel_info['channel_name']
    guild_name = channel_info['guild_name']
    guild_num = channel_info.get('guild_number', 0)
    channel_num = channel_info.get('channel_number', 0)
    
    success_count = 0
    fail_count = 0
    
    while True:
        try:
            full_message = "\n".join(messages)
            status_code, response = api.send_message(channel_id, full_message)
            
            if status_code == 200:
                success_count += 1
                preview = messages[0][:20] + "..." if len(messages[0]) > 20 else messages[0]
                console.print(
                    f"[bold green]✅ [T{task_id}][/] → "
                    f"[yellow]S#{guild_num}[/] [cyan]{guild_name[:15]}[/] > "
                    f"[yellow]C#{channel_num}[/] [magenta]#{channel_name[:12]}[/]: "
                    f"{preview} +{len(messages)}dòng | ✓{success_count}"
                )
            elif status_code == 429:
                try:
                    retry_after = response.json().get("retry_after", 5)
                except:
                    retry_after = 5
                console.print(f"[bold yellow]⏳ [T{task_id}][/] Rate limit {retry_after}s...")
                await asyncio.sleep(retry_after)
                continue
            elif status_code in [403, 401]:
                fail_count += 1
                console.print(f"[bold red]❌ [T{task_id}][/] {'No perms' if status_code==403 else 'Token die'} | ✗{fail_count}")
                break
            else:
                fail_count += 1
                console.print(f"[bold red]❌ [T{task_id}][/] Error {status_code} | ✗{fail_count}")
            
            await asyncio.sleep(delay)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            fail_count += 1
            console.print(f"[bold red]❌ [T{task_id}][/] Exception: {str(e)[:30]} | ✗{fail_count}")
            await asyncio.sleep(3)

async def spam_everyone_full_task(token, channel_info, messages, delay, task_id):
    api = DiscordAPI(token)
    channel_id = channel_info['channel_id']
    channel_name = channel_info['channel_name']
    guild_name = channel_info['guild_name']
    guild_num = channel_info.get('guild_number', 0)
    channel_num = channel_info.get('channel_number', 0)
    use_everyone = channel_info.get('use_everyone', False)
    
    success_count = 0
    fail_count = 0
    
    while True:
        try:
            full_message = "\n".join(messages)
            
            if use_everyone:
                full_message = f"@everyone\n{full_message}"
                tag_display = "[bold red][@everyone][/]"
            else:
                tag_display = ""
            
            status_code, response = api.send_message(channel_id, full_message)
            
            if status_code == 200:
                success_count += 1
                preview = messages[0][:15] + "..." if len(messages[0]) > 15 else messages[0]
                console.print(
                    f"[bold green]✅ [T{task_id}][/] → "
                    f"[yellow]S#{guild_num}[/] [cyan]{guild_name[:15]}[/] > "
                    f"[yellow]C#{channel_num}[/] [magenta]#{channel_name[:12]}[/]: "
                    f"{preview} {tag_display} | ✓{success_count}"
                )
            elif status_code == 429:
                try:
                    retry_after = response.json().get("retry_after", 5)
                except:
                    retry_after = 5
                console.print(f"[bold yellow]⏳ [T{task_id}][/] Rate limit {retry_after}s...")
                await asyncio.sleep(retry_after)
                continue
            elif status_code in [403, 401]:
                fail_count += 1
                console.print(f"[bold red]❌ [T{task_id}][/] {'No perms' if status_code==403 else 'Token die'} | ✗{fail_count}")
                break
            else:
                fail_count += 1
                console.print(f"[bold red]❌ [T{task_id}][/] Error {status_code} | ✗{fail_count}")
            
            await asyncio.sleep(delay)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            fail_count += 1
            console.print(f"[bold red]❌ [T{task_id}][/] Exception: {str(e)[:30]} | ✗{fail_count}")
            await asyncio.sleep(3)

async def reotag_task(token, channel_info, messages, delay, task_id):
    api = DiscordAPI(token)
    channel_id = channel_info['channel_id']
    channel_name = channel_info['channel_name']
    guild_name = channel_info['guild_name']
    guild_num = channel_info.get('guild_number', 0)
    channel_num = channel_info.get('channel_number', 0)
    members = channel_info.get('members', [])
    use_everyone = channel_info.get('use_everyone', False)
    
    message_index = 0
    success_count = 0
    fail_count = 0
    
    while True:
        try:
            base_message = messages[message_index]
            
            if use_everyone:
                full_message = f"@everyone {base_message}"
                tag_display = "[bold red][@everyone][/]"
            elif members and len(members) > 0:
                mentions = " ".join([f"<@{m['id']}>" for m in members])
                full_message = f"{base_message} {mentions}"
                tag_display = f"[bold cyan][@{len(members)}][/]"
            else:
                full_message = base_message
                tag_display = ""
            
            status_code, response = api.send_message(channel_id, full_message)
            
            if status_code == 200:
                success_count += 1
                preview = base_message[:15] + "..." if len(base_message) > 15 else base_message
                console.print(
                    f"[bold green]✅ [T{task_id}][/] → "
                    f"[yellow]S#{guild_num}[/] [cyan]{guild_name[:15]}[/] > "
                    f"[yellow]C#{channel_num}[/] [magenta]#{channel_name[:12]}[/]: "
                    f"{preview} {tag_display} | ✓{success_count}"
                )
            elif status_code == 429:
                try:
                    retry_after = response.json().get("retry_after", 5)
                except:
                    retry_after = 5
                console.print(f"[bold yellow]⏳ [T{task_id}][/] Rate limit {retry_after}s...")
                await asyncio.sleep(retry_after)
                continue
            elif status_code in [403, 401]:
                fail_count += 1
                console.print(f"[bold red]❌ [T{task_id}][/] {'No perms' if status_code==403 else 'Token die'} | ✗{fail_count}")
                break
            else:
                fail_count += 1
                console.print(f"[bold red]❌ [T{task_id}][/] Error {status_code} | ✗{fail_count}")
            
            message_index = (message_index + 1) % len(messages)
            await asyncio.sleep(delay)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            fail_count += 1
            console.print(f"[bold red]❌ [T{task_id}][/] Exception: {str(e)[:30]} | ✗{fail_count}")
            await asyncio.sleep(3)

async def nhay_thuong_task(token, channel_info, messages, delay, task_id):
    api = DiscordAPI(token)
    channel_id = channel_info['channel_id']
    channel_name = channel_info['channel_name']
    guild_name = channel_info['guild_name']
    guild_num = channel_info.get('guild_number', 0)
    channel_num = channel_info.get('channel_number', 0)
    
    message_index = 0
    success_count = 0
    fail_count = 0
    
    while True:
        try:
            message = messages[message_index]
            status_code, response = api.send_message(channel_id, message)
            
            if status_code == 200:
                success_count += 1
                preview = message[:25] + "..." if len(message) > 25 else message
                console.print(
                    f"[bold green]✅ [T{task_id}][/] → "
                    f"[yellow]S#{guild_num}[/] [cyan]{guild_name[:15]}[/] > "
                    f"[yellow]C#{channel_num}[/] [magenta]#{channel_name[:12]}[/]: "
                    f"{preview} | ✓{success_count}"
                )
            elif status_code == 429:
                try:
                    retry_after = response.json().get("retry_after", 5)
                except:
                    retry_after = 5
                console.print(f"[bold yellow]⏳ [T{task_id}][/] Rate limit {retry_after}s...")
                await asyncio.sleep(retry_after)
                continue
            elif status_code in [403, 401]:
                fail_count += 1
                console.print(f"[bold red]❌ [T{task_id}][/] {'No perms' if status_code==403else 'Token die'} | ✗{fail_count}")
                break
            else:
                fail_count += 1
                console.print(f"[bold red]❌ [T{task_id}][/] Error {status_code} | ✗{fail_count}")
            
            message_index = (message_index + 1) % len(messages)
            await asyncio.sleep(delay)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            fail_count += 1
            console.print(f"[bold red]❌ [T{task_id}][/] Exception: {str(e)[:30]} | ✗{fail_count}")
            await asyncio.sleep(3)

async def main():
    clear()
    print_banner()
    
    # CHỌN CHỨC NĂNG
    console.print(f"\n[bold cyan]{'═' * 70}[/]")
    console.print("[bold cyan]                  CHỌN CHỨC NĂNG                    [/]")
    console.print(f"[bold cyan]{'═' * 70}[/]")
    console.print("[bold yellow]1[/] [cyan]Treo Ngôn[/]")
    console.print("[bold yellow]2[/] [red]Treo Ngôn + @everyone[/]")
    console.print("[bold yellow]3[/] [magenta]Reo Tag[/]")
    console.print("[bold yellow]4[/] [green]Nhây Thường[/]")
    console.print(f"[bold cyan]{'═' * 70}[/]")
    
    mode_choice = Prompt.ask("\n[bold cyan]Chọn chức năng[/]", choices=["1", "2", "3", "4"], default="1")
    
    mode_map = {
        "1": ("spam", "TREO NGÔN (FULL)"),
        "2": ("spam_everyone", "TREO NGÔN + @EVERYONE"),
        "3": ("reotag", "REO TAG (TỪNG DÒNG)"),
        "4": ("nhay_thuong", "NHÂY THƯỜNG")
    }
    
    mode, mode_name = mode_map[mode_choice]
    
    console.print(f"\n[bold green]✅ Đã chọn: {mode_name}[/]")
    sleep(1)
    
    console.print(f"\n[bold cyan]{'═' * 70}[/]")
    console.print("[bold cyan]                    CẤU HÌNH                        [/]")
    console.print(f"[bold cyan]{'═' * 70}[/]")
    
    # 1. Token
    token_file = Prompt.ask("\n[bold yellow]📂 File token (.txt)[/]", default="tokens.txt")
    tokens = load_tokens(token_file)
    
    if not tokens:
        console.print("[red]❌ Không có token![/]")
        return
    
    console.print(f"[green]✅ Đã tải {len(tokens)} token[/]")
    sleep(1)
    
    # 2. Chọn server và channel
    console.print(f"\n[bold cyan]{'═' * 70}[/]")
    console.print("[bold cyan]              CHỌN SERVER VÀ CHANNEL                [/]")
    console.print(f"[bold cyan]{'═' * 70}[/]")
    console.print("[yellow]💡 Dùng token đầu để lấy danh sách[/]\n")
    
    selected_channels = select_guilds_and_channels(tokens[0], mode=mode)
    
    if not selected_channels:
        console.print("[red]❌ Không có channel![/]")
        return
    
    console.print(f"\n[bold green]{'═' * 70}[/]")
    console.print(f"[bold green]✅ ĐÃ CHỌN {len(selected_channels)} CHANNEL[/]")
    console.print(f"[bold green]{'═' * 70}[/]")
    
    # HIỂN THỊ TỔNG QUAN
    current_guild = None
    for ch in selected_channels:
        guild_num = ch.get('guild_number', 0)
        channel_num = ch.get('channel_number', 0)
        guild_name = ch['guild_name']
        channel_name = ch['channel_name']
        
        if current_guild != guild_num:
            console.print(f"\n[bold yellow]📁 Server #{guild_num}: {guild_name}[/]")
            current_guild = guild_num
        
        tag_info = ""
        if ch.get('use_everyone'):
            tag_info = " [bold red][@everyone][/]"
        elif ch.get('members') and len(ch['members']) > 0:
            tag_info = f" [bold cyan][@{len(ch['members'])}][/]"
        
        console.print(f"   [yellow]└─ C#{channel_num}[/] [magenta]#{channel_name}[/]{tag_info}")
    
    # 3. File tin nhắn
    console.print(f"\n[bold cyan]{'─' * 70}[/]")
    message_file = Prompt.ask("[bold yellow]📂 File tin nhắn (.txt)[/]", default="messages.txt")
    messages = load_messages(message_file)
    
    if not messages:
        console.print("[red]❌ Không có tin nhắn![/]")
        return
    
    console.print(f"[green]✅ Đã tải {len(messages)} tin nhắn[/]")
    
    # Preview
    console.print(f"\n[bold cyan]📝 Preview:[/]")
    for i, msg in enumerate(messages[:3], 1):
        preview = msg[:50] + "..." if len(msg) > 50 else msg
        console.print(f"   {i}. {preview}")
    if len(messages) > 3:
        console.print(f"   ... và {len(messages) - 3} tin nhắn khác")
    
    # Thông báo gửi
    if mode in ["spam", "spam_everyone"]:
        console.print(f"\n[bold magenta]📨 Sẽ gửi FULL {len(messages)} dòng/lần[/]")
    else:
        console.print(f"\n[bold magenta]📨 Sẽ gửi TỪNG dòng, lặp {len(messages)} tin[/]")
    
    # 4. Delay
    try:
        delay = float(Prompt.ask("\n[bold yellow]⏳ Delay (giây)[/]", default="2"))
        if delay < 0.5:
            console.print("[yellow]⚠️ Delay tối thiểu 0.5s[/]")
            delay = 0.5
    except ValueError:
        console.print("[yellow]⚠️ Dùng delay 2s[/]")
        delay = 2
    
    # 5. TỔNG KẾT
    total_tasks = len(tokens) * len(selected_channels)
    
    console.print(f"\n[bold red]{'═' * 70}[/]")
    console.print(f"[bold red]           🚀 TỔNG KẾT - {mode_name}[/]")
    console.print(f"[bold red]{'═' * 70}[/]")
    console.print(f"[cyan]📊 {len(tokens)} token × {len(selected_channels)} channel = [bold]{total_tasks} TASK[/]")
    console.print(f"[yellow]⏱️  Delay: {delay}s | Tin nhắn: {len(messages)} dòng[/]")
    
    # Thống kê tag
    if mode == "spam_everyone":
        everyone_count = sum(1 for ch in selected_channels if ch.get('use_everyone'))
        if everyone_count > 0:
            console.print(f"[red]👥 @everyone: {everyone_count}/{len(selected_channels)} channel[/]")
        else:
            console.print(f"[yellow]⚠️  Không có channel nào @everyone[/]")
    
    if mode == "reotag":
        total_members = sum(len(ch.get('members', [])) for ch in selected_channels)
        everyone_count = sum(1 for ch in selected_channels if ch.get('use_everyone'))
        mention_channels = sum(1 for ch in selected_channels if ch.get('members') and len(ch.get('members', [])) > 0)
        
        if everyone_count > 0:
            console.print(f"[red]👥 @everyone: {everyone_count} channel[/]")
        if mention_channels > 0:
            console.print(f"[cyan]👥 @mention: {mention_channels} channel | {total_members} member[/]")
        
        no_tag = len(selected_channels) - everyone_count - mention_channels
        if no_tag > 0:
            console.print(f"[yellow]⚠️  {no_tag} channel không tag[/]")
    
    console.print(f"[bold red]{'═' * 70}[/]")
    console.print("[red]⌨️  Nhấn Ctrl+C để dừng[/]")
    
    confirm = Prompt.ask(f"\n[bold green]▶️  BẮT ĐẦU {mode_name}? (y/n)[/]", choices=["y", "n"], default="y").lower()
    if confirm != 'y':
        console.print("[yellow]❌ Đã hủy[/]")
        return
    
    # KHỞI ĐỘNG
    tasks = []
    task_id = 1
    
    task_map = {
        "spam": spam_full_task,
        "spam_everyone": spam_everyone_full_task,
        "reotag": reotag_task,
        "nhay_thuong": nhay_thuong_task
    }
    
    task_function = task_map[mode]
    
    for token in tokens:
        for channel_info in selected_channels:
            tasks.append(task_function(token, channel_info, messages, delay, task_id))
            task_id += 1
    
    console.print(f"\n[bold magenta]{'═' * 70}[/]")
    console.print(f"[bold magenta]     🔥 ĐANG {mode_name} - {len(tasks)} TASK[/]")
    console.print(f"[bold magenta]{'═' * 70}[/]\n")
    
    try:
        await asyncio.gather(*tasks)
    except KeyboardInterrupt:
        console.print(f"\n[bold yellow]{'═' * 70}[/]")
        console.print("[bold yellow]⏹️  DỪNG TOOL[/]")
        console.print(f"[bold yellow]{'═' * 70}[/]")
    except Exception as e:
        console.print(f"\n[bold red]❌ Lỗi: {e}[/]")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[bold yellow]👋 Tạm biệt![/]")
    except Exception as e:
        console.print(f"\n[bold red]❌ Lỗi nghiêm trọng: {e}[/]")