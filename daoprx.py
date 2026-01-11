import requests
import concurrent.futures
import time
import os
import re
from datetime import datetime
from colorama import init, Fore, Back, Style

# Khởi tạo colorama
init(autoreset=True)

# Danh sách API proxy (rút gọn)
PROXY_API_SOURCES = {
    "http": [
        "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all",
        "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt",
        "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
     ###### tự tìm đi ########
    ],
    "socks4": [
        "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks4.txt",
        "https://raw.githubusercontent.com/roosterkid/openproxylist/main/socks4.txt",
        "https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks4&timeout=10000&country=all"
    ],
    "socks5": [
         "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks5.txt",
        "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt",
        "https://raw.githubusercontent.com/roosterkid/openproxylist/main/socks5.txt",
        "https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks5&timeout=10000&country=all",
        "https://raw.githubusercontent.com/jetkai/proxy-list/master/online-proxies/txt/proxies.txt",
        "https://raw.githubusercontent.com/sunny9577/proxy-scraper/master/proxies.txt"
    ]
}

class ProxyScraper:
    def __init__(self, max_workers=100):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.timeout = 10
        self.max_workers = max(min(max_workers, 1000), 1)
        self.total_checked = 0
        self.live_count = 0
        self.total_proxies = 0
        self.live_proxies = []
        self.start_time = time.time()
        self.last_print_time = 0
        self.last_stats = ""
        
    def clear_line(self):
        """Xóa dòng hiện tại trên console"""
        print("\r" + " " * 100, end="\r")
    
    def print_progress(self, force=False):
        """Hiển thị thanh tiến trình và thống kê"""
        current_time = time.time()
        if not force and current_time - self.last_print_time < 0.1:
            return
            
        self.last_print_time = current_time
        elapsed = current_time - self.start_time
        percent = (self.total_checked / self.total_proxies * 100) if self.total_proxies > 0 else 0
        
        # Tạo thanh tiến trình
        bar_length = 20
        filled_length = int(bar_length * percent // 100)
        bar = '█' * filled_length + ' ' * (bar_length - filled_length)
        
        # Tạo thông tin thống kê
        stats = f"{Fore.CYAN}[{bar}] {percent:.1f}% | {Fore.YELLOW}Đã kiểm tra: {self.total_checked}/{self.total_proxies} | {Fore.GREEN}Live: {self.live_count} | {Fore.BLUE}Thời gian: {elapsed:.1f}s"
        
        # Chỉ in nếu có thay đổi so với lần trước
        if stats != self.last_stats:
            self.clear_line()
            print(f"\r{stats}", end="", flush=True)
            self.last_stats = stats
    
    def print_live_proxy(self, proxy, speed):
        """Hiển thị proxy live như trong ảnh mẫu"""
        self.clear_line()
        speed_color = Fore.GREEN if speed < 2 else Fore.YELLOW if speed < 5 else Fore.RED
        print(f"{Fore.GREEN}OK: {proxy} - elite - {speed_color}{speed:.2f}s")
        self.print_progress(force=True)
    
    def get_proxies_from_api(self, api_url):
        try:
            response = self.session.get(api_url, timeout=self.timeout)
            if response.status_code == 200:
                proxies = re.findall(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{2,5}", response.text)
                return list(set(proxies))
            elif response.status_code == 429:
                time.sleep(2)
                return self.get_proxies_from_api(api_url)
        except:
            return []

    def check_proxy(self, proxy):
        test_url = "http://httpbin.org/ip"
        proxies = {
            "http": f"http://{proxy}",
            "https": f"http://{proxy}"
        }
        
        try:
            start_time = time.time()
            response = self.session.get(
                test_url,
                proxies=proxies,
                timeout=5
            )
            if response.status_code == 200:
                speed = time.time() - start_time
                return (proxy, speed)
        except:
            pass
        
        return None

    def process_proxy(self, proxy):
        result = self.check_proxy(proxy)
        self.total_checked += 1
        
        if result:
            proxy, speed = result
            self.live_count += 1
            self.live_proxies.append((proxy, speed))
            self.print_live_proxy(proxy, speed)
        else:
            self.print_progress()
            
        return result

    def scrape_and_check(self):
        print(f"{Fore.CYAN}⚡ Bắt đầu thu thập proxy với {self.max_workers} luồng...")
        
        # Thu thập proxy từ tất cả nguồn
        print(f"{Fore.BLUE}🔍 Đang thu thập proxy từ {sum(len(v) for v in PROXY_API_SOURCES.values())} nguồn...")
        
        all_proxies = set()
        with concurrent.futures.ThreadPoolExecutor(max_workers=min(20, self.max_workers)) as executor:
            futures = []
            for proxy_type, api_list in PROXY_API_SOURCES.items():
                for api_url in api_list:
                    futures.append(executor.submit(self.get_proxies_from_api, api_url))
            
            for future in concurrent.futures.as_completed(futures):
                proxies = future.result()
                if proxies:
                    all_proxies.update(proxies)
        
        self.total_proxies = len(all_proxies)
        print(f"\n{Fore.CYAN}🌟 Tổng số proxy thu thập được: {self.total_proxies}")
        
        # Kiểm tra proxy live
        print(f"\n{Fore.BLUE}🔎 Đang kiểm tra {self.total_proxies} proxy...")
        self.print_progress(force=True)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(self.process_proxy, proxy) for proxy in all_proxies]
            concurrent.futures.wait(futures)
        
        # Sắp xếp proxy theo tốc độ
        self.live_proxies.sort(key=lambda x: x[1])
        
        total_time = time.time() - self.start_time
        self.clear_line()
        print(f"\n{Fore.CYAN}✅ Hoàn thành trong {total_time:.2f}s")
        print(f"{Fore.GREEN}✔ Proxy live: {self.live_count}/{self.total_proxies}")
        print(f"{Fore.BLUE}⚡ Luồng sử dụng: {self.max_workers}")
        
        return [proxy for proxy, speed in self.live_proxies]

    def save_results(self, filename=None):
        if not os.path.exists("proxy_results"):
            os.makedirs("proxy_results")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if not filename:
            filename = f"proxies_{timestamp}"
        
        filepath = os.path.join("proxy_results", f"{filename}.txt")
        with open(filepath, 'w', encoding='utf-8') as f:
            for proxy in [proxy for proxy, speed in self.live_proxies]:
                f.write(f"{proxy}\n")
        
        print(f"\n{Fore.CYAN}💾 Kết quả đã lưu vào: {filepath}")

def get_thread_count():
    while True:
        try:
            threads = input(f"{Fore.CYAN}🧵 Nhập số luồng (1-1000, mặc định 100): ").strip()
            if not threads:
                return 100
            threads = int(threads)
            if 1 <= threads <= 1000:
                return threads
            print(f"{Fore.RED}⚠ Vui lòng nhập giá trị từ 1 đến 1000")
        except ValueError:
            print(f"{Fore.RED}⚠ Nhập không hợp lệ. Vui lòng nhập số.")

def main():
    print(f"""
    {Fore.CYAN}██████╗ ██████╗  ██████╗ ██╗  ██╗██╗   ██╗██████╗ 
    ██╔══██╗██╔══██╗██╔═══██╗╚██╗██╔╝╚██╗ ██╔╝╚════██╗
    ██████╔╝██████╔╝██║   ██║ ╚███╔╝  ╚████╔╝   ▄███╔╝
    ██╔═══╝ ██╔══██╗██║   ██║ ██╔██╗   ╚██╔╝    ▀▀══╝ 
    ██║     ██║  ██║╚██████╔╝██╔╝ ██╗   ██║     ██╗   
    ╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝     ╚═╝   
    {Fore.YELLOW}Proxy Scraper VIP - Phiên bản ổn định
    """)
    
    thread_count = get_thread_count()
    scraper = ProxyScraper(max_workers=thread_count)
    
    try:
        live_proxies = scraper.scrape_and_check()
        
        if live_proxies:
            custom_name = input(f"\n{Fore.CYAN}📝 Nhập tên file (để trống để tự động đặt tên): ")
            scraper.save_results(custom_name.strip() or None)
        else:
            print(f"{Fore.RED}⚠ Không tìm thấy proxy live nào!")
        
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}🚫 Đã dừng tiến trình!")
        if scraper.live_count > 0:
            save = input(f"{Fore.YELLOW}💾 Lưu proxy đã thu thập? (y/n): ").lower()
            if save == 'y':
                scraper.save_results("interrupted_results")
    
    print(f"\n{Fore.GREEN}✨ Hoàn tất chương trình!")

if __name__ == "__main__":
    main()