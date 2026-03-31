import customtkinter as ctk
import os
import json
import random
import pyfiglet
import shutil

# CONFIG
BG_TEST = "#160f07"
FG_TEST = "#a87f48"
ACCENT_TEST = "#cfa86b" 
SAMPLE_DIR = "SampleText"
FONT_DIR = "FigletFonts"

class SampleTabReplica(ctk.CTk):
    def __init__(self, use_accent=True):
        super().__init__()
        self.title("Pairz Interactive Renderer")
        self.geometry("1400x1000") 
        self.configure(fg_color=BG_TEST)
        
        self.current_fg = FG_TEST
        self.current_accent = ACCENT_TEST if use_accent else None
        
        # Scaling & Layout States
        self.body_font_size = 10
        self.title_font_size = 10
        self.title_render_width = 250
        self.current_font_name = "standard"
        self.justifications = ["left", "center", "right"]
        self.just_index = 1 # Center
        
        try:
            self.pyfiglet_base = os.path.dirname(pyfiglet.__file__)
            self.internal_font_dir = os.path.join(self.pyfiglet_base, "fonts")
        except:
            self.internal_font_dir = ""

        self.setup_ui()
        self.load_sample()

    def setup_ui(self):
        # 1. Scrollable Frame (Hidden Scrollbar)
        self.content_frame = ctk.CTkScrollableFrame(
            self, fg_color="transparent", corner_radius=0,
            scrollbar_fg_color=BG_TEST, scrollbar_button_color=BG_TEST, scrollbar_button_hover_color=BG_TEST
        )
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=(0, 80))
        self.content_frame._scrollbar.configure(width=0)

        # 2. Title Entity
        self.title_display = ctk.CTkLabel(self.content_frame, text="", font=("Courier New", self.title_font_size), justify="center")
        self.title_display.pack(pady=(40, 30), fill="x", expand=True)

        # 3. Body Entity
        self.body_display = ctk.CTkTextbox(self.content_frame, fg_color="transparent", border_width=0, activate_scrollbars=False, wrap="word")
        self.body_display.pack(pady=10, anchor="center")

        # --- KEYBOARD & MOUSE BINDINGS ---
        self.bind("<space>", lambda e: self.load_sample())
        self.bind("<Left>", lambda e: self.change_justification(-1))
        self.bind("<Right>", lambda e: self.change_justification(1))
        self.bind("<Up>", lambda e: self.adjust_body_font(1))
        self.bind("<Down>", lambda e: self.adjust_body_font(-1))
        
        # Mouse Scaling
        self.bind("<Control-MouseWheel>", self.scale_body_mouse)
        self.bind("<Control-Button-4>", self.scale_body_mouse)
        self.bind("<Control-Button-5>", self.scale_body_mouse)
        
        self.bind("<Shift-MouseWheel>", self.scale_title_mouse)
        self.bind("<Shift-Button-4>", self.scale_title_mouse)
        self.bind("<Shift-Button-5>", self.scale_title_mouse)

        # 4. Bottom Bar
        self.button_bar = ctk.CTkFrame(self, fg_color=BG_TEST, height=80, corner_radius=0)
        self.button_bar.place(relx=0.5, rely=1.0, anchor="s", relwidth=1.0)
        self.btn = ctk.CTkButton(self.button_bar, text="SPACEBAR FOR RANDOM", command=self.load_sample, fg_color="#333", width=300, height=40)
        self.btn.pack(pady=20)

    def change_justification(self, direction):
        self.just_index = (self.just_index + direction) % len(self.justifications)
        self.update_ui_elements(update_title=False)

    def adjust_body_font(self, amount):
        self.body_font_size = max(6, self.body_font_size + amount)
        self.update_ui_elements(update_title=False)

    def scale_body_mouse(self, event):
        delta = 1 if (event.num == 4 or event.delta > 0) else -1
        self.adjust_body_font(delta)

    def scale_title_mouse(self, event):
        delta = 1 if (event.num == 4 or event.delta > 0) else -1
        self.title_font_size = max(4, self.title_font_size + delta)
        self.title_render_width = max(50, self.title_render_width + (delta * 5))
        self.update_ui_elements(update_body=False)

    def update_ui_elements(self, update_title=True, update_body=True):
        if not hasattr(self, 'current_data'): return
        mode = self.justifications[self.just_index]

        if update_title:
            raw_title = self.current_data.get("TITLE", "UNTITLED")
            title_color = self.current_accent if self.current_accent else self.current_fg
            try:
                fig_text = pyfiglet.figlet_format(raw_title, font=self.current_font_name, width=self.title_render_width)
                self.title_display.configure(text=fig_text, text_color=title_color, font=("Courier New", self.title_font_size))
            except: pass

        if update_body:
            json_width = self.current_data.get("WIDTH", 700)
            json_font = self.current_data.get("FONT_FAMILY", "Helvetica")
            text_content = self.current_data.get("TEXT", "")
            lines = text_content.count('\n') + (len(text_content) // (json_width // 6)) + 4
            dynamic_height = max(100, lines * (self.body_font_size + 8)) 

            self.body_display.configure(state="normal")
            self.body_display.configure(font=(json_font, self.body_font_size), height=dynamic_height)
            self.body_display.tag_add("align", "1.0", "end")
            self.body_display.tag_config("align", justify=mode)
            self.body_display.configure(state="disabled")

    def load_sample(self):
        try:
            sample_files = [f for f in os.listdir(SAMPLE_DIR) if f.endswith('.json')]
            if not sample_files: return
            with open(os.path.join(SAMPLE_DIR, random.choice(sample_files)), "r") as f:
                self.current_data = json.load(f)

            font_files = [f for f in os.listdir(FONT_DIR) if f.endswith(('.flf', '.tlf'))]
            if font_files:
                selected_file = random.choice(font_files)
                self.current_font_name = os.path.splitext(selected_file)[0]
                dest_path = os.path.join(self.internal_font_dir, selected_file)
                if not os.path.exists(dest_path):
                    shutil.copy2(os.path.join(FONT_DIR, selected_file), dest_path)
            
            self.body_display.configure(state="normal")
            self.body_display.delete("1.0", "end")
            self.body_display.insert("1.0", self.current_data.get("TEXT", ""))
            self.body_display.configure(width=self.current_data.get("WIDTH", 700), text_color=self.current_fg)
            self.body_display.pack_configure(padx=self.current_data.get("PADDING", 30))
            self.update_ui_elements()
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    app = SampleTabReplica()
    app.mainloop()
