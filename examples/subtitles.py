from tkinter import *
from tkinter.font import Font
import time

# from cfg.subtitles import *
import ash_cfgs
import threading
class SubtitleWindow:
    def __init__(self):

        subtitles_cfg = {
            "window_width": ash_cfgs.subtitles_window_width_cfg,
            "window_height": ash_cfgs.subtitles_window_height_cfg,
            "title": ash_cfgs.subtitles_title_cfg,
            "root_bg": ash_cfgs.subtitles_root_bg_cfg,
            "label_bg": ash_cfgs.subtitles_label_bg_cfg,
            "label_fg": ash_cfgs.subtitles_label_fg_cfg,
            "family": ash_cfgs.subtitles_family_cfg,
            "font_size": ash_cfgs.subtitles_font_size_cfg,
            "weight": ash_cfgs.subtitles_weight_cfg
        }

        print('init_subtitles')
        window_width = subtitles_cfg["window_width"]
        window_height = subtitles_cfg["window_height"]

        self.root = Tk()
        self.root.title(subtitles_cfg['title'])
        self.root.geometry(f"{window_width}x{window_height}+0+0")
        # Set to red
        self.root.configure(bg=subtitles_cfg["root_bg"])

        self.outline_font = Font(family=subtitles_cfg['family'], size=subtitles_cfg["font_size"])
        self.outline_font.configure(weight=subtitles_cfg["weight"])

        self.text_label = Label(self.root, bg=subtitles_cfg["label_bg"], fg=subtitles_cfg["label_fg"],
                                font=self.outline_font, wraplength=window_width)
        self.text_label.pack(expand=True)

        self.lock = threading.Lock()

    def clean_text_from_window(self):
        self.text_label.config(text="")
        self.root.update()

    def resize_text_label(self, content):
        text_width = self.outline_font.measure(content)
        text_height = self.outline_font.metrics("linespace")

        window_width = self.root.winfo_reqwidth()
        window_height = self.root.winfo_reqheight()

        if text_width < window_width * 1.5 and text_height < window_height * 1.5:
            if self.outline_font.actual("size") != ash_cfgs.subtitles_font_size_cfg:
                self.outline_font.configure(size=ash_cfgs.subtitles_font_size_cfg)
                self.update_wrapped_text(content)
            return

        while text_width > window_width * 2 or text_height > window_height * 2:
            current_font_size = self.outline_font.actual("size")
            current_font_size -= 4
            if current_font_size < 40:
                break 
            self.outline_font.configure(size=current_font_size)
            text_width = self.outline_font.measure(content)
            text_height = self.outline_font.metrics("linespace")

        self.update_wrapped_text(content)

    def update_wrapped_text(self, content):
        words = content.split()
        lines = []
        current_line = ""
        for word in words:
            word_width = self.outline_font.measure(word)
            if self.outline_font.measure(current_line + word) > self.root.winfo_reqwidth() * 2:
                lines.append(current_line)
                current_line = word + " "
            else:
                current_line += word + " "
        if current_line.strip():
            lines.append(current_line)

        self.text_label.config(text="\n".join(lines))

    def display_progressive_words(self, text, delay=0.4):
        with self.lock:
            time.sleep(ash_cfgs.subtitles_start_delay_cfg)
            text = text.encode('utf-8').decode('ascii', 'ignore')
            words = text.split()
            for i in range(1, len(words) + 1):
                progressive_text = ' '.join(words[:i])
                self.text_label.config(text=progressive_text, font=self.outline_font)
                self.resize_text_label(progressive_text)
                self.text_label.config(text=progressive_text, font=self.outline_font)

                self.root.update()
                time.sleep(delay)


    def run(self):
        # print('run_subtitles')  
        self.root.mainloop()

# if __name__ == "__main__":
#     subtitle_window = SubtitleWindow()
#     subtitle_window.display_progressive_words("Hello, this is a sample subtitle.", delay=0.2)
#     subtitle_window.root.mainloop()
