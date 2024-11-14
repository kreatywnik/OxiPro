import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, Toplevel, Checkbutton, IntVar, StringVar, OptionMenu
import openai
from dotenv import load_dotenv
import os
import pyperclip
import webbrowser
import threading
from PIL import Image, ImageTk
import requests
from io import BytesIO

# Wczytaj zmienne środowiskowe z pliku .env, jeśli jest obecny
load_dotenv()

# Pobierz klucz API z systemowych zmiennych środowiskowych
openai_api_key = os.getenv('OPENAI_API_KEY')

# Sprawdź, czy klucz API jest dostępny
if not openai_api_key:
    raise ValueError("Klucz API nie został znaleziony. Upewnij się, że zmienna środowiskowa OPENAI_API_KEY jest ustawiona.")

# Przypisz klucz API do OpenAI
openai.api_key = openai_api_key

def run_in_thread(target, *args):
    start_loading_animation()
    def wrapper():
        try:
            target(*args)
        finally:
            stop_loading_animation()
    thread = threading.Thread(target=wrapper)
    thread.start()

root = tk.Tk()
root.title("Wybierz tryb działania")

# Ustawienie favicony z podanego linku
favicon_url = "https://faldowski.pl/wp-content/uploads/2024/11/OxiPro-fafi.png"
try:
    response = requests.get(favicon_url)
    response.raise_for_status()
    favicon_image = Image.open(BytesIO(response.content))
    favicon_photo = ImageTk.PhotoImage(favicon_image)
    root.iconphoto(False, favicon_photo)  # Ustawienie favicony
except Exception as e:
    messagebox.showwarning("Ostrzeżenie", f"Nie udało się załadować favicony: {str(e)}")

css_var = IntVar()
image_size_var = StringVar(value="512x512")
text_width_var = StringVar(value="60%")

loading_canvas = tk.Canvas(root, width=50, height=50, highlightthickness=0)
loading_circle = None
loading_animation_running = False

def start_loading_animation():
    global loading_animation_running
    loading_animation_running = True
    loading_canvas.pack(pady=(10, 20))
    animate_loading_circle()

def stop_loading_animation():
    global loading_animation_running
    loading_animation_running = False
    loading_canvas.delete("all")

def animate_loading_circle(angle=0):
    global loading_animation_running, loading_circle
    if loading_animation_running:
        loading_canvas.delete("all")
        x0, y0, x1, y1 = 10, 10, 40, 40
        loading_canvas.create_arc(x0, y0, x1, y1, start=angle, extent=120, style="arc", width=4)
        root.after(50, animate_loading_circle, (angle + 10) % 360)

def read_article(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        messagebox.showerror("Błąd", f"Nie można odczytać pliku: {str(e)}")
        return None

def get_html_from_openai(article_content, prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"{prompt}\n\n{article_content}"}
            ],
            max_tokens=3000,
            temperature=0.5
        )
        html_content = response['choices'][0]['message']['content'].strip()
        html_content = html_content.replace("```html", "").replace("```", "").strip()
        return html_content
    except Exception as e:
        messagebox.showerror("Błąd", f"Wystąpił problem z API OpenAI: {str(e)}")
        return None

def add_css_styles(html_content):
    css = f"""
    <style>
        body {{
            max-width: {text_width_var.get()};
            margin: 0 auto;
            font-family: Arial, sans-serif;
            line-height: 1.6;
        }}
        img {{
            display: block;
            max-width: 100%;
            height: auto;
            margin: 0 auto;
        }}
        figure {{
            text-align: center;
            margin: 0;
            margin-bottom: 20px;
        }}
        figcaption {{
            font-style: italic;
            text-align: center;
            margin-top: 5px;
        }}
    </style>
    """
    return css + html_content

def generate_image_from_prompt(prompt, article_context):
    try:
        modified_prompt = f"Realistic photograph, highly detailed, high resolution, related to {article_context}. {prompt}"
        response = openai.Image.create(
            prompt=modified_prompt,
            n=1,
            size=image_size_var.get()
        )
        image_url = response['data'][0]['url']
        return image_url
    except Exception as e:
        messagebox.showerror("Błąd", f"Wystąpił problem z generowaniem obrazu: {str(e)}")
        return None

def replace_image_placeholders(html_content, article_context):
    image_placeholders = html_content.split('<img src="image_placeholder.jpg" alt="')
    if len(image_placeholders) > 1:
        for i in range(1, len(image_placeholders)):
            alt_text = image_placeholders[i].split('">')[0]
            image_url = generate_image_from_prompt(alt_text, article_context[:100])
            if image_url:
                html_content = html_content.replace(
                    f'<img src="image_placeholder.jpg" alt="{alt_text}">',
                    f'<figure style="text-align: center;"><img src="{image_url}" alt="{alt_text}" style="display: block; max-width: 100%; height: auto; margin: 0 auto;"><figcaption style="font-style: italic; text-align: center; margin-top: 5px;">{alt_text}</figcaption></figure>'
                )
    return html_content

def open_file_with_options(mode, include_styles):
    file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    if file_path:
        run_in_thread(process_file, file_path, mode, include_styles)

def process_file(file_path, mode, include_styles):
    article_content = read_article(file_path)
    if article_content:
        prompt = (
            "Przetwórz poniższy artykuł na kod HTML z odpowiednimi tagami. "
            "W miejscach, gdzie warto dodać grafiki, użyj <img src=\"image_placeholder.jpg\" alt=\"Opis obrazka\">. "
            "Cały kod umieść tylko wewnątrz tagów <body>."
        )
        html_content = get_html_from_openai(article_content, prompt)
        if html_content:
            if mode == 'projekt':
                if include_styles:
                    html_content = add_css_styles(html_content)
                html_content_with_images = replace_image_placeholders(html_content, article_content)
                show_html_window(html_content_with_images)
            else:
                show_html_window(html_content)

def show_html_window(html_content):
    html_window = Toplevel(root)
    html_window.title("Wygenerowany kod HTML")

    # Dodanie logo do okna
    try:
        response = requests.get(logo_url)
        response.raise_for_status()
        logo_image = Image.open(BytesIO(response.content))
        logo_image = logo_image.resize((100, 23), Image.LANCZOS)
        logo_photo = ImageTk.PhotoImage(logo_image)
        logo_label = tk.Label(html_window, image=logo_photo)
        logo_label.image = logo_photo
        logo_label.pack(pady=(10, 5))
    except Exception as e:
        messagebox.showwarning("Ostrzeżenie", f"Nie udało się załadować logo: {str(e)}")

    text_area = scrolledtext.ScrolledText(html_window, wrap=tk.WORD, width=100, height=30)
    text_area.insert(tk.INSERT, html_content)
    text_area.configure(state='disabled')
    text_area.pack(padx=10, pady=10)

    # Checkbox do kopiowania tylko zawartości <body>
    copy_only_body_var = IntVar()
    copy_checkbox = Checkbutton(html_window, text="Kopiuj tylko zawartość <body>", variable=copy_only_body_var)
    copy_checkbox.pack(pady=5)

    # Przyciski
    button_frame = tk.Frame(html_window)
    button_frame.pack(pady=5)

    copy_button = tk.Button(button_frame, text="Skopiuj kod", command=lambda: copy_to_clipboard(html_content, copy_only_body_var.get()))
    copy_button.pack(side="left", padx=5)

    save_button = tk.Button(button_frame, text="Zapisz", command=lambda: save_html_file(html_content))
    save_button.pack(side="left", padx=5)

    preview_button = tk.Button(button_frame, text="Podgląd", command=lambda: show_web_preview(html_content))
    preview_button.pack(side="left", padx=5)

    save_preview_button = tk.Button(button_frame, text="Zapisz podgląd", command=lambda: save_html_preview(html_content))
    save_preview_button.pack(side="left", padx=5)

def copy_to_clipboard(content, copy_only_body):
    if copy_only_body:
        start_body = content.find("<body>") + len("<body>")
        end_body = content.find("</body>")
        if start_body != -1 and end_body != -1:
            content = content[start_body:end_body].strip()
    pyperclip.copy(content)
    messagebox.showinfo("Informacja", "Kod skopiowany do schowka!")

def save_html_file(html_content):
    try:
        with open("artykul.html", "w", encoding="utf-8") as file:
            file.write(html_content)
        messagebox.showinfo("Informacja", "Kod został zapisany do pliku artykul.html.")
    except Exception as e:
        messagebox.showerror("Błąd", f"Nie można zapisać pliku: {str(e)}")

def save_html_preview(html_content):
    try:
        full_html = f"""<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Podgląd Artykułu</title>
    <style>
        body {{
            max-width: 60%;
            margin: 0 auto;
            font-family: Arial, sans-serif;
            line-height: 1.6;
        }}
        img {{
            display: block;
            max-width: 100%;
            height: auto;
            margin: 0 auto;
        }}
        figure {{
            text-align: center;
            margin: 0;
            margin-bottom: 20px;
        }}
        figcaption {{
            font-style: italic;
            text-align: center;
            margin-top: 5px;
        }}
    </style>
</head>
<body>
{html_content}
</body>
</html>"""
        with open("podglad.html", "w", encoding="utf-8") as file:
            file.write(full_html)
        messagebox.showinfo("Informacja", "Podgląd został zapisany do pliku podglad.html.")
    except Exception as e:
        messagebox.showerror("Błąd", f"Nie można zapisać pliku: {str(e)}")

def generate_html_template():
    html_template = """<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Podgląd Artykułu</title>
    <style>
        body {
            max-width: 60%;
            margin: 0 auto;
            font-family: Arial, sans-serif;
            line-height: 1.6;
        }
        img {
            display: block;
            max-width: 100%;
            height: auto;
            margin: 0 auto;
        }
        figure {
            text-align: center;
            margin: 0;
            margin-bottom: 20px;
        }
        figcaption {
            font-style: italic;
            text-align: center;
            margin-top: 5px;
        }
    </style>
</head>
<body>
    <!-- Wklej tutaj treść artykułu -->
</body>
</html>"""
    try:
        with open("szablon.html", "w", encoding="utf-8") as file:
            file.write(html_template)
        messagebox.showinfo("Informacja", "Szablon HTML został zapisany do pliku szablon.html.")
    except Exception as e:
        messagebox.showerror("Błąd", f"Nie można zapisać pliku: {str(e)}")

def generate_html_template_button():
    generate_html_template()
    messagebox.showinfo("Informacja", "Szablon HTML został wygenerowany.")

def show_web_preview(html_content):
    try:
        preview_file_path = "podglad.html"
        with open(preview_file_path, "w", encoding="utf-8") as file:
            file.write(html_content)
        webbrowser.open(preview_file_path)
    except Exception as e:
        messagebox.showerror("Błąd", f"Nie można otworzyć podglądu: {str(e)}")

def show_options_window():
    options_window = Toplevel(root)
    options_window.title("Opcje")
    options_window.geometry("300x200")
    options_window.configure(padx=10, pady=10)
    tk.Label(options_window, text="Rozdzielczość obrazów:").pack(pady=5)
    image_size_menu = OptionMenu(options_window, image_size_var, "256x256", "512x512", "1024x1024", "1024x1792", "1792x1024")
    image_size_menu.pack(pady=5)
    tk.Label(options_window, text="Szerokość tekstu:").pack(pady=5)
    text_width_menu = OptionMenu(options_window, text_width_var, "60%", "70%", "80%", "90%")
    text_width_menu.pack(pady=5)
    close_button = tk.Button(options_window, text="Zamknij", command=options_window.destroy)
    close_button.pack(pady=10)

# Główne menu
frame = tk.Frame(root, padx=20, pady=20)
frame.pack(pady=(30, 10))

logo_url = "https://faldowski.pl/wp-content/uploads/2024/11/OxiPro.png"
try:
    response = requests.get(logo_url)
    response.raise_for_status()
    logo_image = Image.open(BytesIO(response.content))
    logo_image = logo_image.resize((200, 46), Image.LANCZOS)
    logo_photo = ImageTk.PhotoImage(logo_image)
    logo_label = tk.Label(frame, image=logo_photo)
    logo_label.image = logo_photo
    logo_label.pack(pady=(0, 50))
except Exception as e:
    messagebox.showwarning("Ostrzeżenie", f"Nie udało się załadować logo: {str(e)}")

# Przycisk "Surowy kod HTML"
raw_button = tk.Button(frame, text="Surowy kod HTML", command=lambda: open_file_with_options('surowy', include_styles=False))
raw_button.pack(pady=5)

# Ramka z przyciskami "Projekt z grafikami" i "Opcje"
project_options_frame = tk.Frame(frame)
project_options_frame.pack(pady=5)

project_button = tk.Button(project_options_frame, text="Projekt z grafikami", command=lambda: open_file_with_options('projekt', include_styles=css_var.get()))
project_button.pack(side="left", padx=5)

options_button = tk.Button(project_options_frame, text="⚙️ Opcje", command=show_options_window)
options_button.pack(side="left", padx=5)

# Przycisk "Dodaj style CSS"
checkbox = Checkbutton(frame, text="Dodaj style CSS", variable=css_var)
checkbox.pack(pady=5)

# Przycisk do generowania szablonu HTML (umieszczony poniżej checkboxa)
template_button = tk.Button(frame, text="Wygeneruj szablon HTML", command=generate_html_template_button)
template_button.pack(pady=5)

loading_canvas.pack(pady=(10, 20))

root.geometry("400x500")
root.mainloop()
