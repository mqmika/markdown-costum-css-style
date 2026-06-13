import customtkinter as ctk
from tkinter import filedialog, messagebox
import markdown
import os
import sys
from pathlib import Path

ctk.set_appearance_mode("dark")

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dönüştürülmüş Markdown</title>
    <style>
        body {{ font-family: 'Segoe UI', sans-serif; background-color: #0d0d11; color: #e0e0ed; padding: 40px; max-width: 800px; margin: 0 auto; line-height: 1.6; min-height: 100vh; }}
        .content {{ background: rgba(18, 18, 24, 0.9); padding: 30px; border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.7); position: relative; z-index: 10; border: 1px solid #2a2a35; }}
        h1, h2, h3 {{ color: #a370f7; }}
        code {{ background: #22222e; padding: 2px 6px; border-radius: 4px; color: #ff6b8b; }}
        pre {{ background: #050508; padding: 15px; border-radius: 8px; overflow-x: auto; border: 1px solid #1a1a24; }}
        #fx-canvas {{ position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; pointer-events: none; z-index: 1; }}
        {extra_css}
    </style>
</head>
<body>
    <canvas id="fx-canvas"></canvas>
    <div class="content">{content}</div>
    <script>{extra_js}</script>
</body>
</html>"""

EFFECTS = {
    "Yok 📝": {"css": "", "js": ""},
    "Kar Yağışı ❄️": {
        "css": "",
        "js": "const canvas = document.getElementById('fx-canvas'); const ctx = canvas.getContext('2d'); let flakes = []; function resize() { canvas.width = window.innerWidth; canvas.height = window.innerHeight; } window.addEventListener('resize', resize); resize(); for(let i=0; i<120; i++) { flakes.push({x: Math.random()*canvas.width, y: Math.random()*canvas.height, r: Math.random()*3+1, d: Math.random()*100}); } function draw() { ctx.clearRect(0,0,canvas.width,canvas.height); ctx.fillStyle = 'rgba(255,255,255,0.75)'; ctx.beginPath(); for(let i=0; i<flakes.length; i++) { let f = flakes[i]; ctx.moveTo(f.x, f.y); ctx.arc(f.x, f.y, f.r, 0, Math.PI*2, true); f.y += Math.cos(f.d) + 1 + f.r/2; f.x += Math.sin(f.d)*0.4; if(f.y > canvas.height) { flakes[i] = {x: Math.random()*canvas.width, y:0, r:f.r, d:f.d}; } } ctx.fill(); requestAnimationFrame(draw); } draw();"
    },
    "Cyberpunk Neon 🎆": {
        "css": "body { background-color: #030008 !important; } .content { border: 2px solid #ff0055; box-shadow: 0 0 25px #ff0055, inset 0 0 10px #ff0055; color: #00ffff; } h1, h2, h3 { color: #ff0055; text-shadow: 0 0 8px #ff0055; }",
        "js": ""
    },
    "Matrix Yağmuru 📟": {
        "css": "body { background-color: #000000 !important; } .content { border: 1px solid #00ff00; background: rgba(0, 5, 0, 0.9) !important; color: #00ff00 !important; } h1, h2, h3, code { color: #33ff33 !important; }",
        "js": "const canvas = document.getElementById('fx-canvas'); const ctx = canvas.getContext('2d'); function resize() { canvas.width = window.innerWidth; canvas.height = window.innerHeight; } window.addEventListener('resize', resize); resize(); const letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%&*'; const fontSize = 16; const columns = canvas.width / fontSize; const drops = Array(Math.floor(columns)).fill(1); function draw() { ctx.fillStyle = 'rgba(0, 0, 0, 0.05)'; ctx.fillRect(0, 0, canvas.width, canvas.height); ctx.fillStyle = '#0f0'; ctx.font = fontSize + 'px monospace'; for(let i=0; i<drops.length; i++) { const text = letters[Math.floor(Math.random()*letters.length)]; ctx.fillText(text, i*fontSize, drops[i]*fontSize); if(drops[i]*fontSize > canvas.height && Math.random() > 0.975) drops[i] = 0; drops[i]++; } } setInterval(draw, 33);"
    },
    "Uzay Yıldızları ✨": {
        "css": "body { background-color: #010105 !important; }",
        "js": "const canvas = document.getElementById('fx-canvas'); const ctx = canvas.getContext('2d'); let stars = []; function resize() { canvas.width = window.innerWidth; canvas.height = window.innerHeight; } window.addEventListener('resize', resize); resize(); for(let i=0; i<150; i++) { stars.push({x: Math.random()*canvas.width, y: Math.random()*canvas.height, size: Math.random()*2, alpha: Math.random(), speed: Math.random()*0.02}); } function draw() { ctx.clearRect(0,0,canvas.width,canvas.height); for(let i=0; i<stars.length; i++) { let s = stars[i]; ctx.fillStyle = `rgba(255,255,255,${s.alpha})`; ctx.fillRect(s.x, s.y, s.size, s.size); s.alpha += s.speed; if(s.alpha > 1 || s.alpha < 0) s.speed = -s.speed; } requestAnimationFrame(draw); } draw();"
    }
}

class MarkdownConverterGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Markdown HTML Converter Pro")
        self.geometry("600x420")
        self.resizable(False, False)
        self.configure(fg_color="#000000")
        
        if hasattr(sys, '_MEIPASS'):
            icon_path = os.path.join(sys._MEIPASS, "assets", "logo.ico")
        else:
            icon_path = os.path.join(os.path.dirname(__file__), "assets", "logo.ico")
            
        if os.path.exists(icon_path):
            self.iconbitmap(icon_path)
        
        self.selected_file_path = ""
        self.file_name_var = ctk.StringVar(value="Henüz bir Markdown dosyası seçilmedi...")
        
        self.title_label = ctk.CTkLabel(self, text="Markdown to HTML Converter", font=ctk.CTkFont(family="Arial", size=24, weight="bold"), text_color="#ffffff")
        self.title_label.pack(pady=(35, 25))
        
        self.file_frame = ctk.CTkFrame(self, fg_color="#0b0b0f", border_color="#1f1f2e", border_width=1, corner_radius=8)
        self.file_frame.pack(pady=10, fill="x", padx=40)
        self.file_frame.grid_columnconfigure(1, weight=1)
        
        self.btn_select = ctk.CTkButton(self.file_frame, text="Dosya Seç (.md)", command=self.select_file, width=140, fg_color="#1f1f2e", hover_color="#2d2d3f", text_color="#ffffff", font=ctk.CTkFont(weight="bold"), corner_radius=6)
        self.btn_select.grid(row=0, column=0, padx=15, pady=15)
        
        self.lbl_file = ctk.CTkLabel(self.file_frame, textvariable=self.file_name_var, text_color="#52526b", anchor="w", font=ctk.CTkFont(slant="italic"))
        self.lbl_file.grid(row=0, column=1, padx=(0, 15), pady=15, sticky="ew")
        
        self.fx_frame = ctk.CTkFrame(self, fg_color="#0b0b0f", border_color="#1f1f2e", border_width=1, corner_radius=8)
        self.fx_frame.pack(pady=10, fill="x", padx=40)
        self.fx_frame.grid_columnconfigure(1, weight=1)
        
        self.lbl_fx = ctk.CTkLabel(self.fx_frame, text="Arka Plan Efekti:", font=ctk.CTkFont(size=14), text_color="#a0a0b0", anchor="w")
        self.lbl_fx.grid(row=0, column=0, padx=20, pady=15, sticky="w")
        
        self.fx_menu = ctk.CTkOptionMenu(self.fx_frame, values=list(EFFECTS.keys()), fg_color="#1f1f2e", button_color="#151522", button_hover_color="#252538", text_color="#ffffff", corner_radius=6)
        self.fx_menu.grid(row=0, column=1, padx=20, pady=15, sticky="ew")
        
        self.btn_convert = ctk.CTkButton(self, text="DÖNÜŞTÜR VE İNDİRİLENLERE KAYDET", command=self.convert_and_save_user_choice, fg_color="#238636", hover_color="#2ea043", text_color="#ffffff", font=ctk.CTkFont(size=14, weight="bold"), height=48, corner_radius=6)
        self.btn_convert.pack(pady=(35, 20), fill="x", padx=40)

    def select_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Markdown Files", "*.md")])
        if file_path:
            self.selected_file_path = file_path
            filename = os.path.basename(file_path)
            if len(filename) > 35:
                filename = filename[:32] + "..."
            self.lbl_file.configure(text_color="#58a6ff")
            self.file_name_var.set(filename)

    def convert_and_save_user_choice(self):
        if not self.selected_file_path:
            messagebox.showwarning("Dosya Eksik", "Lütfen önce dönüştürülecek bir .md dosyası seçin!")
            return
        try:
            downloads_dir = str(Path.home() / "Downloads")
            base_name = os.path.splitext(os.path.basename(self.selected_file_path))[0]
            suggested_filename = f"{base_name}_efektli.html"
            save_path = filedialog.asksaveasfilename(initialdir=downloads_dir, initialfile=suggested_filename, defaultextension=".html", filetypes=[("HTML Files", "*.html")], title="Efektli Dosyayı Kaydet")
            if not save_path:
                return
            with open(self.selected_file_path, "r", encoding="utf-8") as f:
                md_content = f.read()
            html_body = markdown.markdown(md_content, extensions=['extra'])
            chosen_fx_name = self.fx_menu.get()
            fx_data = EFFECTS[chosen_fx_name]
            final_html = HTML_TEMPLATE.format(extra_css=fx_data["css"], content=html_body, extra_js=fx_data["js"])
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(final_html)
            messagebox.showinfo("Başarılı!", f"Dosya başarıyla kaydedildi:\n\n{os.path.basename(save_path)}")
        except Exception as e:
            messagebox.showerror("Hata", f"Dönüştürme esnasında bir hata oluştu:\n{str(e)}")

if __name__ == "__main__":
    app = MarkdownConverterGUI()
    app.mainloop()