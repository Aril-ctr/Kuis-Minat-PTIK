import json
import tkinter as tk
from tkinter import messagebox
import random
from PIL import Image, ImageTk

# Import Pygame untuk fitur Audio
try:
    import pygame.mixer
    AUDIO_SUPPORT = True
except ImportError:
    AUDIO_SUPPORT = False
    print("Peringatan: Pustaka 'pygame' tidak ditemukan. Fitur audio dimatikan.")

# ==================================
# CLASS UTAMA: FINAL APP (REVISI WARNA MULTIMEDIA)
# ==================================
class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Kuis PTIK - HMJ")
        self.root.attributes("-fullscreen", True)

        # === CONFIG: DEFAULT PALETTE (BASE) ===
        self.DEFAULT_PALETTE = {
            "bg_main": "#050505",
            "bg_card": "#111111",
            "circuit_line": "#1F1F1F",
            "circuit_node": "#FF6600",
            "primary": "#FF6600",
            "secondary": "#FF6600",
            "success": "#00E676",
            "danger": "#D50000",
            "text_light": "#FFFFFF",
            "text_dark": "#000000",
            "text_dim": "#AAAAAA",
            "overlay": "black"
        }

        # Mulai dengan Default
        self.PALETTE = self.DEFAULT_PALETTE.copy()

        # === CONFIG: TEMA PER KONSENTRASI ===
        self.THEME_CONFIG = {
            # --- [REVISI TEMA MULTIMEDIA] ---
            # Background dan elemen Ungu diganti Orange/Cokelat.
            "Multimedia": {
                "bg_main": "#4A2500",       # Background: Cokelat/Orange Gelap (Ganti Ungu Gelap)
                "bg_card": "#804000",       # Card Soal: Cokelat Bata
                "primary": "#FF6600",       # Header Line & Score: Orange Cerah (Ganti Pink Neon)
                "secondary": "#FF9933",     # Aksen: Orange Muda
                "circuit_line": "#A0522D",  # Garis hiasan: Sienna
                "circuit_node": "#FFD700"   # Titik: Emas
            },
            "RPL": {
                "bg_main": "#001100",
                "bg_card": "#002200",
                "primary": "#00FF00",
                "secondary": "#008F11",
                "circuit_line": "#003300",
                "circuit_node": "#32CD32"
            },
            "TKJ": {
                "bg_main": "#000510",
                "bg_card": "#001133",
                "primary": "#00CCFF",
                "secondary": "#0055AA",
                "circuit_line": "#002244",
                "circuit_node": "#00CCFF"
            }
        }

        # --- [REVISI WARNA TOMBOL] ---
        # Warna Ungu (#B0006F) diganti Orange (#FF4500).
        # Sisanya (Olive, Biru, Cokelat Muda) TETAP ADA.
        self.MULTI_COLORS = ["#FF4500", "#FF4500", "#FF4500", "#FF4500"]

        self.root.configure(bg=self.PALETTE["bg_main"])

        # --- Audio & Variables ---
        self.sfx_correct = None
        self.sfx_incorrect = None
        self.sfx_bonus = None

        # Setup Lagu
        self.BGM_DEFAULT = "Extreme-Sport-Trap-Music-PISTA(chosic.com).mp3"
        self.BGM_RPL = "RPL.mp3"
        self.BGM_TKJ = "TKJ.mp3"
        self.BGM_MULTI = "MULTIMEDIA.mp3"
        self.current_bgm = None

        if AUDIO_SUPPORT: self._init_audio()

        self.timer_job = None
        self.loading_job = None
        self.exit_modal = None
        self.exit_btn_widget = None
        self.back_btn_widget = None 

        self.current_index = 1
        self.score = 0
        self.consecutive_correct = 0
        self.questions = {}
        self.question_order = []
        self.selected_answer = tk.StringVar()
        self.option_widgets = []
        self.current_concentration = "HMJ"
        self.answer_submitted = False

        # Widget Refs
        self.quiz_canvas = None
        self.content_frame = None
        self.window_id = None
        self.logo_image = None
        self.header_logo_image = None
        self.exit_door_icon = None

        self.main_frame = tk.Frame(root, bg=self.PALETTE["bg_main"])
        self.main_frame.pack(fill="both", expand=True)

        self.root.bind("<Escape>", self._handle_escape)
        self._load_shared_images()

        self.startup_loading_screen()

    # ==================================
    # HELPER: BACKGROUND & CARD
    # ==================================
    def _create_tech_card(self, parent, title_text, border_color=None):
        if border_color is None: border_color = self.PALETTE["primary"]
        outer_frame = tk.Frame(parent, bg=border_color, padx=2, pady=2)
        inner_frame = tk.Frame(outer_frame, bg=self.PALETTE["bg_card"],
                               highlightthickness=3, highlightbackground=border_color)
        inner_frame.pack(fill="both", expand=True)
        header_strip = tk.Frame(inner_frame, bg=border_color, height=35)
        header_strip.pack(fill="x", side="top")
        header_strip.pack_propagate(False)
        tk.Label(header_strip, text=f"// {title_text}",
                 font=("Consolas", 14, "bold"), fg="black", bg=border_color).pack(side="left", padx=10)
        body_frame = tk.Frame(inner_frame, bg=self.PALETTE["bg_card"], padx=25, pady=25)
        body_frame.pack(fill="both", expand=True)
        return outer_frame, body_frame

    def _draw_tech_background(self, canvas, width, height):
        canvas.delete("tech_bg")
        
        # 1. TEMA MULTIMEDIA: Bubbles
        # Warna bubble disesuaikan dengan background baru (Kuning/Orange/Merah)
        if self.current_concentration == "Multimedia":
            bubble_colors = ["#FF4500", "#FFA500", "#FFD700", "#FF6347", "#8B4500"]
            for _ in range(60):
                x = random.randint(0, width)
                y = random.randint(0, height)
                r = random.randint(10, 50)
                color = random.choice(bubble_colors)
                canvas.create_oval(x-r, y-r, x+r, y+r, outline=color, width=2, tags="tech_bg")
                if random.random() < 0.2:
                    canvas.create_oval(x-r/2, y-r/2, x+r/2, y+r/2, fill=color, outline="", tags="tech_bg")

        # 2. TEMA RPL: Matrix Digits
        elif self.current_concentration == "RPL":
            for _ in range(150):
                x = random.randint(0, width)
                y = random.randint(0, height)
                char = random.choice(["0", "1", "<>", "{}"])
                canvas.create_text(x, y, text=char, fill="#003300", font=("Courier", 14, "bold"), tags="tech_bg")

        # 3. TEMA TKJ: Network Grid
        elif self.current_concentration == "TKJ":
            step = 60
            for x in range(0, width, step):
                canvas.create_line(x, 0, x, height, fill="#001133", width=1, tags="tech_bg")
            for y in range(0, height, step):
                canvas.create_line(0, y, width, y, fill="#001133", width=1, tags="tech_bg")
            for _ in range(40):
                x1 = random.randint(0, width)
                y1 = random.randint(0, height)
                x2 = x1 + random.randint(-100, 100)
                y2 = y1 + random.randint(-100, 100)
                canvas.create_line(x1, y1, x2, y2, fill=self.PALETTE["primary"], width=1, tags="tech_bg")
                canvas.create_oval(x1-2, y1-2, x1+2, y1+2, fill="white", tags="tech_bg")

        # 4. DEFAULT
        else:
            step = 60
            for x in range(0, width, step):
                canvas.create_line(x, 0, x, height, fill="#0E0E0E", width=1, tags="tech_bg")
            for y in range(0, height, step):
                canvas.create_line(0, y, width, y, fill="#0E0E0E", width=1, tags="tech_bg")
            for _ in range(40):
                x1 = random.randint(0, width // step) * step
                y1 = random.randint(0, height // step) * step
                if random.choice([True, False]):
                    x2, y2 = x1 + random.randint(2, 5) * step, y1
                    x3, y3 = x2, y2 + random.randint(-1, 1) * step
                else:
                    x2, y2 = x1, y1 + random.randint(2, 5) * step
                    x3, y3 = x2 + random.randint(-1, 1) * step, y2
                canvas.create_line(x1, y1, x2, y2, x3, y3, fill=self.PALETTE["circuit_line"], width=2, tags="tech_bg")
                if random.random() < 0.25:
                    r = 3
                    fill = self.PALETTE["circuit_node"] if random.random() < 0.5 else "#333"
                    canvas.create_oval(x3-r, y3-r, x3+r, y3+r, fill=fill, outline="", tags="tech_bg")
        canvas.tag_lower("tech_bg")

    # ==================================
    # SYSTEM AUDIO & ASSETS
    # ==================================
    def _init_audio(self):
        try:
            pygame.mixer.init()
            self._switch_music(self.BGM_DEFAULT)
            self.sfx_correct = pygame.mixer.Sound("Benar.wav")
            self.sfx_incorrect = pygame.mixer.Sound("Salah.wav")
            self.sfx_bonus = pygame.mixer.Sound("Bonus.mp3")
            self.sfx_correct.set_volume(0.6)
            self.sfx_incorrect.set_volume(0.6)
        except: global AUDIO_SUPPORT; AUDIO_SUPPORT = False

    def _switch_music(self, music_file):
        if not AUDIO_SUPPORT: return
        if self.current_bgm == music_file: return
        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.load(music_file)
            pygame.mixer.music.play(-1)
            pygame.mixer.music.set_volume(0.2)
            self.current_bgm = music_file
        except Exception as e:
            print(f"Gagal memuat lagu {music_file}: {e}")

    def _stop_audio(self):
        if AUDIO_SUPPORT: pygame.mixer.music.stop()

    def _play_sfx_for_result(self, is_correct, consecutive_correct):
        if not AUDIO_SUPPORT: return
        if is_correct:
            if consecutive_correct > 1 and self.sfx_bonus: self.sfx_bonus.play()
            elif self.sfx_correct: self.sfx_correct.play()
        else:
            if self.sfx_incorrect: self.sfx_incorrect.play()

    def _load_shared_images(self):
        try:
            img = Image.open("logo.png")
            self.logo_image = ImageTk.PhotoImage(img.resize((200, 200)))
            self.header_logo_image = ImageTk.PhotoImage(img.resize((50, 50)))
            exit_img = Image.open("exit_door_icon.png").resize((30, 30))
            self.exit_door_icon = ImageTk.PhotoImage(exit_img)
        except: self.logo_image = None; self.exit_door_icon = None

    def _handle_escape(self, event=None):
        if self.exit_modal: self.close_custom_exit_modal()
        else: self.root.attributes("-fullscreen", False)

    def exit_app(self): self._show_custom_exit_modal()
    def confirm_exit(self): self._stop_audio(); self.root.destroy()
    def close_custom_exit_modal(self):
        if self.exit_modal: self.exit_modal.destroy(); self.exit_modal = None

    def clear_frame(self):
        for widget in self.main_frame.winfo_children(): widget.destroy()
        self.quiz_canvas = None
        self.content_frame = None
        self.exit_btn_widget = None
        self.back_btn_widget = None
        if self.timer_job: self.root.after_cancel(self.timer_job)
        if self.loading_job: self.root.after_cancel(self.loading_job)
        self.answer_submitted = False
        self.close_custom_exit_modal()

    # ==================================
    # HELPER: NAVIGASI BAWAH
    # ==================================
    def _place_bottom_nav(self, back_command=None):
        if self.exit_btn_widget: self.exit_btn_widget.destroy()
        self.exit_btn_widget = tk.Button(self.main_frame, text="X KELUAR", command=self.exit_app,
                        bg=self.PALETTE["danger"], fg="white", font=("Impact", 12),
                        relief="raised", bd=5, padx=15, pady=8, cursor="hand2")
        self.exit_btn_widget.place(relx=1.0, rely=1.0, anchor="se", x=-20, y=-20)
        self.exit_btn_widget.lift()

        if self.back_btn_widget: self.back_btn_widget.destroy()
        if back_command:
            self.back_btn_widget = tk.Button(self.main_frame, text="< KEMBALI", command=back_command,
                            bg=self.PALETTE["secondary"], fg="white", font=("Impact", 12),
                            relief="raised", bd=5, padx=15, pady=8, cursor="hand2")
            self.back_btn_widget.place(relx=0.0, rely=1.0, anchor="sw", x=20, y=-20)
            self.back_btn_widget.lift()

    # ==================================
    # 1. LOADING SCREEN
    # ==================================
    def startup_loading_screen(self):
        self.PALETTE = self.DEFAULT_PALETTE.copy()
        self.current_concentration = "HMJ"
        self.main_frame.configure(bg=self.PALETTE["bg_main"])
        self.clear_frame()
        canvas = tk.Canvas(self.main_frame, bg=self.PALETTE["bg_main"], highlightthickness=0)
        canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.root.update()
        self._draw_tech_background(canvas, self.root.winfo_width(), self.root.winfo_height())
        cx, cy = self.root.winfo_width() // 2, self.root.winfo_height() // 2
        if self.logo_image: canvas.create_image(cx, cy - 120, image=self.logo_image)
        canvas.create_text(cx, cy + 30, text="KUIS MINAT PTIK", font=("Impact", 42), fill=self.PALETTE["primary"])
        canvas.create_text(cx, cy + 90, text="SYSTEM INITIALIZING...", font=("Consolas", 18), fill=self.PALETTE["text_dim"])
        self.loading_label_id = canvas.create_text(cx, cy + 130, text="[..........]", font=("Consolas", 20, "bold"), fill=self.PALETTE["success"])
        self.animate_loading_bar(canvas, 0, self.introduction_screen)

    def transition_loading(self, callback_func):
        self.clear_frame()
        canvas = tk.Canvas(self.main_frame, bg=self.PALETTE["bg_main"], highlightthickness=0)
        canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.root.update()
        self._draw_tech_background(canvas, self.root.winfo_width(), self.root.winfo_height())
        cx, cy = self.root.winfo_width() // 2, self.root.winfo_height() // 2
        canvas.create_text(cx, cy - 30, text="PROCESSING DATA...", font=("Impact", 36), fill=self.PALETTE["primary"])
        canvas.create_text(cx, cy + 40, text="Please wait, calibrating module...", font=("Consolas", 16), fill=self.PALETTE["text_dim"])
        self.loading_label_id = canvas.create_text(cx, cy + 100, text="[..........]", font=("Consolas", 20, "bold"), fill=self.PALETTE["success"])
        self.animate_loading_bar(canvas, 0, callback_func, speed=150)

    def animate_loading_bar(self, canvas, step, callback, speed=250):
        bars = ["█", "██", "███", "████", "█████", "██████", "███████"]
        if not self.main_frame.winfo_exists(): return
        max_steps = len(bars) * 3
        if step < max_steps:
            text = f"[{bars[step % len(bars)].ljust(10)}]"
            canvas.itemconfigure(self.loading_label_id, text=text)
            self.loading_job = self.root.after(speed, lambda: self.animate_loading_bar(canvas, step + 1, callback, speed))
        else:
            callback()

    # ==================================
    # 2. INTRO & MENU
    # ==================================
    def introduction_screen(self):
        self.clear_frame()
        canvas = tk.Canvas(self.main_frame, bg=self.PALETTE["bg_main"], highlightthickness=0)
        canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.root.update()
        self._draw_tech_background(canvas, self.root.winfo_width(), self.root.winfo_height())
        intro_container = tk.Frame(self.main_frame, bg=self.PALETTE["bg_main"])
        intro_container.place(relx=0.5, rely=0.5, anchor="center")
        card_outer, card_body = self._create_tech_card(intro_container, "INFO_SYSTEM", border_color=self.PALETTE["primary"])
        card_outer.pack()
        tk.Label(card_body, text="PENGANTAR KONSENTRASI", font=("Impact", 32),
                 bg=self.PALETTE["bg_card"], fg=self.PALETTE["text_light"]).pack(pady=(0, 20))
        intro_text = (
            "Kuis ini adalah langkah awal yang menyenangkan untuk mengenal 3 Konsentrasi "
            "utama yang ada di jurusan kita. Di Semester 2 nanti, Anda akan memilih "
            "salah satu dari tiga konsentrasi ini:\n\n"
            "• MULTIMEDIA (Desain & Produksi Konten)\n"
            "• RPL (Rekayasa Perangkat Lunak - Coding)\n"
            "• TKJ (Teknik Komputer & Jaringan - Infrastruktur)\n"
        )
        tk.Label(card_body, text=intro_text, font=("Arial", 14), bg=self.PALETTE["bg_card"], fg=self.PALETTE["text_dim"], wraplength=900, justify="left").pack(pady=20)
        btn = tk.Button(card_body, text="MULAI PILIH KONSENTRASI >",
                        command=lambda: self.transition_loading(self.menu_screen),
                        font=("Consolas", 18, "bold"), bg=self.PALETTE["primary"], fg="black",
                        activebackground=self.PALETTE["primary"], activeforeground="white",
                        relief="raised", bd=5, padx=40, pady=15, cursor="hand2")
        btn.pack(pady=20)
        self._place_bottom_nav()

    def menu_screen(self):
        self._switch_music(self.BGM_DEFAULT)
        self.PALETTE = self.DEFAULT_PALETTE.copy()
        self.current_concentration = "HMJ"
        self.main_frame.configure(bg=self.PALETTE["bg_main"])
        self.clear_frame()
        canvas = tk.Canvas(self.main_frame, bg=self.PALETTE["bg_main"], highlightthickness=0)
        canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.root.update()
        self._draw_tech_background(canvas, self.root.winfo_width(), self.root.winfo_height())

        menu_container = tk.Frame(self.main_frame, bg=self.PALETTE["bg_main"])
        menu_container.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(menu_container, text="PILIH BIDANG MINAT", font=("Impact", 40),
                 bg=self.PALETTE["bg_main"], fg=self.PALETTE["primary"]).pack(pady=(0, 30))

        buttons_data = [
            ("🎬 MULTIMEDIA", "multimedia.json", "Multimedia"),
            ("💻 RPL (Coding)", "rpl.json", "RPL"),
            ("🌐 TKJ (Network)", "tkj.json", "TKJ")
        ]

        for text, file, name in buttons_data:
            cmd = lambda f=file, n=name: self.transition_loading(lambda: self.load_questions(f, n))
            btn = tk.Button(menu_container, text=text, command=cmd,
                            font=("Consolas", 20, "bold"),
                            bg="black", fg="white",
                            activebackground=self.PALETTE["primary"], activeforeground="black",
                            relief="raised", bd=5, padx=40, pady=15, cursor="hand2", width=40)
            btn.pack(pady=12)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=self.PALETTE["primary"], fg="black"))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg="black", fg="white"))

        self._place_bottom_nav(back_command=self.introduction_screen)

    def load_questions(self, file_name, concentration_name):
        try:
            if concentration_name in self.THEME_CONFIG:
                custom_theme = self.THEME_CONFIG[concentration_name]
                for k, v in custom_theme.items():
                    self.PALETTE[k] = v

                if concentration_name == "Multimedia":
                    self._switch_music(self.BGM_MULTI)
                elif concentration_name == "RPL":
                    self._switch_music(self.BGM_RPL)
                elif concentration_name == "TKJ":
                    self._switch_music(self.BGM_TKJ)

            self.main_frame.configure(bg=self.PALETTE["bg_main"])

            with open(file_name, "r", encoding="utf-8") as f: self.questions = json.load(f)
            if not self.questions: raise ValueError("File JSON kosong")

            all_questions_keys = list(self.questions.keys())
            random.shuffle(all_questions_keys)
            self.question_order = all_questions_keys[:10]

            self.current_index = 1
            self.score = 0
            self.consecutive_correct = 0
            self.current_concentration = concentration_name
            self.show_quiz()
        except Exception as e:
            tk.messagebox.showerror("Error", f"Gagal memuat: {e}")
            self.menu_screen()

    # ==================================
    # 3. QUIZ SCREEN (LAYOUT SPLIT)
    # ==================================
    def show_quiz(self):
        self.clear_frame()
        self.option_widgets = []

        if self.current_index > len(self.question_order):
            self.transition_loading(self.show_result)
            return

        q_key = self.question_order[self.current_index - 1]
        q = self.questions[q_key]
        soal_text = q["soal"]
        pilihan = q["pilihan"]
        random.shuffle(pilihan)

        # --- HEADER ---
        header_frame = tk.Frame(self.main_frame, bg=self.PALETTE["bg_card"], pady=10)
        header_frame.pack(fill="x", side="top")
        
        # Garis bawah header (Otomatis ikut warna primary/Orange)
        tk.Frame(header_frame, bg=self.PALETTE["primary"], height=3).pack(side="bottom", fill="x")

        # Info Kiri
        left_header = tk.Frame(header_frame, bg=self.PALETTE["bg_card"])
        left_header.pack(side="left", padx=20)
        if self.header_logo_image:
            tk.Label(left_header, image=self.header_logo_image, bg=self.PALETTE["bg_card"]).pack(side="left", padx=10)
        tk.Label(left_header, text=f"{self.current_concentration} MODULE", font=("Impact", 20), fg=self.PALETTE["text_light"], bg=self.PALETTE["bg_card"]).pack(side="left")

        # Info Kanan
        right_header = tk.Frame(header_frame, bg=self.PALETTE["bg_card"])
        right_header.pack(side="right", padx=20)

        # Skor warna Orange (ikut primary)
        self.score_label = tk.Label(right_header, text=f"SCORE: {self.score}", font=("Consolas", 18, "bold"), fg=self.PALETTE["primary"], bg=self.PALETTE["bg_card"])
        self.score_label.pack(side="left", padx=15)

        streak_color = "#FF4500" if self.consecutive_correct > 1 else "white"
        self.streak_label = tk.Label(right_header, text=f"🔥 STREAK: {self.consecutive_correct}", font=("Consolas", 18, "bold"), fg=streak_color, bg=self.PALETTE["bg_card"])
        self.streak_label.pack(side="left", padx=15)

        self.timer_label = tk.Label(right_header, text="TIME: 60s", font=("Consolas", 18, "bold"), fg=self.PALETTE["text_light"], bg=self.PALETTE["bg_card"])
        self.timer_label.pack(side="left")

        # --- CANVAS ---
        self.quiz_canvas = tk.Canvas(self.main_frame, bg=self.PALETTE["bg_main"], highlightthickness=0)
        self.quiz_canvas.pack(side="left", fill="both", expand=True)
        self.content_frame = tk.Frame(self.quiz_canvas, bg=self.PALETTE["bg_main"])
        self.window_id = self.quiz_canvas.create_window((0, 0), window=self.content_frame, anchor="nw", width=1)
        self.content_frame.bind("<Configure>", lambda e: self.quiz_canvas.configure(scrollregion=self.quiz_canvas.bbox("all")))
        self.quiz_canvas.bind('<Configure>', self._on_canvas_configure_quiz)

        # --- LAYOUT SPLIT ---
        split_container = tk.Frame(self.content_frame, bg=self.PALETTE["bg_main"])
        split_container.pack(fill="both", expand=True, padx=40, pady=40)

        # KIRI (SOAL)
        left_area = tk.Frame(split_container, bg=self.PALETTE["bg_main"])
        left_area.pack(side="left", fill="both", expand=True, padx=(0, 20))

        card_outer, card_body = self._create_tech_card(left_area, f"QUESTION DATA {self.current_index}/{len(self.question_order)}", border_color=self.PALETTE["secondary"])
        card_outer.pack(fill="both", expand=True)
        tk.Label(card_body, text=soal_text, wraplength=500, bg=self.PALETTE["bg_card"],
                 font=("Arial", 20, "bold"), justify="center", fg="white", padx=10, pady=20).pack(expand=True)

        # KANAN (JAWABAN)
        right_area = tk.Frame(split_container, bg=self.PALETTE["bg_main"])
        right_area.pack(side="right", fill="both", expand=True)

        self.selected_answer.set(None)
        for i, p in enumerate(pilihan):
            # --- [LOGIKA WARNA TETAP WARNA-WARNI] ---
            if self.current_concentration == "Multimedia":
                # Menggunakan list warna yang SUDAH diganti ungunya jadi orange
                btn_color = self.MULTI_COLORS[i % len(self.MULTI_COLORS)]
            elif self.current_concentration == "RPL":
                btn_color = "#006400"
            elif self.current_concentration == "TKJ":
                btn_color = "#003366"
            else:
                btn_color = "#333333"

            btn = tk.Button(right_area, text=p, font=("Arial", 16, "bold"), bg=btn_color, fg="white",
                            activebackground="white", activeforeground=btn_color,
                            relief="raised", bd=4, padx=20, pady=12, anchor="center", cursor="hand2")
            btn.config(command=lambda b=btn, v=p: self.process_answer(selected_val=v, btn_widget=b))
            btn.pack(fill="x", pady=8)
            self.option_widgets.append(btn)

        self.feedback_frame = tk.Frame(self.content_frame, bg=self.PALETTE["bg_main"])
        self.feedback_frame.pack(pady=10)

        self.time_left = 60
        self.countdown()
        self._place_bottom_nav(back_command=lambda: self.transition_loading(self.menu_screen))

    def _on_canvas_configure_quiz(self, event):
        self.quiz_canvas.itemconfigure(self.window_id, width=event.width)
        self._draw_tech_background(self.quiz_canvas, event.width, max(event.height, 2000))

    def countdown(self):
        if self.time_left > 0 and not self.answer_submitted:
            self.time_left -= 1
            self.timer_label.config(text=f"TIME: {self.time_left}s")
            if self.time_left <= 10: self.timer_label.config(fg=self.PALETTE["danger"])
            self.timer_job = self.root.after(1000, self.countdown)
        elif self.time_left <= 0: self.process_answer(time_out=True)

    def process_answer(self, selected_val=None, btn_widget=None, time_out=False):
        if self.answer_submitted: return
        self.answer_submitted = True
        if self.timer_job: self.root.after_cancel(self.timer_job)
        q_key = self.question_order[self.current_index - 1]
        correct = self.questions[q_key]["jawaban"]
        is_correct = (selected_val == correct) if not time_out else False
        earned = 0
        if is_correct:
            self.consecutive_correct += 1
            earned = 100 * self.consecutive_correct
            self.score += earned
        else:
            self.consecutive_correct = 0
        self.score_label.config(text=f"SCORE: {self.score}")
        self.streak_label.config(text=f"🔥 STREAK: {self.consecutive_correct}")
        self._play_sfx_for_result(is_correct, self.consecutive_correct)
        if self.consecutive_correct > 1:
            self.streak_label.config(fg="#FF4500")
        else:
            self.streak_label.config(fg="white")
        for btn in self.option_widgets:
            txt = btn.cget("text")
            btn.config(state="disabled", cursor="arrow")
            if txt == correct: btn.config(bg=self.PALETTE["success"], fg="black", disabledforeground="black")
            elif txt == selected_val and not is_correct: btn.config(bg=self.PALETTE["danger"], fg="white", disabledforeground="white")
            else: btn.config(bg="#222", fg="#555", disabledforeground="#555")
        msg = f"ACCESS GRANTED! +{earned}" if is_correct else "ACCESS DENIED!"
        if time_out: msg = "TIME OUT!"
        tk.Label(self.feedback_frame, text=msg, font=("Impact", 24), bg=self.PALETTE["bg_main"], fg=self.PALETTE["success"] if is_correct else self.PALETTE["danger"]).pack()
        self.root.after(2000, self.move_to_next)

    def move_to_next(self):
        self.current_index += 1
        self.show_quiz()

    def show_result(self):
        self.clear_frame()
        canvas = tk.Canvas(self.main_frame, bg=self.PALETTE["bg_main"], highlightthickness=0)
        canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.root.update()
        self._draw_tech_background(canvas, self.root.winfo_width(), self.root.winfo_height())
        main_container = tk.Frame(self.main_frame, bg=self.PALETTE["bg_main"])
        main_container.place(relx=0.5, rely=0.5, anchor="center", relwidth=1, relheight=1)
        center_content = tk.Frame(main_container, bg=self.PALETTE["bg_main"])
        center_content.pack(expand=True)
        tk.Label(center_content, text="SESSION COMPLETED 🎉", font=("Impact", 42), fg=self.PALETTE["text_light"], bg=self.PALETTE["bg_main"]).pack(pady=20)
        tk.Label(center_content, text="FINAL SCORE:", font=("Consolas", 18), fg=self.PALETTE["text_dim"], bg=self.PALETTE["bg_main"]).pack()
        tk.Label(center_content, text=f"{self.score}", font=("Consolas", 80, "bold"), fg=self.PALETTE["primary"], bg=self.PALETTE["bg_main"]).pack(pady=10)
        card_outer, card_body = self._create_tech_card(center_content, "SYSTEM MESSAGE", border_color=self.PALETTE["primary"])
        card_outer.pack(pady=20, fill="x", padx=100)
        tk.Label(card_body, text="Selamat! Gunakan hasil kuis ini sebagai refleksi awal minat Anda terhadap konsentrasi yang ada di PTIK UNIMA.", font=("Arial", 16), fg="white", bg=self.PALETTE["bg_card"], wraplength=800, justify="center").pack()
        bottom_frame = tk.Frame(main_container, bg=self.PALETTE["bg_main"], pady=40)
        bottom_frame.pack(side="bottom", fill="x")

        btn_back = tk.Button(bottom_frame, text="< KEMBALI KE MENU UTAMA",
                             command=lambda: self.transition_loading(self.menu_screen),
                             font=("Consolas", 16, "bold"), bg=self.PALETTE["secondary"], fg="white",
                             activebackground="#8A2BE2", activeforeground="white",
                             relief="raised", bd=5, padx=30, pady=15, cursor="hand2")
        btn_back.pack()
        self._place_bottom_nav()

    def _show_custom_exit_modal(self):
        self.exit_modal = tk.Frame(self.root, bg=self.PALETTE["overlay"])
        self.exit_modal.place(relx=0, rely=0, relwidth=1, relheight=1)
        modal_container = tk.Frame(self.exit_modal, bg=self.PALETTE["overlay"])
        modal_container.place(relx=0.5, rely=0.5, anchor="center")
        card_outer, card_body = self._create_tech_card(modal_container, "SYSTEM EXIT", border_color=self.PALETTE["danger"])
        card_outer.pack()
        tk.Label(card_body, text="KONFIRMASI KELUAR", font=("Impact", 28), fg=self.PALETTE["danger"], bg=self.PALETTE["bg_card"]).pack(pady=10)
        tk.Label(card_body, text="Semoga Kuis ini Bermanfaat, salam hangat dari HMJ PTIK.\n\nApakah Anda yakin ingin menutup aplikasi?", font=("Arial", 16), fg="white", bg=self.PALETTE["bg_card"], wraplength=500, justify="center").pack(pady=20)
        btn_frame = tk.Frame(card_body, bg=self.PALETTE["bg_card"])
        btn_frame.pack(pady=20)
        tk.Button(btn_frame, text="Ya, Keluar", command=self.confirm_exit, font=("Arial", 14, "bold"), bg=self.PALETTE["danger"], fg="white", activebackground="#D50000", activeforeground="white", relief="raised", bd=5, padx=25, pady=10).pack(side="left", padx=15)
        tk.Button(btn_frame, text="Tidak, Kembali", command=self.close_custom_exit_modal, font=("Arial", 14, "bold"), bg="#333", fg="white", activebackground="#444", activeforeground="white", relief="raised", bd=5, padx=25, pady=10).pack(side="left", padx=15)

if __name__ == "__main__":
    root = tk.Tk()
    app = QuizApp(root)
    root.mainloop()
