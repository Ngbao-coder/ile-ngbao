import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from threading import Thread
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import re
import os
import random

class TikTokLoginApp:
    # Class-level tracking for used reporting options across all browsers
    used_reporting_options = set()
    
    def __init__(self, root):
        self.root = root
        self.root.title("TAT - REPORT TIKTOK V2")
        self.root.geometry("1400x1000")  # Tăng width để có chỗ cho layout 2 cột
        self.root.resizable(True, True)
        
        # Trạng thái ứng dụng
        self.drivers = []  # Danh sách các driver instances
        self.is_running = False
        self.cookie_fields = []  # Danh sách các cookie text widgets
        self.proxy_fields = []  # Danh sách các proxy text widgets
        self.current_account_count = 1
        
        # Proxy settings
        self.use_proxy_var = tk.BooleanVar()
        self.proxy_mode_var = tk.StringVar(value="chung")  # "chung" hoặc "rieng"
        self.proxy_type_var = tk.StringVar(value="static_ipv6")  # "static_ipv6" hoặc "rotating_ipv6"
        
        # Reporting options definition
        self.reporting_options = [
            {
                "id": 1,
                "primary": "Violence, abuse, and criminal exploitation",
                "secondary": "Exploitation and abuse of people under 18"
            },
            {
                "id": 2,
                "primary": "Violence, abuse, and criminal exploitation",
                "secondary": "Physical violence and violent threats"
            },
            {
                "id": 3,
                "primary": "Violence, abuse, and criminal exploitation",
                "secondary": "Sexual exploitation and abuse"
            },
            {
                "id": 4,
                "primary": "Violence, abuse, and criminal exploitation",
                "secondary": "Human exploitation"
            },
            {
                "id": 5,
                "primary": "Violence, abuse, and criminal exploitation",
                "secondary": "Animal abuse"
            },
            {
                "id": 6,
                "primary": "Violence, abuse, and criminal exploitation",
                "secondary": "Other criminal activities"
            },
            {
                "id": 7,
                "primary": "Hate and harassment",
                "secondary": "Hate speech and hateful behaviors"
            },
            {
                "id": 8,
                "primary": "Hate and harassment",
                "secondary": "Harassment and bullying"
            },
            {
                "id": 9,
                "primary": "Suicide and self-harm",
                "secondary": None
            },
            {
                "id": 10,
                "primary": "Disordered eating and unhealthy body image",
                "secondary": None
            },
            {
                "id": 11,
                "primary": "Dangerous activities and challenges",
                "secondary": None
            },
            {
                "id": 12,
                "primary": "Nudity and sexual content",
                "secondary": "Youth sexual activity, solicitation, and exploitation"
            },
            {
                "id": 13,
                "primary": "Nudity and sexual content",
                "secondary": "Sexually suggestive behavior by youth"
            },
            {
                "id": 14,
                "primary": "Nudity and sexual content",
                "secondary": "Adult sexual activity, services, and solicitation"
            },
            {
                "id": 15,
                "primary": "Nudity and sexual content",
                "secondary": "Adult nudity"
            },
            {
                "id": 16,
                "primary": "Nudity and sexual content",
                "secondary": "Sexually explicit language"
            },
            {
                "id": 17,
                "primary": "Shocking and graphic content",
                "secondary": None
            },
            {
                "id": 18,
                "primary": "Misinformation",
                "secondary": "Election misinformation"
            },
            {
                "id": 19,
                "primary": "Misinformation",
                "secondary": "Harmful misinformation"
            },
            {
                "id": 20,
                "primary": "Misinformation",
                "secondary": "Deepfakes, synthetic media, and manipulated media"
            },
            {
                "id": 21,
                "primary": "Deceptive behavior and spam",
                "secondary": "Fake engagement"
            },
            {
                "id": 22,
                "primary": "Deceptive behavior and spam",
                "secondary": "Spam"
            },
            {
                "id": 23,
                "primary": "Regulated goods and activities",
                "secondary": "Gambling"
            },
            {
                "id": 24,
                "primary": "Regulated goods and activities",
                "secondary": "Alcohol, tobacco, and drugs"
            },
            {
                "id": 25,
                "primary": "Regulated goods and activities",
                "secondary": "Firearms and dangerous weapons"
            },
            {
                "id": 26,
                "primary": "Regulated goods and activities",
                "secondary": "Trade of other regulated goods and services"
            },
            {
                "id": 27,
                "primary": "Frauds and scams",
                "secondary": None
            },
            {
                "id": 28,
                "primary": "Sharing personal information",
                "secondary": None
            },
            {
                "id": 29,
                "primary": "Other",
                "secondary": None
            }
        ]
        
        self.setup_ui()
        
    def setup_ui(self):
        # Configure hacker theme colors
        self.hacker_colors = {
            'bg': '#0d1117',           # Dark background (GitHub dark)
            'fg': '#00ff00',           # Bright green text
            'accent': '#58a6ff',       # Blue accent
            'warning': '#f85149',      # Red warning
            'success': '#3fb950',      # Green success
            'info': '#79c0ff',         # Light blue info
            'panel': '#161b22',        # Panel background
            'button': '#21262d',       # Button background
            'input': '#0d1117',        # Input background
            'border': '#30363d'        # Border color
        }
        
        # Configure root window
        self.root.configure(bg=self.hacker_colors['bg'])
        self.root.title("🔥 TOOL DAME TIKTOK BY nguyen hoang gia bao - ZALO: 0988467271 🔥")
        
        # Create custom style
        self.create_hacker_style()
        
        # Main container
        main_container = tk.Frame(
            self.root, 
            bg=self.hacker_colors['bg'],
            relief='flat',
            bd=0
        )
        main_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Title banner
        self.create_title_banner(main_container)
        
        # Main content frame with scrollbar
        canvas = tk.Canvas(
            main_container,
            bg=self.hacker_colors['bg'],
            highlightthickness=0,
            relief='flat'
        )
        
        scrollbar = tk.Scrollbar(
            main_container,
            orient="vertical",
            command=canvas.yview,
            bg=self.hacker_colors['panel'],
            troughcolor=self.hacker_colors['bg'],
            activebackground=self.hacker_colors['accent']
        )
        
        scrollable_frame = tk.Frame(canvas, bg=self.hacker_colors['bg'])
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Tạo layout 2 cột
        main_columns_frame = tk.Frame(scrollable_frame, bg=self.hacker_colors['bg'])
        main_columns_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Cột trái - các section chính
        left_column = tk.Frame(main_columns_frame, bg=self.hacker_colors['bg'])
        left_column.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Cột phải - control và log
        right_column = tk.Frame(main_columns_frame, bg=self.hacker_colors['bg'])
        right_column.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        # Sections cho cột trái
        self.create_target_section(left_column)
        self.create_accounts_section(left_column)
        self.create_proxy_section(left_column)
        
        # Sections cho cột phải
        self.create_control_section(right_column)
        self.create_log_section(right_column)
        
        # Configure grid weights
        main_container.grid_rowconfigure(1, weight=1)
        main_container.grid_columnconfigure(0, weight=1)
    
    def create_hacker_style(self):
        """Create custom hacker-style UI components"""
        # Custom styles for different elements
        pass
    
    def create_title_banner(self, parent):
        """Create hacker-style title banner"""
        banner_frame = tk.Frame(
            parent,
            bg=self.hacker_colors['panel'],
            relief='solid',
            bd=1,
            highlightbackground=self.hacker_colors['accent'],
            highlightthickness=2
        )
        banner_frame.pack(fill='x', pady=(0, 15))
        
        # ASCII art title
        title_text = """
╔══════════════════════════════════════════════════════════════╗
║  ████████╗██╗██╗  ██╗████████╗ ██████╗ ██╗  ██╗              ║
║  ╚══██╔══╝██║██║ ██╔╝╚══██╔══╝██╔═══██╗██║ ██╔╝              ║
║     ██║   ██║█████╔╝    ██║   ██║   ██║█████╔╝               ║
║     ██║   ██║██╔═██╗    ██║   ██║   ██║██╔═██╗               ║
║     ██║   ██║██║  ██╗   ██║   ╚██████╔╝██║  ██╗              ║
║     ╚═╝   ╚═╝╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝              ║
║                                                              ║
║              🔥 TAT - REPORT TIKTOK V2 🔥                   ║
║                [TOOL AUTO DAME TIKTOK]                       ║
╚══════════════════════════════════════════════════════════════╝
"""
        
        title_label = tk.Label(
            banner_frame,
            text=title_text,
            font=('Courier New', 8, 'bold'),
            fg=self.hacker_colors['accent'],
            bg=self.hacker_colors['panel'],
            justify='center'
        )
        title_label.pack(pady=10)
        
        # Thông tin chủ tool
        info_frame = tk.Frame(banner_frame, bg=self.hacker_colors['panel'])
        info_frame.pack(fill='x', padx=20, pady=(0, 10))
        
        # Thông tin cá nhân
        tk.Label(
            info_frame,
            text="👨‍💻 DEVELOPER INFO",
            font=('Courier New', 10, 'bold'),
            fg=self.hacker_colors['warning'],
            bg=self.hacker_colors['panel']
        ).pack()
        
        tk.Label(
            info_frame,
            text="📛 Tên: Nguyen Dang Khoi | 📱 Phone/Zalo: 0941774123",
            font=('Courier New', 9),
            fg=self.hacker_colors['success'],
            bg=self.hacker_colors['panel']
        ).pack()
        
        # Facebook link có thể click
        fb_label = tk.Label(
            info_frame,
            text="👤 Facebook: https://www.facebook.com/khoi.126201",
            font=('Courier New', 9, 'underline'),
            fg=self.hacker_colors['info'],
            bg=self.hacker_colors['panel'],
            cursor='hand2'
        )
        fb_label.pack()
        fb_label.bind("<Button-1>", lambda e: self.open_facebook())
        
        tk.Label(
            info_frame,
            text="💼 Mô tả: Hiện đang có nhiều tool dame bên Facebook, TikTok. Ai cần inbox Khôi nhaaa!!",
            font=('Courier New', 8),
            fg=self.hacker_colors['fg'],
            bg=self.hacker_colors['panel']
        ).pack()
        
        tk.Label(
            info_frame,
            text="🎓 Khôi vẫn nhận làm tool theo yêu cầu, nhận học viên dame bản quyền thương hiệu..",
            font=('Courier New', 8),
            fg=self.hacker_colors['fg'],
            bg=self.hacker_colors['panel']
        ).pack()
        
        # Status indicators
        status_frame = tk.Frame(banner_frame, bg=self.hacker_colors['panel'])
        status_frame.pack(fill='x', padx=20, pady=(10, 10))
        
        # System status
        status_labels = [
            ("🟢 SYSTEM", "ONLINE"),
            ("🔒 SECURITY", "BYPASSED"), 
            ("⚡ POWER", "MAXIMUM"),
            ("🎯 TARGET", "ACQUIRED")
        ]
        
        for i, (status, value) in enumerate(status_labels):
            tk.Label(
                status_frame,
                text=f"{status}: {value}",
                font=('Courier New', 9, 'bold'),
                fg=self.hacker_colors['success'],
                bg=self.hacker_colors['panel']
            ).grid(row=0, column=i, padx=10, sticky='w')
    
    def create_target_section(self, parent):
        """Create target/URL section with hacker style"""
        section_frame = self.create_section_frame(parent, "🎯 TARGET CONFIGURATION")
        
        # URL input
        url_frame = tk.Frame(section_frame, bg=self.hacker_colors['bg'])
        url_frame.pack(fill='x', pady=5)
        
        tk.Label(
            url_frame,
            text="TARGET URL:",
            font=('Courier New', 10, 'bold'),
            fg=self.hacker_colors['warning'],
            bg=self.hacker_colors['bg']
        ).pack(anchor='w')
        
        self.url_var = tk.StringVar()
        url_entry = tk.Entry(
            url_frame,
            textvariable=self.url_var,
            font=('Courier New', 11),
            bg=self.hacker_colors['input'],
            fg=self.hacker_colors['fg'],
            insertbackground=self.hacker_colors['fg'],
            relief='solid',
            bd=1,
            highlightbackground=self.hacker_colors['accent'],
            highlightthickness=1
        )
        url_entry.pack(fill='x', pady=(5, 0), ipady=5)
        url_entry.insert(0, "https://www.tiktok.com/@victim/video/xxxxxxxxx")
    
    def create_accounts_section(self, parent):
        """Create accounts section with hacker style"""
        section_frame = self.create_section_frame(parent, "👥 INFILTRATION ACCOUNTS")
        
        # Number of accounts
        accounts_frame = tk.Frame(section_frame, bg=self.hacker_colors['bg'])
        accounts_frame.pack(fill='x', pady=5)
        
        tk.Label(
            accounts_frame,
            text="AGENT COUNT:",
            font=('Courier New', 10, 'bold'),
            fg=self.hacker_colors['warning'],
            bg=self.hacker_colors['bg']
        ).pack(side='left')
        
        self.num_accounts_var = tk.IntVar(value=1)
        accounts_spinner = tk.Spinbox(
            accounts_frame,
            from_=1, to=10,
            textvariable=self.num_accounts_var,
            font=('Courier New', 11, 'bold'),
            bg=self.hacker_colors['input'],
            fg=self.hacker_colors['accent'],
            buttonbackground=self.hacker_colors['button'],
            relief='solid',
            bd=1,
            width=10,
            command=self.update_cookie_fields
        )
        accounts_spinner.pack(side='left', padx=(10, 0))
        
        # Cookie fields container
        self.cookie_container = tk.Frame(section_frame, bg=self.hacker_colors['bg'])
        self.cookie_container.pack(fill='both', expand=True, pady=10)
        
        self.update_cookie_fields()
    
    def create_proxy_section(self, parent):
        """Create proxy section with hacker style"""  
        section_frame = self.create_section_frame(parent, "🌐 PROXY NETWORK")
        
        # Proxy enable/disable
        proxy_control_frame = tk.Frame(section_frame, bg=self.hacker_colors['bg'])
        proxy_control_frame.pack(fill='x', pady=5)
        
        self.use_proxy_var = tk.BooleanVar()
        proxy_check = tk.Checkbutton(
            proxy_control_frame,
            text="ENABLE PROXY CLOAKING",
            variable=self.use_proxy_var,
            font=('Courier New', 10, 'bold'),
            fg=self.hacker_colors['accent'],
            bg=self.hacker_colors['bg'],
            selectcolor=self.hacker_colors['panel'],
            activebackground=self.hacker_colors['bg'],
            activeforeground=self.hacker_colors['success'],
            command=self.toggle_proxy_fields
        )
        proxy_check.pack(anchor='w')
        
        # Proxy mode selection
        proxy_mode_frame = tk.Frame(section_frame, bg=self.hacker_colors['bg'])
        proxy_mode_frame.pack(fill='x', pady=5)
        
        tk.Label(
            proxy_mode_frame,
            text="PROXY MODE:",
            font=('Courier New', 10, 'bold'),
            fg=self.hacker_colors['warning'],
            bg=self.hacker_colors['bg']
        ).pack(anchor='w')
        
        self.proxy_mode_var = tk.StringVar(value="rieng")
        
        modes = [("INDIVIDUAL", "rieng"), ("SHARED", "chung")]
        mode_frame = tk.Frame(proxy_mode_frame, bg=self.hacker_colors['bg'])
        mode_frame.pack(anchor='w', pady=(5, 0))
        
        for text, value in modes:
            tk.Radiobutton(
                mode_frame,
                text=text,
                variable=self.proxy_mode_var,
                value=value,
                font=('Courier New', 9, 'bold'),
                fg=self.hacker_colors['info'],
                bg=self.hacker_colors['bg'],
                selectcolor=self.hacker_colors['panel'],
                activebackground=self.hacker_colors['bg'],
                activeforeground=self.hacker_colors['success'],
                command=self.toggle_proxy_mode
            ).pack(side='left', padx=(0, 20))
        
        # Proxy type selection
        proxy_type_frame = tk.Frame(section_frame, bg=self.hacker_colors['bg'])
        proxy_type_frame.pack(fill='x', pady=5)
        
        tk.Label(
            proxy_type_frame,
            text="PROXY TYPE:",
            font=('Courier New', 10, 'bold'),
            fg=self.hacker_colors['warning'],
            bg=self.hacker_colors['bg']
        ).pack(anchor='w')
        
        self.proxy_type_var = tk.StringVar(value="static_ipv6")
        
        types = [("STATIC IPv6", "static_ipv6"), ("ROTATING IPv6", "rotating_ipv6")]
        type_frame = tk.Frame(proxy_type_frame, bg=self.hacker_colors['bg'])
        type_frame.pack(anchor='w', pady=(5, 0))
        
        for text, value in types:
            tk.Radiobutton(
                type_frame,
                text=text,
                variable=self.proxy_type_var,
                value=value,
                font=('Courier New', 9, 'bold'),
                fg=self.hacker_colors['info'],
                bg=self.hacker_colors['bg'],
                selectcolor=self.hacker_colors['panel'],
                activebackground=self.hacker_colors['bg'],
                activeforeground=self.hacker_colors['success'],
                command=self.update_proxy_placeholders
            ).pack(side='left', padx=(0, 20))
        
        # Proxy fields container
        self.proxy_container = tk.Frame(section_frame, bg=self.hacker_colors['bg'])
        self.proxy_container.pack(fill='both', expand=True, pady=10)
        
        self.toggle_proxy_fields()
    
    def create_control_section(self, parent):
        """Create control buttons section with hacker style"""
        section_frame = self.create_section_frame(parent, "⚡ MISSION CONTROL")
        
        # Main control buttons
        button_frame = tk.Frame(section_frame, bg=self.hacker_colors['bg'])
        button_frame.pack(fill='x', pady=10)
        
        # Start button
        self.start_button = tk.Button(
            button_frame,
            text="🚀 INITIATE ATTACK",
            font=('Courier New', 12, 'bold'),
            bg=self.hacker_colors['success'],
            fg='black',
            relief='raised',
            bd=3,
            padx=20,
            pady=10,
            command=self.start_automation,
            cursor='hand2'
        )
        self.start_button.pack(side='left', padx=(0, 10))
        
        # Stop button
        self.stop_button = tk.Button(
            button_frame,
            text="🛑 ABORT MISSION",
            font=('Courier New', 12, 'bold'),
            bg=self.hacker_colors['warning'],
            fg='white',
            relief='raised',
            bd=3,
            padx=20,
            pady=10,
            command=self.stop_automation,
            cursor='hand2',
            state='disabled'
        )
        self.stop_button.pack(side='left', padx=(0, 10))
        
        # Clear log button
        clear_button = tk.Button(
            button_frame,
            text="🗑️ CLEAR LOG",
            font=('Courier New', 10, 'bold'),
            bg=self.hacker_colors['button'],
            fg=self.hacker_colors['fg'],
            relief='raised',
            bd=2,
            padx=15,
            pady=5,
            command=self.clear_log,
            cursor='hand2'
        )
        clear_button.pack(side='left')
        
        # Status indicator
        self.status_label = tk.Label(
            section_frame,
            text="STATUS: STANDBY",
            font=('Courier New', 11, 'bold'),
            fg=self.hacker_colors['info'],
            bg=self.hacker_colors['bg']
        )
        self.status_label.pack(anchor='w', pady=(10, 0))
    
    def create_log_section(self, parent):
        """Create log section with hacker style"""
        section_frame = self.create_section_frame(parent, "📋 SYSTEM LOG")
        
        # Log text area
        log_container = tk.Frame(section_frame, bg=self.hacker_colors['bg'])
        log_container.pack(fill='both', expand=True, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(
            log_container,
            font=('Courier New', 9),
            bg=self.hacker_colors['input'],
            fg=self.hacker_colors['fg'],
            insertbackground=self.hacker_colors['fg'],
            relief='solid',
            bd=1,
            height=15,
            wrap=tk.WORD
        )
        self.log_text.pack(fill='both', expand=True)
        
        # Configure log colors
        self.log_text.tag_configure("info", foreground=self.hacker_colors['info'])
        self.log_text.tag_configure("success", foreground=self.hacker_colors['success'])
        self.log_text.tag_configure("warning", foreground=self.hacker_colors['warning'])
        self.log_text.tag_configure("error", foreground="#ff6b6b")
    
    def create_section_frame(self, parent, title):
        """Create a styled section frame"""
        # Main section frame
        section = tk.Frame(
            parent,
            bg=self.hacker_colors['panel'],
            relief='solid',
            bd=1,
            highlightbackground=self.hacker_colors['accent'],
            highlightthickness=1
        )
        section.pack(fill='x', pady=10, padx=5)
        
        # Section title
        title_frame = tk.Frame(section, bg=self.hacker_colors['accent'])
        title_frame.pack(fill='x')
        
        tk.Label(
            title_frame,
            text=title,
            font=('Courier New', 11, 'bold'),
            fg='black',
            bg=self.hacker_colors['accent'],
            pady=8
        ).pack()
        
        # Content frame
        content_frame = tk.Frame(section, bg=self.hacker_colors['bg'])
        content_frame.pack(fill='both', expand=True, padx=15, pady=15)
        
        return content_frame
    
    def log_message(self, message, tag="info"):
        """Thêm message vào log text area với hacker style"""
        # Check if log_text exists yet (setup_ui might not be complete)
        if not hasattr(self, 'log_text'):
            print(f"[LOG] {message}")  # Fallback to console
            return
            
        timestamp = time.strftime("%H:%M:%S")
        message_with_timestamp = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, message_with_timestamp, tag)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def on_account_count_change(self, event):
        """Xử lý khi người dùng thay đổi số lượng tài khoản"""
        try:
            count = int(self.account_count_var.get())
            if count <= 0:
                count = 1
                self.account_count_var.set("1")
            elif count > 10:  # Giới hạn tối đa 10 tài khoản
                count = 10
                self.account_count_var.set("10")
                self.log_message("⚠️ Giới hạn tối đa 10 tài khoản!")
        except ValueError:
            pass  # Ignore invalid input
    
    def update_cookie_fields(self):
        """Cập nhật số lượng cookie fields theo input"""
        try:
            count = int(self.num_accounts_var.get())
            if count <= 0:
                count = 1
                self.num_accounts_var.set(1)
            elif count > 10:
                count = 10
                self.num_accounts_var.set(10)
                
            self.create_cookie_fields(count)
            
            # Cập nhật proxy fields nếu đang ở chế độ riêng
            if self.use_proxy_var.get() and self.proxy_mode_var.get() == "rieng":
                self.create_proxy_fields(count)
                
            self.log_message(f"🔧 Updated {count} agent cookie fields" + 
                           (" and proxy" if self.use_proxy_var.get() and self.proxy_mode_var.get() == "rieng" else ""))
            
        except ValueError:
            self.log_message("❌ Invalid agent count!")
            self.num_accounts_var.set(1)
    
    def create_cookie_fields(self, count):
        """Tạo số lượng cookie fields theo yêu cầu với hacker style"""
        # Clear existing fields
        for widget in self.cookie_container.winfo_children():
            widget.destroy()
        self.cookie_fields = []
        
        self.current_account_count = count
        
        # Create scrollable frame for cookie fields
        canvas = tk.Canvas(
            self.cookie_container, 
            height=200,
            bg=self.hacker_colors['bg'],
            highlightthickness=0
        )
        scrollbar = tk.Scrollbar(
            self.cookie_container, 
            orient="vertical", 
            command=canvas.yview,
            bg=self.hacker_colors['panel'],
            troughcolor=self.hacker_colors['bg'],
            activebackground=self.hacker_colors['accent']
        )
        scrollable_frame = tk.Frame(canvas, bg=self.hacker_colors['bg'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Create cookie fields với hacker style
        for i in range(count):
            # Frame cho mỗi cookie field
            field_frame = tk.LabelFrame(
                scrollable_frame, 
                text=f"🤖 AGENT {i+1:02d} COOKIES",
                font=('Courier New', 10, 'bold'),
                fg=self.hacker_colors['accent'],
                bg=self.hacker_colors['bg'],
                relief='solid',
                bd=1,
                labelanchor='n'
            )
            field_frame.pack(fill="x", padx=5, pady=5)
            field_frame.columnconfigure(0, weight=1)
            
            # Cookie text area với hacker style
            cookie_text = scrolledtext.ScrolledText(
                field_frame, 
                height=4, 
                width=70, 
                wrap=tk.WORD,
                font=('Courier New', 9),
                bg=self.hacker_colors['input'],
                fg=self.hacker_colors['fg'],
                insertbackground=self.hacker_colors['fg'],
                relief='solid',
                bd=1
            )
            cookie_text.pack(fill="x", padx=5, pady=5)
            
            # Placeholder text
            placeholder = f"""[CLASSIFIED] Agent {i+1:02d} Authentication Tokens:
tt_csrf_token=<ENCRYPTED>; sessionid=<SECRET>; passport_csrf_token=<TOKEN>; ..."""
            cookie_text.insert("1.0", placeholder)
            cookie_text.config(fg="gray")
            
            # Bind events cho placeholder
            cookie_text.bind("<FocusIn>", lambda e, widget=cookie_text, idx=i: self.on_cookie_focus_in_multi(e, widget, idx))
            cookie_text.bind("<FocusOut>", lambda e, widget=cookie_text, idx=i: self.on_cookie_focus_out_multi(e, widget, idx))
            
            self.cookie_fields.append(cookie_text)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel to canvas
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", on_mousewheel)
    
    def on_cookie_focus_in_multi(self, event, widget, account_index):
        """Xử lý focus in cho cookie field"""
        current_text = widget.get("1.0", tk.END).strip()
        if "[CLASSIFIED]" in current_text or current_text.startswith(f"Nhập cookie cho tài khoản {account_index+1}"):
            widget.delete("1.0", tk.END)
            widget.config(fg=self.hacker_colors['fg'])
    
    def on_cookie_focus_out_multi(self, event, widget, account_index):
        """Xử lý focus out cho cookie field"""
        current_text = widget.get("1.0", tk.END).strip()
        if not current_text:
            placeholder = f"""[CLASSIFIED] Agent {account_index+1:02d} Authentication Tokens:
tt_csrf_token=<ENCRYPTED>; sessionid=<SECRET>; passport_csrf_token=<TOKEN>; ..."""
            widget.insert("1.0", placeholder)
            widget.config(fg="gray")
    
    def on_proxy_toggle(self):
        """Xử lý khi checkbox proxy được toggle - Updated for hacker UI"""
        if self.use_proxy_var.get():
            # Show proxy container
            if hasattr(self, 'proxy_container'):
                self.proxy_container.pack(fill='both', expand=True, pady=10)
            self.on_proxy_mode_change()  # Cập nhật hiển thị proxy fields
            self.log_message("✅ Đã bật tính năng proxy", "success")
        else:
            # Hide proxy container
            if hasattr(self, 'proxy_container'):
                self.proxy_container.pack_forget()
            self.log_message("❌ Đã tắt tính năng proxy", "warning")
    
    def on_proxy_mode_change(self):
        """Xử lý khi thay đổi chế độ proxy - Updated for hacker UI"""
        if not self.use_proxy_var.get():
            return
            
        mode = self.proxy_mode_var.get()
        if mode == "chung":
            self.log_message("📡 Chế độ proxy: SHARED - All agents use global tunnel", "info")
            # For shared mode, we could show a single shared proxy field
            # For now, just update the log message
        else:  # rieng  
            self.log_message("📡 Chế độ proxy: INDIVIDUAL - Each agent has separate tunnel", "info")
            # For individual mode, create proxy fields for each account
            if hasattr(self, 'current_account_count'):
                self.create_proxy_fields(self.current_account_count)
    
    def on_shared_proxy_focus_in(self, event):
        """Xử lý focus in cho shared proxy field"""
        current_text = self.shared_proxy_text.get("1.0", tk.END).strip()
        if current_text.startswith("Nhập proxy chung"):
            self.shared_proxy_text.delete("1.0", tk.END)
            self.shared_proxy_text.config(fg="black")
    
    def on_shared_proxy_focus_out(self, event):
        """Xử lý focus out cho shared proxy field"""
        current_text = self.shared_proxy_text.get("1.0", tk.END).strip()
        if not current_text:
            placeholder = """Nhập proxy chung (ví dụ):
HOST:PORT
45.32.149.59:49088

HOST:PORT SOCKS5
45.32.149.59:59088

Tên người dùng
user49088

Mật khẩu
grE0S8LQh0"""
            self.shared_proxy_text.insert("1.0", placeholder)
            self.shared_proxy_text.config(fg="gray")
    
    def toggle_proxy_fields(self):
        """Alias for on_proxy_toggle - compatibility with hacker UI"""
        return self.on_proxy_toggle()
    
    def toggle_proxy_mode(self):
        """Alias for on_proxy_mode_change - compatibility with hacker UI"""  
        return self.on_proxy_mode_change()
    
    def update_proxy_placeholders(self):
        """Update proxy placeholders when proxy type changes"""
        if hasattr(self, 'proxy_fields') and self.proxy_fields:
            for i, proxy_field in enumerate(self.proxy_fields):
                if proxy_field.winfo_exists():
                    proxy_type = self.proxy_type_var.get()
                    placeholder = self.get_proxy_placeholder_hacker(i+1, proxy_type)
                    current_text = proxy_field.get("1.0", tk.END).strip()
                    if "[ENCRYPTED]" in current_text or not current_text:
                        proxy_field.delete("1.0", tk.END)
                        proxy_field.insert("1.0", placeholder)
                        proxy_field.config(fg="gray")
    
    def start_automation(self):
        """Alias for start_login - compatibility with hacker UI"""
        return self.start_login()
    
    def stop_automation(self):
        """Alias for stop_login - compatibility with hacker UI"""
        return self.stop_login()
    
    def clear_log(self):
        """Clear the log text area"""
        if hasattr(self, 'log_text'):
            self.log_text.delete('1.0', tk.END)
            self.log_message("📋 System log cleared", "info")
    
    def open_facebook(self):
        """Mở link Facebook của tác giả"""
        import webbrowser
        webbrowser.open("https://www.facebook.com/dvfb.anhtu")
        self.log_message("🌐 Opening Facebook profile...", "info")
    
    def create_proxy_fields(self, count):
        """Tạo số lượng proxy fields theo yêu cầu với hacker style"""
        # Clear existing fields
        for widget in self.proxy_container.winfo_children():
            widget.destroy()
        self.proxy_fields.clear()
        
        # Create scrollable frame for proxy fields với hacker style
        canvas = tk.Canvas(
            self.proxy_container,
            height=180,
            bg=self.hacker_colors['bg'],
            highlightthickness=0
        )
        scrollbar = tk.Scrollbar(
            self.proxy_container,
            orient="vertical",
            command=canvas.yview,
            bg=self.hacker_colors['panel'],
            troughcolor=self.hacker_colors['bg'],
            activebackground=self.hacker_colors['accent']
        )
        scrollable_frame = tk.Frame(canvas, bg=self.hacker_colors['bg'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Create proxy fields với hacker style
        for i in range(count):
            # Frame cho mỗi proxy field
            field_frame = tk.LabelFrame(
                scrollable_frame,
                text=f"🌐 PROXY TUNNEL {i+1:02d}",
                font=('Courier New', 10, 'bold'),
                fg=self.hacker_colors['accent'],
                bg=self.hacker_colors['bg'],
                relief='solid',
                bd=1,
                labelanchor='n'
            )
            field_frame.pack(fill="x", padx=5, pady=5)
            field_frame.columnconfigure(0, weight=1)
            
            # Proxy text area với hacker style
            proxy_text = scrolledtext.ScrolledText(
                field_frame,
                height=4,
                width=70,
                wrap=tk.WORD,
                font=('Courier New', 9),
                bg=self.hacker_colors['input'],
                fg=self.hacker_colors['fg'],
                insertbackground=self.hacker_colors['fg'],
                relief='solid',
                bd=1
            )
            proxy_text.pack(fill="x", padx=5, pady=5)
            
            # Placeholder text với hacker style
            proxy_type = self.proxy_type_var.get()
            placeholder = self.get_proxy_placeholder_hacker(i+1, proxy_type)
            proxy_text.insert("1.0", placeholder)
            proxy_text.config(fg="gray")
            
            # Bind events cho placeholder
            proxy_text.bind("<FocusIn>", lambda e, widget=proxy_text, idx=i: self.on_proxy_focus_in_multi(e, widget, idx))
            proxy_text.bind("<FocusOut>", lambda e, widget=proxy_text, idx=i: self.on_proxy_focus_out_multi(e, widget, idx))
            
            self.proxy_fields.append(proxy_text)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel to canvas
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", on_mousewheel)
    
    def get_proxy_placeholder_hacker(self, account_num, proxy_type):
        """Tạo placeholder text cho proxy field với hacker style"""
        if proxy_type == "static_ipv6":
            return f"""[ENCRYPTED] Tunnel {account_num:02d} - Static IPv6 Protocol:

>>> SECURE FORMAT (RECOMMENDED):
user49088:grE0S8LQh0@45.32.149.59:49088

>>> ALTERNATIVE:
HOST:PORT
45.32.149.59:49088
USER:PASS
user49088:grE0S8LQh0"""
        else:
            return f"""[ENCRYPTED] Tunnel {account_num:02d} - Rotating IPv6 Protocol:

>>> SECURE FORMAT (RECOMMENDED):
user49088:grE0S8LQh0@45.32.149.59:49088

>>> ALTERNATIVE:
HOST:PORT
45.32.149.59:49088
USER:PASS
user49088:grE0S8LQh0"""
    
    # get_proxy_placeholder method removed - replaced with get_proxy_placeholder_hacker
    
    
    def on_proxy_focus_in_multi(self, event, widget, account_index):
        """Xử lý focus in cho proxy field"""
        current_text = widget.get("1.0", tk.END).strip()
        if current_text.startswith(f"Nhập proxy cho tài khoản {account_index+1}"):
            widget.delete("1.0", tk.END)
            widget.config(fg="black")
    
    def on_proxy_focus_out_multi(self, event, widget, account_index):
        """Xử lý focus out cho proxy field"""
        current_text = widget.get("1.0", tk.END).strip()
        if not current_text:
            proxy_type = self.proxy_type_var.get()
            placeholder = self.get_proxy_placeholder(account_index+1, proxy_type)
            widget.insert("1.0", placeholder)
            widget.config(fg="gray")
    
    def parse_cookies(self, cookie_string):
        """Parse cookie string thành dictionary"""
        cookies = {}
        if not cookie_string.strip():
            return cookies
            
        # Loại bỏ placeholder text nếu có
        if "Nhập cookie cho tài khoản" in cookie_string or cookie_string.strip().startswith("Nhập cookie ở đây"):
            return cookies
            
        # Split cookies by semicolon
        cookie_pairs = cookie_string.split(';')
        
        for pair in cookie_pairs:
            pair = pair.strip()
            if '=' in pair:
                name, value = pair.split('=', 1)
                cookies[name.strip()] = value.strip()
        
        return cookies
    
    def parse_proxy(self, proxy_string):
        """Parse proxy string thành dictionary - hỗ trợ nhiều định dạng"""
        proxy_info = {}
        if not proxy_string.strip():
            self.log_message("⚠️ Empty proxy string")
            return proxy_info
            
        # Loại bỏ placeholder text nếu có
        if "Nhập proxy cho tài khoản" in proxy_string:
            self.log_message("⚠️ Placeholder text detected in proxy")
            return proxy_info
        
        proxy_string = proxy_string.strip()
        self.log_message(f"🔍 Parsing proxy string: {proxy_string}")
        
        # Kiểm tra định dạng mới: user:password@host:port
        if '@' in proxy_string and ':' in proxy_string:
            try:
                self.log_message("   📋 Detected user:pass@host:port format")
                # Split bằng @
                parts = proxy_string.split('@')
                if len(parts) == 2:
                    auth_part = parts[0]  # user:password
                    host_part = parts[1]  # host:port
                    
                    # Parse auth part
                    if ':' in auth_part:
                        username, password = auth_part.split(':', 1)
                        proxy_info['username'] = username.strip()
                        proxy_info['password'] = password.strip()
                        self.log_message(f"   📝 Username: {username.strip()}")
                        self.log_message(f"   📝 Password: ***")
                    
                    # Parse host part
                    if ':' in host_part:
                        host, port = host_part.rsplit(':', 1)  # rsplit để handle IPv6
                        proxy_info['http'] = f"{host.strip()}:{port.strip()}"
                        proxy_info['host'] = host.strip()
                        proxy_info['port'] = port.strip()
                        proxy_info['proxy_type'] = 'http'
                        
                        self.log_message(f"   📝 Host: {host.strip()}")
                        self.log_message(f"   📝 Port: {port.strip()}")
                        self.log_message(f"✅ Successfully parsed user:pass@host:port format")
                        return proxy_info
            except Exception as e:
                self.log_message(f"⚠️ Lỗi parse proxy format mới: {str(e)}")
        
        self.log_message("   📋 Trying legacy multi-line format")
        # Fallback về định dạng cũ nếu không match định dạng mới
        lines = proxy_string.split('\n')
        current_key = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Kiểm tra các pattern phổ biến
            if line.startswith('HOST:PORT') and 'SOCKS5' in line:
                current_key = 'socks5'
            elif line.startswith('HOST:PORT') and 'AUTHIP' in line:
                current_key = 'authip'
            elif line.startswith('HOST:PORT') or line.startswith('Proxy IP:PORT'):
                current_key = 'http'
            elif line.startswith('IPv6'):
                current_key = 'ipv6'
            elif line.startswith('Tên người dùng') or line.startswith('Username'):
                current_key = 'username'
            elif line.startswith('Mật khẩu') or line.startswith('Password'):
                current_key = 'password'
            elif line.startswith('Loại') or line.startswith('Type'):
                current_key = 'type'
            elif current_key and ':' in line and not any(x in line.lower() for x in ['host', 'proxy', 'tên', 'mật', 'loại', 'đổi', 'thời']):
                # Dòng chứa thông tin proxy (host:port)
                proxy_info[current_key] = line
            elif current_key in ['username', 'password', 'type'] and not ':' in line:
                # Dòng chứa thông tin username/password/type
                proxy_info[current_key] = line
        
        return proxy_info
    
    def get_proxy_config(self, proxy_info):
        """Chuyển proxy info thành config cho Selenium"""
        if not proxy_info:
            self.log_message("⚠️ No proxy info to configure")
            return None
            
        config = {}
        self.log_message(f"🔧 Converting proxy info to config: {list(proxy_info.keys())}")
        
        # Check if we have direct host/port from new format
        if 'host' in proxy_info and 'port' in proxy_info:
            config['host'] = proxy_info['host']
            config['port'] = proxy_info['port']
            config['proxy_type'] = proxy_info.get('proxy_type', 'http')
            self.log_message(f"   ✅ Direct host/port found: {config['host']}:{config['port']}")
        else:
            # Legacy format parsing
            # Ưu tiên SOCKS5, sau đó HTTP, cuối cùng AUTHIP
            if 'socks5' in proxy_info:
                parts = proxy_info['socks5'].split(':')
                if len(parts) >= 2:
                    config['proxy_type'] = 'socks5'
                    config['host'] = parts[0]
                    config['port'] = parts[1]
                    self.log_message(f"   ✅ SOCKS5 config: {config['host']}:{config['port']}")
            elif 'http' in proxy_info:
                parts = proxy_info['http'].split(':')
                if len(parts) >= 2:
                    config['proxy_type'] = 'http'
                    config['host'] = parts[0]
                    config['port'] = parts[1]
                    self.log_message(f"   ✅ HTTP config: {config['host']}:{config['port']}")
            elif 'authip' in proxy_info:
                parts = proxy_info['authip'].split(':')
                if len(parts) >= 2:
                    config['proxy_type'] = 'http'
                    config['host'] = parts[0]
                    config['port'] = parts[1]
                    self.log_message(f"   ✅ AUTHIP config: {config['host']}:{config['port']}")
        
        # Thêm username/password nếu có
        if 'username' in proxy_info:
            config['username'] = proxy_info['username']
            self.log_message(f"   📝 Username added: {config['username']}")
        if 'password' in proxy_info:
            config['password'] = proxy_info['password']
            self.log_message(f"   📝 Password added: ***")
            
        if 'host' in config and 'port' in config:
            self.log_message(f"✅ Proxy config created successfully")
            return config
        else:
            self.log_message(f"❌ Proxy config failed - missing host or port")
            return None
    
    def test_proxy_connection(self, proxy_config):
        """Test proxy connection trước khi sử dụng"""
        import socket
        import time
        import requests
        
        host = proxy_config['host']
        port = int(proxy_config['port'])
        
        self.log_message(f"🧪 Testing proxy: {host}:{port}")
        
        # Test 1: Basic TCP connection
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)  # 10 second timeout
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result == 0:
                self.log_message(f"   ✅ TCP connection successful")
            else:
                self.log_message(f"   ❌ TCP connection failed (Error: {result})")
                return False
                
        except Exception as e:
            self.log_message(f"   ❌ TCP connection exception: {str(e)}")
            return False
        
        # Test 2: HTTP request through proxy (if has auth)
        if 'username' in proxy_config and 'password' in proxy_config:
            try:
                proxy_url = f"http://{proxy_config['username']}:{proxy_config['password']}@{host}:{port}"
                proxies = {
                    'http': proxy_url,
                    'https': proxy_url
                }
                
                response = requests.get('http://httpbin.org/ip', proxies=proxies, timeout=15)
                
                if response.status_code == 200:
                    ip_info = response.json()
                    self.log_message(f"   ✅ HTTP request successful")
                    self.log_message(f"   🌐 IP through proxy: {ip_info.get('origin', 'Unknown')}")
                    return True
                else:
                    self.log_message(f"   ⚠️ HTTP request failed (Status: {response.status_code})")
                    return True  # Still consider TCP success as usable
                    
            except Exception as e:
                self.log_message(f"   ⚠️ HTTP test failed: {str(e)}")
                return True  # TCP worked, so proxy might still be usable
        
        return True  # TCP connection worked
    
    def create_proxy_auth_extension(self, proxy_config):
        """Tạo Chrome extension để handle proxy authentication"""
        if not ('username' in proxy_config and 'password' in proxy_config):
            return None
            
        import zipfile
        import tempfile
        
        proxy_host = proxy_config['host']
        proxy_port = proxy_config['port']
        proxy_username = proxy_config['username']
        proxy_password = proxy_config['password']
        
        # Manifest cho extension
        manifest_json = '''
{
    "version": "1.0.0",
    "manifest_version": 2,
    "name": "Chrome Proxy",
    "permissions": [
        "proxy",
        "tabs",
        "unlimitedStorage",
        "storage",
        "<all_urls>",
        "webRequest",
        "webRequestBlocking"
    ],
    "background": {
        "scripts": ["background.js"]
    },
    "minimum_chrome_version":"22.0.0"
}
'''
        
        # Background script để handle authentication
        background_js = f'''
var config = {{
        mode: "fixed_servers",
        rules: {{
          singleProxy: {{
            scheme: "http",
            host: "{proxy_host}",
            port: parseInt({proxy_port})
          }},
          bypassList: ["localhost"]
        }}
      }};

chrome.proxy.settings.set({{value: config, scope: "regular"}}, function() {{}});

function callbackFn(details) {{
    return {{
        authCredentials: {{
            username: "{proxy_username}",
            password: "{proxy_password}"
        }}
    }};
}}

chrome.webRequest.onAuthRequired.addListener(
            callbackFn,
            {{urls: ["<all_urls>"]}},
            ['blocking']
);
'''
        
        try:
            # Tạo thư mục tạm cho extension
            plugin_dir = tempfile.mkdtemp()
            self.log_message(f"   📁 Creating extension in: {plugin_dir}")
            
            # Tạo files
            manifest_path = f"{plugin_dir}/manifest.json"
            background_path = f"{plugin_dir}/background.js"
            
            with open(manifest_path, "w", encoding='utf-8') as f:
                f.write(manifest_json)
            
            with open(background_path, "w", encoding='utf-8') as f:
                f.write(background_js)
            
            self.log_message(f"   ✅ Extension files created")
            self.log_message(f"   📝 Manifest: {manifest_path}")
            self.log_message(f"   📝 Background: {background_path}")
            
            # Return the directory path instead of zip file for loading
            return plugin_dir
            
        except Exception as e:
            self.log_message(f"⚠️ Failed to create proxy auth extension: {str(e)}")
            return None
    
    def ask_continue_without_proxy(self):
        """Hỏi user có muốn tiếp tục không có proxy khi proxy fail"""
        import tkinter.messagebox as msgbox
        
        result = msgbox.askyesno(
            "Proxy Connection Failed", 
            "Proxy connection failed. Do you want to continue without proxy?\n\n"
            "Yes: Continue without proxy\n"
            "No: Stop the process"
        )
        return result
    
    def setup_basic_proxy(self, chrome_options, proxy_config, proxy_string):
        """Setup basic proxy configuration"""
        try:
            proxy_type = proxy_config.get('proxy_type', 'http')
            
            if proxy_type == 'socks5':
                chrome_options.add_argument(f"--proxy-server=socks5://{proxy_string}")
                self.log_message(f"   ✅ SOCKS5 proxy configured: {proxy_string}")
            else:  # http
                chrome_options.add_argument(f"--proxy-server=http://{proxy_string}")
                self.log_message(f"   ✅ HTTP proxy configured: {proxy_string}")
            
            # Add proxy-related arguments
            chrome_options.add_argument("--ignore-certificate-errors")
            chrome_options.add_argument("--ignore-ssl-errors")
            chrome_options.add_argument("--ignore-certificate-errors-spki-list")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--allow-running-insecure-content")
            
        except Exception as e:
            self.log_message(f"❌ Error setting up basic proxy: {str(e)}")
    
    def setup_driver(self, account_index=0):
        """Thiết lập Chrome driver cho một tài khoản"""
        try:
            self.log_message(f"Đang thiết lập Chrome driver cho tài khoản {account_index + 1}...")
            
            # Tạo thư mục profiles nếu chưa có
            profiles_dir = "./chrome_profiles"
            if not os.path.exists(profiles_dir):
                os.makedirs(profiles_dir)
            
            chrome_options = Options()
            
            # Các option cơ bản cho WebDriver
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-plugins")
            chrome_options.add_argument("--disable-images")  # Tăng tốc độ load
            # chrome_options.add_argument("--disable-javascript")  # Bỏ comment vì TikTok cần JS
            chrome_options.add_argument("--no-first-run")
            chrome_options.add_argument("--no-default-browser-check")
            chrome_options.add_argument("--disable-default-apps")
            chrome_options.add_argument("--disable-popup-blocking")
            
            # Tắt password manager và sync
            chrome_options.add_argument("--disable-password-generation")
            chrome_options.add_argument("--disable-save-password-bubble")
            chrome_options.add_argument("--disable-sync")
            
            # Profile directory riêng cho mỗi tài khoản
            profile_path = os.path.abspath(f"./chrome_profiles/profile_{account_index}")
            chrome_options.add_argument(f"--user-data-dir={profile_path}")
            
            # User agent
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            # Disable automation indicators
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Preferences để tránh popup và chọn profile
            prefs = {
                "profile.default_content_setting_values": {
                    "notifications": 2  # Block notifications
                },
                "profile.default_content_settings.popups": 0,
                "profile.managed_default_content_settings.images": 2  # Block images for speed
            }
            chrome_options.add_experimental_option("prefs", prefs)
            
            # Cấu hình proxy nếu được bật
            proxy_config = self.get_proxy_for_account(account_index)
            if proxy_config:
                proxy_string = f"{proxy_config['host']}:{proxy_config['port']}"
                
                # Kiểm tra proxy có auth không
                has_auth = 'username' in proxy_config and 'password' in proxy_config
                
                self.log_message(f"🔧 Configuring proxy for account {account_index + 1}...")
                self.log_message(f"   Host: {proxy_config['host']}")
                self.log_message(f"   Port: {proxy_config['port']}")
                self.log_message(f"   Type: {proxy_config.get('proxy_type', 'http')}")
                self.log_message(f"   Auth: {'Yes' if has_auth else 'No'}")
                
                # Test proxy connection trước
                proxy_working = False
                try:
                    proxy_working = self.test_proxy_connection(proxy_config)
                    if proxy_working:
                        self.log_message(f"✅ Proxy connection test successful")
                    else:
                        self.log_message(f"❌ Proxy connection test failed")
                        self.log_message(f"⚠️ WARNING: Proxy server appears to be offline or not working")
                        self.log_message(f"💡 You can:")
                        self.log_message(f"   1. Check proxy server status")
                        self.log_message(f"   2. Try a different proxy")
                        self.log_message(f"   3. Disable proxy to continue without it")
                        
                        # Ask user what to do
                        import tkinter.messagebox as msgbox
                        choice = msgbox.askyesnocancel(
                            "Proxy Connection Failed",
                            f"Proxy {proxy_string} is not working properly.\n\n"
                            f"• Yes: Continue WITH proxy (may fail)\n"
                            f"• No: Continue WITHOUT proxy (recommended)\n"
                            f"• Cancel: Stop and fix proxy settings"
                        )
                        
                        if choice is None:  # Cancel
                            self.log_message("❌ User cancelled due to proxy issues")
                            return None
                        elif choice is False:  # No - continue without proxy
                            self.log_message("🔄 User chose to continue WITHOUT proxy")
                            proxy_config = None  # Disable proxy
                        else:  # Yes - continue with proxy
                            self.log_message("⚠️ User chose to continue WITH broken proxy")
                            
                except Exception as proxy_error:
                    self.log_message(f"⚠️ Proxy test error: {str(proxy_error)}")
                
                # Cấu hình proxy nếu vẫn được enable
                if proxy_config and proxy_working or (proxy_config and not proxy_working):
                    if has_auth:
                        # Với proxy có auth, sử dụng extension
                        self.log_message(f"🔧 Setting up proxy with authentication...")
                        
                        plugin_file = self.create_proxy_auth_extension(proxy_config)
                        if plugin_file:
                            try:
                                # Load extension directory instead of zip file
                                chrome_options.add_argument(f"--load-extension={plugin_file}")
                                self.log_message(f"✅ Proxy auth extension loaded successfully")
                            except Exception as e:
                                self.log_message(f"⚠️ Failed to load extension: {str(e)}")
                                # Fallback to basic proxy
                                self.setup_basic_proxy(chrome_options, proxy_config, proxy_string)
                        else:
                            # Fallback to basic proxy
                            self.setup_basic_proxy(chrome_options, proxy_config, proxy_string)
                        
                        self.log_message(f"Proxy cho tài khoản {account_index + 1}: {proxy_string} (Auth: {proxy_config['username']})")
                    else:
                        # Proxy không có auth
                        self.setup_basic_proxy(chrome_options, proxy_config, proxy_string)
                        self.log_message(f"Proxy cho tài khoản {account_index + 1}: {proxy_string} (No auth)")
                else:
                    self.log_message("🚫 Proxy disabled - running with direct connection")
            else:
                self.log_message(f"Tài khoản {account_index + 1}: Không sử dụng proxy")
            
            # Khởi tạo driver
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Ẩn automation indicators
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Set window size
            driver.set_window_size(1200, 800)
            
            self.log_message(f"Chrome driver cho tài khoản {account_index + 1} đã được thiết lập thành công!")
            return driver
            
        except Exception as e:
            self.log_message(f"Lỗi khi thiết lập Chrome driver cho tài khoản {account_index + 1}: {str(e)}")
            return None
    
    def get_proxy_for_account(self, account_index):
        """Lấy proxy config cho một tài khoản cụ thể"""
        if not self.use_proxy_var.get():
            return None
            
        mode = self.proxy_mode_var.get()
        
        if mode == "chung":
            # Tất cả dùng chung proxy
            proxy_string = self.shared_proxy_text.get("1.0", tk.END).strip()
            proxy_info = self.parse_proxy(proxy_string)
            return self.get_proxy_config(proxy_info)
        else:  # rieng
            if account_index < len(self.proxy_fields):
                proxy_string = self.proxy_fields[account_index].get("1.0", tk.END).strip()
                proxy_info = self.parse_proxy(proxy_string)
                return self.get_proxy_config(proxy_info)
        
        return None
    
    def apply_cookies(self, driver, cookies, account_index=0):
        """Apply cookies vào browser session"""
        try:
            if not cookies:
                self.log_message(f"Không có cookie để apply cho tài khoản {account_index + 1}!")
                return False
                
            self.log_message(f"Đang apply {len(cookies)} cookies cho tài khoản {account_index + 1}...")
            
            # Đi đến TikTok trước để có thể set cookies
            url = self.url_var.get().strip()
            if not url:
                url = "https://www.tiktok.com"
            
            # Thử get trang với timeout và retry
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    self.log_message(f"🌐 Attempting to load {url} (Attempt {attempt + 1}/{max_retries})...")
                    
                    # Set timeout for page load
                    driver.set_page_load_timeout(30)
                    driver.get(url)
                    
                    # Wait for page to load
                    time.sleep(5)
                    
                    # Check if page loaded successfully
                    if "tiktok" in driver.current_url.lower():
                        self.log_message(f"✅ Page loaded successfully: {driver.current_url}")
                        break
                    else:
                        self.log_message(f"⚠️ Unexpected URL: {driver.current_url}")
                        
                except Exception as e:
                    self.log_message(f"❌ Failed to load page (Attempt {attempt + 1}): {str(e)}")
                    if attempt == max_retries - 1:
                        # Last attempt failed
                        if "ERR_TUNNEL_CONNECTION_FAILED" in str(e):
                            self.log_message("🔧 Error: Proxy tunnel connection failed")
                            self.log_message("💡 Suggestions:")
                            self.log_message("   - Check proxy server status")
                            self.log_message("   - Verify proxy credentials")
                            self.log_message("   - Try a different proxy")
                            self.log_message("   - Disable proxy temporarily")
                        elif "ERR_PROXY_CONNECTION_FAILED" in str(e):
                            self.log_message("🔧 Error: Cannot connect to proxy server")
                            self.log_message("💡 Check proxy host and port")
                        elif "TimeoutException" in str(e):
                            self.log_message("🔧 Error: Page load timeout")
                            self.log_message("💡 Try with faster internet or different proxy")
                        
                        return False
                    else:
                        time.sleep(3)  # Wait before retry
            
            # Apply từng cookie
            cookies_applied = 0
            for name, value in cookies.items():
                try:
                    driver.add_cookie({
                        'name': name,
                        'value': value,
                        'domain': '.tiktok.com'
                    })
                    cookies_applied += 1
                except Exception as e:
                    self.log_message(f"Không thể apply cookie {name} cho tài khoản {account_index + 1}: {str(e)}")
            
            self.log_message(f"✅ {cookies_applied}/{len(cookies)} cookies applied cho tài khoản {account_index + 1}!")
            return True
            
        except Exception as e:
            self.log_message(f"Lỗi khi apply cookies cho tài khoản {account_index + 1}: {str(e)}")
            return False
    
    def check_login_status(self, driver, account_index=0):
        """Kiểm tra trạng thái đăng nhập"""
        try:
            # Refresh trang để load cookies
            driver.refresh()
            time.sleep(5)
            
            # Kiểm tra các element cho biết đã đăng nhập
            try:
                # Tìm avatar hoặc profile menu
                avatar = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[data-e2e='nav-profile']"))
                )
                self.log_message(f"✅ Tài khoản {account_index + 1}: Đăng nhập thành công! Đã tìm thấy profile menu.")
                return True
            except:
                pass
            
            try:
                # Kiểm tra nút login
                login_button = driver.find_element(By.CSS_SELECTOR, "[data-e2e='top-login-button']")
                self.log_message(f"❌ Tài khoản {account_index + 1}: Chưa đăng nhập - vẫn thấy nút Login.")
                return False
            except:
                pass
            
            # Kiểm tra URL có chứa login không
            current_url = driver.current_url
            if "login" in current_url.lower():
                self.log_message(f"❌ Tài khoản {account_index + 1}: Đang ở trang login - chưa đăng nhập thành công.")
                return False
            
            self.log_message(f"⚠️ Tài khoản {account_index + 1}: Không thể xác định trạng thái đăng nhập.")
            return None
            
        except Exception as e:
            self.log_message(f"Lỗi khi kiểm tra trạng thái đăng nhập cho tài khoản {account_index + 1}: {str(e)}")
            return False
    
    def get_available_reporting_option(self):
        """Lấy một option báo cáo chưa được sử dụng"""
        # Lấy các option chưa được sử dụng
        available_options = [opt for opt in self.reporting_options if opt["id"] not in TikTokLoginApp.used_reporting_options]
        
        if not available_options:
            # Nếu đã dùng hết, reset lại
            TikTokLoginApp.used_reporting_options.clear()
            available_options = self.reporting_options
            self.log_message("🔄 Đã reset danh sách reporting options, bắt đầu lại từ đầu")
        
        # Random một option
        selected_option = random.choice(available_options)
        TikTokLoginApp.used_reporting_options.add(selected_option["id"])
        
        return selected_option
    
    def debug_available_reporting_options(self, driver, account_index=0):
        """Debug function để xem tất cả options báo cáo có sẵn"""
        try:
            self.log_message(f"🔍 Tài khoản {account_index + 1}: Đang scan tất cả options báo cáo có sẵn...")
            
            # Wait a bit for options to load
            time.sleep(3)
            
            # Try to find all reporting options
            reason_elements = driver.find_elements(By.CSS_SELECTOR, '[data-e2e="report-card-reason"]')
            
            if reason_elements:
                self.log_message(f"📋 Tài khoản {account_index + 1}: Tìm thấy {len(reason_elements)} options:")
                
                for i, element in enumerate(reason_elements):
                    try:
                        reason_text_element = element.find_element(By.CSS_SELECTOR, '.css-1hnazpm-5e6d46e3--DivReasonText')
                        reason_text = reason_text_element.text.strip()
                        self.log_message(f"  {i+1}. '{reason_text}'")
                    except:
                        try:
                            # Try alternative selector
                            reason_text = element.text.strip()
                            self.log_message(f"  {i+1}. '{reason_text}' (alt)")
                        except:
                            self.log_message(f"  {i+1}. (Không đọc được text)")
            else:
                self.log_message(f"❌ Tài khoản {account_index + 1}: Không tìm thấy options báo cáo nào")
                
                # Try alternative selectors
                alternative_selectors = [
                    'label[data-e2e*="report"]',
                    '.css-1kma92a-5e6d46e3--LabelRadio',
                    '[role="radio"]',
                    'input[type="radio"]',
                    '.TUXRadio'
                ]
                
                for selector in alternative_selectors:
                    try:
                        alt_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                        if alt_elements:
                            self.log_message(f"🔄 Tài khoản {account_index + 1}: Tìm thấy {len(alt_elements)} elements với selector: {selector}")
                            break
                    except:
                        continue
                        
        except Exception as e:
            self.log_message(f"❌ Tài khoản {account_index + 1}: Lỗi debug: {str(e)}")
    
    def perform_reporting_workflow(self, driver, account_index=0):
        """Thực hiện quy trình báo cáo video"""
        try:
            self.log_message(f"📋 Tài khoản {account_index + 1}: Bắt đầu quy trình báo cáo...")
            
            # Step 1: Click more menu button
            try:
                more_menu_selector = '[data-e2e="more-menu"]'
                more_menu = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, more_menu_selector))
                )
                
                # Scroll to element
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", more_menu)
                time.sleep(1)
                
                # Click more menu
                driver.execute_script("arguments[0].click();", more_menu)
                self.log_message(f"✅ Tài khoản {account_index + 1}: Đã click more menu")
                time.sleep(2)
                
            except Exception as e:
                self.log_message(f"❌ Tài khoản {account_index + 1}: Lỗi khi click more menu: {str(e)}")
                return False
            
            # Step 2: Click Report option
            try:
                report_selector = '[data-e2e="more-menu-popover_report"]'
                report_option = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, report_selector))
                )
                
                driver.execute_script("arguments[0].click();", report_option)
                self.log_message(f"✅ Tài khoản {account_index + 1}: Đã click Report")
                time.sleep(3)
                
                # Debug: Check available options
                self.debug_available_reporting_options(driver, account_index)
                
            except Exception as e:
                self.log_message(f"❌ Tài khoản {account_index + 1}: Lỗi khi click Report: {str(e)}")
                return False
            
            # Step 3: Select reporting reasons
            selected_option = self.get_available_reporting_option()
            self.log_message(f"🎯 Tài khoản {account_index + 1}: Chọn option {selected_option['id']}: {selected_option['primary']}")
            
            try:
                # Wait for reporting options to load
                time.sleep(3)
                
                # Try multiple selectors for finding reporting reasons
                primary_found = False
                
                # Method 1: Try with exact text match using data-e2e
                try:
                    primary_selector = f'[data-e2e="report-card-reason"]'
                    reason_elements = WebDriverWait(driver, 10).until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, primary_selector))
                    )
                    
                    self.log_message(f"🔍 Tài khoản {account_index + 1}: Tìm thấy {len(reason_elements)} lựa chọn báo cáo")
                    
                    for element in reason_elements:
                        try:
                            # Get the text content of the reason
                            reason_text_element = element.find_element(By.CSS_SELECTOR, '.css-1hnazpm-5e6d46e3--DivReasonText')
                            reason_text = reason_text_element.text.strip()
                            
                            self.log_message(f"🔍 Tài khoản {account_index + 1}: Kiểm tra lý do: '{reason_text}'")
                            
                            if reason_text == selected_option['primary']:
                                # Scroll to element and click
                                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
                                time.sleep(1)
                                driver.execute_script("arguments[0].click();", element)
                                self.log_message(f"✅ Tài khoản {account_index + 1}: Đã chọn lý do chính: {selected_option['primary']}")
                                primary_found = True
                                time.sleep(2)
                                break
                        except Exception as inner_e:
                            self.log_message(f"⚠️ Tài khoản {account_index + 1}: Lỗi kiểm tra element: {str(inner_e)}")
                            continue
                    
                except Exception as e:
                    self.log_message(f"⚠️ Tài khoản {account_index + 1}: Method 1 failed: {str(e)}")
                
                # Method 2: If method 1 fails, try with XPath
                if not primary_found:
                    try:
                        primary_xpath = f"//div[contains(text(), '{selected_option['primary']}')]"
                        primary_elements = driver.find_elements(By.XPATH, primary_xpath)
                        
                        for element in primary_elements:
                            try:
                                # Find the clickable parent (label)
                                clickable_parent = element.find_element(By.XPATH, "./ancestor::label[@data-e2e='report-card-reason']")
                                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", clickable_parent)
                                time.sleep(1)
                                driver.execute_script("arguments[0].click();", clickable_parent)
                                self.log_message(f"✅ Tài khoản {account_index + 1}: Đã chọn lý do chính (XPath): {selected_option['primary']}")
                                primary_found = True
                                time.sleep(2)
                                break
                            except:
                                continue
                    except Exception as e:
                        self.log_message(f"⚠️ Tài khoản {account_index + 1}: Method 2 failed: {str(e)}")
                
                # Method 3: If still not found, try partial text match
                if not primary_found:
                    try:
                        # Try with partial text match
                        primary_words = selected_option['primary'].split()
                        for word in primary_words[:3]:  # Use first 3 words
                            if len(word) > 3:  # Only use meaningful words
                                partial_xpath = f"//div[contains(text(), '{word}')]"
                                partial_elements = driver.find_elements(By.XPATH, partial_xpath)
                                
                                for element in partial_elements:
                                    try:
                                        element_text = element.text.strip()
                                        if selected_option['primary'].lower() in element_text.lower():
                                            clickable_parent = element.find_element(By.XPATH, "./ancestor::label[@data-e2e='report-card-reason']")
                                            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", clickable_parent)
                                            time.sleep(1)
                                            driver.execute_script("arguments[0].click();", clickable_parent)
                                            self.log_message(f"✅ Tài khoản {account_index + 1}: Đã chọn lý do chính (Partial): {selected_option['primary']}")
                                            primary_found = True
                                            time.sleep(2)
                                            break
                                    except:
                                        continue
                                if primary_found:
                                    break
                    except Exception as e:
                        self.log_message(f"⚠️ Tài khoản {account_index + 1}: Method 3 failed: {str(e)}")
                
                if not primary_found:
                    # Method 4: Fallback - Just click the first available option
                    try:
                        self.log_message(f"🔄 Tài khoản {account_index + 1}: Fallback - chọn option đầu tiên có sẵn")
                        reason_elements = driver.find_elements(By.CSS_SELECTOR, '[data-e2e="report-card-reason"]')
                        
                        if reason_elements and len(reason_elements) > 0:
                            first_element = reason_elements[0]
                            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", first_element)
                            time.sleep(1)
                            driver.execute_script("arguments[0].click();", first_element)
                            self.log_message(f"✅ Tài khoản {account_index + 1}: Đã chọn option đầu tiên (fallback)")
                            primary_found = True
                            time.sleep(2)
                    except Exception as e:
                        self.log_message(f"⚠️ Tài khoản {account_index + 1}: Fallback failed: {str(e)}")
                
                if not primary_found:
                    self.log_message(f"❌ Tài khoản {account_index + 1}: Không thể tìm thấy lý do chính: {selected_option['primary']}")
                    return False
                
                # Click secondary reason if exists
                if selected_option["secondary"]:
                    secondary_found = False
                    time.sleep(2)  # Wait for page to update
                    
                    try:
                        # Special handling for "Harassment and bullying" with 4 sub-options
                        if selected_option['secondary'] == "Harassment and bullying":
                            secondary_found = self.handle_harassment_bullying_suboptions(driver, account_index)
                        else:
                            # Normal secondary handling
                            secondary_found = self.handle_normal_secondary_option(driver, account_index, selected_option)
                        
                        if not secondary_found:
                            self.log_message(f"⚠️ Tài khoản {account_index + 1}: Không tìm thấy lý do phụ: {selected_option['secondary']}")
                        
                    except Exception as e:
                        self.log_message(f"⚠️ Tài khoản {account_index + 1}: Lỗi khi chọn lý do phụ: {str(e)}")
                
            except Exception as e:
                self.log_message(f"❌ Tài khoản {account_index + 1}: Lỗi khi chọn lý do báo cáo: {str(e)}")
                return False
            
            # Step 4: Click Submit
            submit_success = False
            try:
                # Try multiple selectors for Submit button
                submit_selectors = [
                    '.css-vuhncw-5e6d46e3--ButtonSubmit',
                    '[data-e2e*="submit"]',
                    'button[type="submit"]',
                    'button:contains("Submit")',
                    '.TUXButton--primary'
                ]
                
                for selector in submit_selectors:
                    try:
                        submit_button = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )
                        
                        driver.execute_script("arguments[0].click();", submit_button)
                        self.log_message(f"✅ Tài khoản {account_index + 1}: Đã click Submit với selector: {selector}")
                        submit_success = True
                        time.sleep(3)
                        break
                    except:
                        continue
                
                if not submit_success:
                    # Try finding submit button by text
                    submit_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Submit') or contains(text(), 'Gửi')]")
                    if submit_buttons:
                        driver.execute_script("arguments[0].click();", submit_buttons[0])
                        self.log_message(f"✅ Tài khoản {account_index + 1}: Đã click Submit (by text)")
                        submit_success = True
                        time.sleep(3)
                
                if not submit_success:
                    self.log_message(f"❌ Tài khoản {account_index + 1}: Không tìm thấy nút Submit")
                    return False
                
            except Exception as e:
                self.log_message(f"❌ Tài khoản {account_index + 1}: Lỗi khi click Submit: {str(e)}")
                return False
            
            # Step 5: Click Done
            done_success = False
            try:
                # Try multiple selectors for Done button
                done_selectors = [
                    '.css-vzks70-5e6d46e3--ButtonFinish',
                    '[data-e2e*="done"]',
                    '[data-e2e*="finish"]',
                    'button:contains("Done")',
                    '.TUXButton--secondary'
                ]
                
                for selector in done_selectors:
                    try:
                        done_button = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )
                        
                        driver.execute_script("arguments[0].click();", done_button)
                        self.log_message(f"✅ Tài khoản {account_index + 1}: Đã click Done với selector: {selector}")
                        done_success = True
                        time.sleep(2)
                        break
                    except:
                        continue
                
                if not done_success:
                    # Try finding done button by text
                    done_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Done') or contains(text(), 'Xong') or contains(text(), 'Hoàn thành')]")
                    if done_buttons:
                        driver.execute_script("arguments[0].click();", done_buttons[0])
                        self.log_message(f"✅ Tài khoản {account_index + 1}: Đã click Done (by text)")
                        done_success = True
                        time.sleep(2)
                
                if done_success:
                    self.log_message(f"🎉 Tài khoản {account_index + 1}: Hoàn thành báo cáo!")
                    return True
                else:
                    self.log_message(f"⚠️ Tài khoản {account_index + 1}: Không tìm thấy nút Done, nhưng có thể đã submit thành công")
                    return True  # Consider it success even if Done button not found
                
            except Exception as e:
                self.log_message(f"❌ Tài khoản {account_index + 1}: Lỗi khi click Done: {str(e)}")
                return False
                
        except Exception as e:
            self.log_message(f"❌ Tài khoản {account_index + 1}: Lỗi trong quy trình báo cáo: {str(e)}")
            return False
    
    def handle_harassment_bullying_suboptions(self, driver, account_index):
        """Handle sub-options cho Harassment and bullying với 4 lựa chọn random"""
        harassment_suboptions = [
            "I have been bullied or harassed",
            "Someone I know has been bullied or harassed", 
            "A celebrity or government official has been bullied or harassed",
            "Others have been bullied or harassed"
        ]
        
        # Chọn random 1 trong 4 options
        selected_suboption = random.choice(harassment_suboptions)
        self.log_message(f"🎯 Tài khoản {account_index + 1}: Chọn Harassment sub-option: {selected_suboption}")
        
        return self.click_suboption_by_text(driver, account_index, selected_suboption)
    
    def handle_normal_secondary_option(self, driver, account_index, selected_option):
        """Handle secondary options bình thường và các special cases"""
        secondary_text = selected_option['secondary']
        
        # Special case for "Deceptive behavior and spam" - random between 2 sub-options
        if secondary_text == "Fake engagement" or secondary_text == "Spam":
            spam_suboptions = ["Fake engagement", "Spam"]
            selected_suboption = random.choice(spam_suboptions)
            self.log_message(f"🎯 Tài khoản {account_index + 1}: Chọn Spam sub-option: {selected_suboption}")
            return self.click_suboption_by_text(driver, account_index, selected_suboption)
        
        # Special case for "Regulated goods and activities" - random between 4 sub-options  
        elif secondary_text in ["Gambling", "Alcohol, tobacco, and drugs", "Firearms and dangerous weapons", "Trade of other regulated goods and services"]:
            regulated_suboptions = [
                "Gambling",
                "Alcohol, tobacco, and drugs", 
                "Firearms and dangerous weapons",
                "Trade of other regulated goods and services"
            ]
            selected_suboption = random.choice(regulated_suboptions)
            self.log_message(f"🎯 Tài khoản {account_index + 1}: Chọn Regulated sub-option: {selected_suboption}")
            return self.click_suboption_by_text(driver, account_index, selected_suboption)
        
        # Normal secondary option handling
        else:
            return self.click_suboption_by_text(driver, account_index, secondary_text)
    
    def click_suboption_by_text(self, driver, account_index, option_text):
        """Click sub-option dựa trên text"""
        try:
            # Method 1: CSS selector approach
            reason_elements = driver.find_elements(By.CSS_SELECTOR, '[data-e2e="report-card-reason"]')
            
            for element in reason_elements:
                try:
                    reason_text_element = element.find_element(By.CSS_SELECTOR, '.css-1hnazpm-5e6d46e3--DivReasonText')
                    reason_text = reason_text_element.text.strip()
                    
                    if reason_text == option_text:
                        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
                        time.sleep(1)
                        driver.execute_script("arguments[0].click();", element)
                        self.log_message(f"✅ Tài khoản {account_index + 1}: Đã chọn sub-option: {option_text}")
                        time.sleep(2)
                        return True
                except:
                    continue
            
            # Method 2: XPath approach
            option_xpath = f"//div[contains(text(), '{option_text}')]"
            option_elements = driver.find_elements(By.XPATH, option_xpath)
            
            for element in option_elements:
                try:
                    clickable_parent = element.find_element(By.XPATH, "./ancestor::label[@data-e2e='report-card-reason']")
                    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", clickable_parent)
                    time.sleep(1)
                    driver.execute_script("arguments[0].click();", clickable_parent)
                    self.log_message(f"✅ Tài khoản {account_index + 1}: Đã chọn sub-option (XPath): {option_text}")
                    time.sleep(2)
                    return True
                except:
                    continue
            
            # Method 3: Fallback - try any available option
            remaining_elements = driver.find_elements(By.CSS_SELECTOR, '[data-e2e="report-card-reason"]')
            if remaining_elements:
                # Random selection from available options
                fallback_element = random.choice(remaining_elements)
                try:
                    reason_text_element = fallback_element.find_element(By.CSS_SELECTOR, '.css-1hnazpm-5e6d46e3--DivReasonText')
                    fallback_text = reason_text_element.text.strip()
                    
                    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", fallback_element)
                    time.sleep(1)
                    driver.execute_script("arguments[0].click();", fallback_element)
                    self.log_message(f"✅ Tài khoản {account_index + 1}: Đã chọn sub-option (fallback): {fallback_text}")
                    time.sleep(2)
                    return True
                except:
                    pass
            
            return False
            
        except Exception as e:
            self.log_message(f"❌ Tài khoản {account_index + 1}: Lỗi khi chọn sub-option: {str(e)}")
            return False
    
    def scroll_down_and_check_url(self, driver, account_index=0):
        """Cuộn xuống và kiểm tra URL có thay đổi không"""
        try:
            current_url = driver.current_url
            victim_url = self.url_var.get().strip()
            
            # Cuộn xuống bằng phím mũi tên
            body = driver.find_element(By.TAG_NAME, "body")
            body.send_keys(Keys.ARROW_DOWN)
            
            time.sleep(2)  # Đợi một chút để trang phản ứng
            
            new_url = driver.current_url
            
            # Kiểm tra URL có thay đổi không
            if current_url != new_url:
                # Kiểm tra xem URL mới có bắt đầu với victim URL không
                if victim_url and not new_url.startswith(victim_url.rstrip('/')):
                    self.log_message(f"⚠️ Tài khoản {account_index + 1}: URL mới không khớp với victim URL")
                    self.log_message(f"   Expected: {victim_url}")
                    self.log_message(f"   Got: {new_url}")
                    self.log_message(f"🔄 Tài khoản {account_index + 1}: Quay lại victim URL và thực hiện lại...")
                    return "invalid_url"  # URL không hợp lệ
                
                self.log_message(f"🔄 Tài khoản {account_index + 1}: URL đã thay đổi từ {current_url} → {new_url}")
                return True  # URL đã thay đổi và hợp lệ
            else:
                self.log_message(f"⬇️ Tài khoản {account_index + 1}: Đã cuộn xuống, URL không đổi")
                return False  # URL không thay đổi
                
        except Exception as e:
            self.log_message(f"❌ Tài khoản {account_index + 1}: Lỗi khi cuộn xuống: {str(e)}")
            return False
    
    def check_and_change_language_to_english(self, driver, account_index=0):
        """Kiểm tra ngôn ngữ và chuyển sang tiếng Anh nếu cần"""
        try:
            # Kiểm tra xem có button "Thêm" (tiếng Việt) không
            more_buttons = driver.find_elements(By.XPATH, "//button[@aria-label='Thêm']")
            
            if more_buttons:
                self.log_message(f"🌐 Tài khoản {account_index + 1}: Phát hiện giao diện tiếng Việt, đang chuyển sang tiếng Anh...")
                
                # Click vào button "Thêm"
                more_button = more_buttons[0]
                driver.execute_script("arguments[0].click();", more_button)
                time.sleep(2)
                
                # Click vào button language select
                language_buttons = driver.find_elements(By.XPATH, "//button[@data-e2e='language-select']")
                if language_buttons:
                    driver.execute_script("arguments[0].click();", language_buttons[0])
                    time.sleep(2)
                    
                    # Click vào English (US)
                    english_buttons = driver.find_elements(By.XPATH, "//button[@aria-label='English (US)']")
                    if english_buttons:
                        driver.execute_script("arguments[0].click();", english_buttons[0])
                        time.sleep(3)
                        self.log_message(f"✅ Tài khoản {account_index + 1}: Đã chuyển sang tiếng Anh")
                        return True
                    else:
                        self.log_message(f"❌ Tài khoản {account_index + 1}: Không tìm thấy button English (US)")
                else:
                    self.log_message(f"❌ Tài khoản {account_index + 1}: Không tìm thấy language select button")
            else:
                self.log_message(f"✅ Tài khoản {account_index + 1}: Giao diện đã là tiếng Anh")
                return True
                
        except Exception as e:
            self.log_message(f"❌ Tài khoản {account_index + 1}: Lỗi khi thay đổi ngôn ngữ: {str(e)}")
            
        return False
    
    def navigate_to_victim_and_click_video(self, driver, account_index=0):
        """Điều hướng đến link victim, click video và thực hiện báo cáo liên tục"""
        loop_count = 0
        
        # Flag để xác định có cần load victim URL hay không
        should_load_victim_url = True
        
        while self.is_running:  # Lặp cho đến khi người dùng dừng
            try:
                loop_count += 1
                self.log_message(f"🔄 Tài khoản {account_index + 1}: Lần lặp #{loop_count}")
                
                # Chỉ load victim URL khi cần thiết
                if should_load_victim_url:
                    # Lấy URL victim
                    victim_url = self.url_var.get().strip()
                    if not victim_url:
                        victim_url = "https://www.tiktok.com"
                    
                    self.log_message(f"🎯 Tài khoản {account_index + 1}: Đang điều hướng đến {victim_url}")
                    
                    # Điều hướng đến victim URL
                    driver.get(victim_url)
                    time.sleep(5)  # Đợi trang load
                    
                    self.log_message(f"⏳ Tài khoản {account_index + 1}: Đợi trang load xong...")
                    
                    # Đợi trang load hoàn toàn
                    WebDriverWait(driver, 15).until(
                        lambda d: d.execute_script("return document.readyState") == "complete"
                    )
                    
                    time.sleep(3)  # Thêm delay để đảm bảo content động load xong
                    
                    # Kiểm tra và chuyển ngôn ngữ sang tiếng Anh nếu cần
                    language_changed = self.check_and_change_language_to_english(driver, account_index)
                    
                    if language_changed:
                        # Nếu đã thay đổi ngôn ngữ, load lại victim URL
                        self.log_message(f"🔄 Tài khoản {account_index + 1}: Đã đổi ngôn ngữ, load lại victim URL...")
                        driver.get(victim_url)
                        time.sleep(5)
                        
                        # Đợi trang load hoàn toàn
                        WebDriverWait(driver, 15).until(
                            lambda d: d.execute_script("return document.readyState") == "complete"
                        )
                        time.sleep(3)
                    
                    should_load_victim_url = False  # Đã load rồi, không cần load lại
                else:
                    # Nếu không cần load victim URL, có nghĩa là đang ở URL mới sau khi cuộn
                    current_url = driver.current_url
                    self.log_message(f"🎯 Tài khoản {account_index + 1}: Tiếp tục ở URL hiện tại: {current_url}")
                    time.sleep(2)  # Đợi trang ổn định
                
                # Kiểm tra xem có đang ở trang video không
                current_url = driver.current_url
                video_clicked = "/video/" in current_url
                
                if not video_clicked:
                    # Tìm và click vào video đầu tiên
                    try:
                        # Thử nhiều selector khác nhau cho video đầu tiên (ưu tiên ID)
                        video_selectors = [
                            '#column-item-video-container-0',  # ID selector đầu tiên
                            '#column-item-video-container-1',  # ID backup
                            '[id^="column-item-video-container"]',  # Bất kỳ ID column-item
                            '[data-e2e="user-post-item"]',  # Selector chính
                            '.css-16cwaxc-5e6d46e3--DivContainer-5e6d46e3--StyledDivContainerV2',  # Class selector
                            'a[href*="/video/"]',  # Link chứa /video/
                            '[role="button"][aria-label*="Xem ở chế độ toàn màn hình"]'  # Aria label
                        ]
                        
                        video_element = None
                        used_selector = None
                        
                        for selector in video_selectors:
                            try:
                                elements = WebDriverWait(driver, 10).until(
                                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector))
                                )
                                if elements:
                                    video_element = elements[0]  # Lấy element đầu tiên
                                    used_selector = selector
                                    self.log_message(f"🎥 Tài khoản {account_index + 1}: Tìm thấy video với selector: {selector}")
                                    break
                            except:
                                continue
                        
                        if video_element:
                            # Scroll đến element để đảm bảo nó visible
                            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", video_element)
                            time.sleep(2)
                            
                            # Nếu đây là container, tìm link bên trong
                            video_link = None
                            if 'column-item-video-container' in used_selector:
                                try:
                                    # Tìm link video bên trong container
                                    video_link = video_element.find_element(By.CSS_SELECTOR, 'a[href*="/video/"]')
                                    self.log_message(f"🔗 Tài khoản {account_index + 1}: Tìm thấy link video bên trong container")
                                except:
                                    # Nếu không tìm thấy link, thử click container
                                    video_link = video_element
                            else:
                                video_link = video_element
                            
                            # Thử nhiều cách click
                            click_success = False
                            
                            # Cách 1: Click vào link nếu có href
                            try:
                                if video_link.get_attribute('href'):
                                    href = video_link.get_attribute('href')
                                    self.log_message(f"🔗 Tài khoản {account_index + 1}: Tìm thấy href: {href}")
                                    driver.get(href)  # Navigate trực tiếp
                                    click_success = True
                                    self.log_message(f"🎬 Tài khoản {account_index + 1}: Điều hướng trực tiếp đến video!")
                                else:
                                    raise Exception("Không có href")
                            except:
                                # Cách 2: JavaScript click
                                try:
                                    driver.execute_script("arguments[0].click();", video_link)
                                    click_success = True
                                    self.log_message(f"🎬 Tài khoản {account_index + 1}: Đã click vào video (JavaScript)!")
                                except:
                                    # Cách 3: Normal click
                                    try:
                                        video_link.click()
                                        click_success = True
                                        self.log_message(f"🎬 Tài khoản {account_index + 1}: Đã click vào video (Normal click)!")
                                    except:
                                        pass
                            
                            if click_success:
                                time.sleep(5)  # Đợi lâu hơn để trang load
                                
                                # Kiểm tra xem có chuyển đến trang video không
                                current_url = driver.current_url
                                if "/video/" in current_url:
                                    self.log_message(f"✅ Tài khoản {account_index + 1}: Đã chuyển đến trang video thành công!")
                                    video_clicked = True
                                else:
                                    self.log_message(f"⚠️ Tài khoản {account_index + 1}: Click video nhưng chưa chuyển trang")
                                    self.log_message(f"🔍 Current URL: {current_url}")
                            else:
                                self.log_message(f"❌ Tài khoản {account_index + 1}: Không thể click video!")
                                
                        else:
                            self.log_message(f"❌ Tài khoản {account_index + 1}: Không tìm thấy video nào để click!")
                            
                    except Exception as e:
                        self.log_message(f"❌ Tài khoản {account_index + 1}: Lỗi khi tìm/click video: {str(e)}")
                
                # Nếu đã ở trang video (hoặc đã click thành công), thực hiện báo cáo
                if video_clicked:
                    time.sleep(2)  # Đợi trang video load hoàn toàn
                    
                    # Thực hiện báo cáo
                    report_success = self.perform_reporting_workflow(driver, account_index)
                    
                    if report_success:
                        self.log_message(f"🎉 Tài khoản {account_index + 1}: Hoàn thành báo cáo thành công!")
                    else:
                        self.log_message(f"⚠️ Tài khoản {account_index + 1}: Báo cáo thất bại, tiếp tục...")
                    
                    # Cuộn xuống và kiểm tra URL
                    scrolled_url_changed = False
                    for scroll_attempt in range(5):  # Thử cuộn tối đa 5 lần
                        if not self.is_running:
                            break
                            
                        url_changed = self.scroll_down_and_check_url(driver, account_index)
                        
                        if url_changed == "invalid_url":
                            # URL không hợp lệ -> quay lại victim URL và thực hiện từ đầu
                            self.log_message(f"🔄 Tài khoản {account_index + 1}: URL không hợp lệ, quay lại victim URL...")
                            should_load_victim_url = True
                            scrolled_url_changed = False
                            break
                        elif url_changed:
                            scrolled_url_changed = True
                            break
                        
                        time.sleep(1)  # Đợi giữa các lần cuộn
                    
                    # Logic quyết định tiếp theo
                    if should_load_victim_url:
                        # Trường hợp URL không hợp lệ -> quay lại victim URL
                        continue
                    elif scrolled_url_changed:
                        # URL đã thay đổi và hợp lệ -> tiếp tục ở URL mới, không cần load victim URL
                        self.log_message(f"➡️ Tài khoản {account_index + 1}: URL đã thay đổi và hợp lệ, tiếp tục báo cáo ở URL mới...")
                        should_load_victim_url = False  # Không load victim URL
                    else:
                        # URL không thay đổi -> quay về victim URL và làm lại từ đầu
                        self.log_message(f"🔄 Tài khoản {account_index + 1}: URL không đổi sau khi cuộn, quay lại victim URL...")
                        should_load_victim_url = True  # Cần load victim URL
                else:
                    # Không click được video -> quay về victim URL
                    self.log_message(f"🔄 Tài khoản {account_index + 1}: Không click được video, quay lại victim URL...")
                    should_load_victim_url = True
                
                # Kiểm tra nếu không phải trong vòng lặp chính nữa
                if not self.is_running:
                    break
                    
                time.sleep(2)  # Delay nhỏ trước khi lặp tiếp
                
            except Exception as e:
                self.log_message(f"❌ Tài khoản {account_index + 1}: Lỗi trong vòng lặp chính: {str(e)}")
                
                # Nếu có lỗi, thử quay lại victim URL
                try:
                    victim_url = self.url_var.get().strip()
                    if not victim_url:
                        victim_url = "https://www.tiktok.com"
                    self.log_message(f"🔄 Tài khoản {account_index + 1}: Đang khôi phục bằng cách quay lại {victim_url}")
                    driver.get(victim_url)
                    should_load_victim_url = False  # Đã load rồi
                    time.sleep(3)
                except:
                    self.log_message(f"❌ Tài khoản {account_index + 1}: Không thể khôi phục, tiếp tục...")
                
                time.sleep(5)  # Delay lâu hơn khi có lỗi
        
        self.log_message(f"🏁 Tài khoản {account_index + 1}: Kết thúc vòng lặp (đã chạy {loop_count} lần)")
        return True
    
    def login_single_account(self, account_index):
        """Đăng nhập cho một tài khoản duy nhất"""
        try:
            self.log_message(f"=== BẮT ĐẦU ĐĂNG NHẬP TÀI KHOẢN {account_index + 1} ===")
            
            # Lấy cookie từ text area tương ứng
            if account_index >= len(self.cookie_fields):
                self.log_message(f"❌ Không tìm thấy trường cookie cho tài khoản {account_index + 1}")
                return None
                
            cookie_string = self.cookie_fields[account_index].get("1.0", tk.END).strip()
            cookies = self.parse_cookies(cookie_string)
            
            if not cookies:
                self.log_message(f"❌ Tài khoản {account_index + 1}: Vui lòng nhập cookie hợp lệ!")
                return None
            
            self.log_message(f"Tài khoản {account_index + 1}: Đã parse {len(cookies)} cookies từ input.")
            
            # Thiết lập driver
            driver = self.setup_driver(account_index)
            if not driver:
                return None
            
            # Apply cookies
            if not self.apply_cookies(driver, cookies, account_index):
                driver.quit()
                return None
            
            # Kiểm tra trạng thái đăng nhập
            login_status = self.check_login_status(driver, account_index)
            
            if login_status:
                self.log_message(f"🎉 TÀI KHOẢN {account_index + 1}: ĐĂNG NHẬP THÀNH CÔNG!")
                
                # Điều hướng đến victim URL và click video đầu tiên
                self.log_message(f"🚀 TÀI KHOẢN {account_index + 1}: Bắt đầu điều hướng đến victim...")
                video_success = self.navigate_to_victim_and_click_video(driver, account_index)
                
                if video_success:
                    self.log_message(f"✅ TÀI KHOẢN {account_index + 1}: Hoàn thành tất cả các bước!")
                else:
                    self.log_message(f"⚠️ TÀI KHOẢN {account_index + 1}: Đăng nhập OK nhưng click video thất bại!")
                    
            elif login_status is False:
                self.log_message(f"❌ TÀI KHOẢN {account_index + 1}: ĐĂNG NHẬP THẤT BẠI! Vui lòng kiểm tra lại cookie.")
            else:
                self.log_message(f"⚠️ TÀI KHOẢN {account_index + 1}: Không thể xác định trạng thái. Vui lòng kiểm tra thủ công.")
            
            return driver
            
        except Exception as e:
            self.log_message(f"❌ Lỗi trong quá trình đăng nhập tài khoản {account_index + 1}: {str(e)}")
            return None
    
    def login_process(self):
        """Quy trình đăng nhập chính cho tất cả tài khoản"""
        try:
            self.log_message("=== BẮT ĐẦU QUY TRÌNH ĐĂNG NHẬP MULTI-ACCOUNT ===")
            
            # Lấy số lượng tài khoản
            account_count = len(self.cookie_fields)
            if account_count == 0:
                self.log_message("❌ Không có trường cookie nào!")
                return
            
            self.log_message(f"Sẽ đăng nhập {account_count} tài khoản...")
            
            # Clear danh sách drivers cũ
            self.drivers.clear()
            
            # Đăng nhập từng tài khoản
            for i in range(account_count):
                if not self.is_running:  # Kiểm tra nếu user đã dừng
                    self.log_message("Quá trình đã được dừng bởi người dùng.")
                    break
                    
                driver = self.login_single_account(i)
                if driver:
                    self.drivers.append({
                        'driver': driver,
                        'account_index': i,
                        'status': 'running'
                    })
                else:
                    self.drivers.append({
                        'driver': None,
                        'account_index': i,
                        'status': 'failed'
                    })
                
                # Thêm delay giữa các lần đăng nhập
                if i < account_count - 1:
                    self.log_message(f"Chờ 3 giây trước khi đăng nhập tài khoản tiếp theo...")
                    time.sleep(3)
            
            # Tổng kết
            successful_logins = len([d for d in self.drivers if d['driver'] is not None])
            failed_logins = len([d for d in self.drivers if d['driver'] is None])
            
            self.log_message("=== TỔNG KẾT QUY TRÌNH ĐĂNG NHẬP ===")
            self.log_message(f"✅ Thành công: {successful_logins} tài khoản")
            self.log_message(f"❌ Thất bại: {failed_logins} tài khoản")
            self.log_message(f"📊 Tổng cộng: {account_count} tài khoản")
            
            if successful_logins > 0:
                self.log_message("🎉 Các trình duyệt đã đăng nhập và điều hướng đến victim!")
                self.log_message("🎬 Video đầu tiên đã được click tự động!")
                self.log_message("💡 Có thể sử dụng 'Dừng lại' để đóng tất cả browser khi cần.")
            
        except Exception as e:
            self.log_message(f"❌ Lỗi trong quá trình đăng nhập: {str(e)}")
        finally:
            # Reset button states
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.NORMAL if self.drivers else tk.DISABLED)
            self.is_running = False
    
    def start_login(self):
        """Bắt đầu quá trình đăng nhập"""
        if self.is_running:
            self.log_message("Quá trình đăng nhập đang chạy...")
            return
        
        self.is_running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        # Chạy trong thread riêng để không block UI
        thread = Thread(target=self.login_process, daemon=True)
        thread.start()
    
    def stop_login(self):
        """Dừng quá trình và đóng tất cả browser"""
        try:
            self.log_message("Đang dừng tất cả browser...")
            
            if self.drivers:
                for driver_info in self.drivers:
                    driver = driver_info.get('driver')
                    account_index = driver_info.get('account_index', 0)
                    
                    if driver:
                        try:
                            driver.quit()
                            self.log_message(f"✅ Browser tài khoản {account_index + 1} đã được đóng.")
                        except Exception as e:
                            self.log_message(f"⚠️ Lỗi khi đóng browser tài khoản {account_index + 1}: {str(e)}")
                
                self.drivers.clear()
                self.log_message("✅ Tất cả browser đã được đóng.")
            else:
                self.log_message("Không có browser nào đang chạy.")
            
            self.is_running = False
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            
        except Exception as e:
            self.log_message(f"Lỗi khi đóng browser: {str(e)}")
    
    def on_closing(self):
        """Xử lý khi đóng ứng dụng"""
        try:
            if self.drivers:
                for driver_info in self.drivers:
                    driver = driver_info.get('driver')
                    if driver:
                        try:
                            driver.quit()
                        except:
                            pass
        except:
            pass
        
        self.root.destroy()

def main():
    root = tk.Tk()
    app = TikTokLoginApp(root)
    
    # Xử lý khi đóng window
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    root.mainloop()

if __name__ == "__main__":
    main()