import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import threading
from src.i18n import t, set_language, get_language
from src.bot import run_bot

# Define global Tkinter elements
root = None
label_search = None
job_entry = None
label_city = None
city_entry = None
label_title = None
title_entry = None
label_pages = None
pages_entry = None
hiring_var = None
hiring_check = None
start_button = None
lang_button = None
pause_button = None
clear_db_button = None

pause_event = threading.Event()
pause_event.set()  # Default to not paused


def update_gui_language():
    if root:
        root.title(t("window_title"))
    if label_search:
        label_search.config(text=t("label_search"))
    if label_city:
        label_city.config(text=t("label_city"))
    if label_title:
        label_title.config(text=t("label_title"))
    if label_pages:
        label_pages.config(text=t("label_pages"))
    if hiring_check:
        hiring_check.config(text=t("checkbox_hiring"))
    if start_button:
        start_button.config(text=t("btn_start"))
    if lang_button:
        lang_button.config(text=t("btn_language"))
    if pause_button:
        if pause_event and not pause_event.is_set():
            pause_button.config(text=t("btn_resume"))
        else:
            pause_button.config(text=t("btn_pause"))
    if clear_db_button:
        clear_db_button.config(text=t("btn_clear_db"))


def toggle_language():
    new_lang = "pt" if get_language() == "en" else "en"
    set_language(new_lang)
    update_gui_language()


bot_running = False


def toggle_pause():
    global bot_running
    if not bot_running:
        return
    if pause_event.is_set():
        pause_event.clear()
        pause_button.config(text=t("btn_resume"))
    else:
        pause_event.set()
        pause_button.config(text=t("btn_pause"))


def clear_history():
    if messagebox.askyesno(t("clear_db_confirm_title"), t("clear_db_confirm_msg")):
        from src.db import clear_contacted_profiles
        clear_contacted_profiles()
        messagebox.showinfo(t("success_title"), t("clear_db_success"))


def enable_start_button():
    global bot_running
    bot_running = False
    if root:
        root.after(0, lambda: start_button.config(state="normal"))
        root.after(0, lambda: pause_button.config(state="disabled", text=t("btn_pause")))
        root.after(0, lambda: clear_db_button.config(state="normal"))


def start_bot_thread():
    global bot_running
    if bot_running:
        return

    city = city_entry.get().strip()
    job = job_entry.get().strip()
    title = title_entry.get().strip()
    hiring = hiring_var.get()

    try:
        pages = int(pages_entry.get().strip())
        pages = max(1, min(20, pages))
    except:
        pages = 1

    if not job:
        messagebox.showwarning(t("warning_title"), t("warning_fill"))
        return

    # --- Note popup before starting ---
    note_text = simpledialog.askstring(
        t("note_popup_title"),
        t("note_popup_msg"),
        parent=root
    )
    if note_text is None:
        # User cancelled the dialog — abort
        return
    note_text = note_text.strip()

    # Security warning for note character length
    if len(note_text) > 300:
        if get_language() == "pt":
            msg = f"A nota digitada tem {len(note_text)} caracteres. O LinkedIn limita a 300 caracteres. Ela será truncada automaticamente para evitar falhas."
        else:
            msg = f"The note has {len(note_text)} characters. LinkedIn limits notes to 300 characters. It will be truncated automatically to prevent failures."
        messagebox.showwarning(t("warning_title"), msg)
        note_text = note_text[:300]

    bot_running = True
    pause_event.set()  # Reset to running state
    start_button.config(state="disabled")
    pause_button.config(state="normal", text=t("btn_pause"))
    clear_db_button.config(state="disabled")

    if note_text:
        print(f"  {t('note_set', note=note_text[:50])}")
    else:
        print(f"  {t('note_empty')}")

    print(f"\n{t('starting')}")
    print(f"  {t('search_label')}: {job}")
    print(f"  {t('city_label')}: {city if city else t('none')}")
    print(f"  {t('title_label')}: {title if title else t('any')}")
    print(f"  {t('hiring_label')}: {t('yes') if hiring else t('no')}")
    print(f"  {t('pages_label')}: {pages}")
    print(f"  {t('note_label')}: {note_text if note_text else t('none')}")

    thread = threading.Thread(
        target=run_bot, args=(city, job, title, pages, hiring, note_text, enable_start_button, pause_event)
    )
    thread.daemon = True
    thread.start()


def init_gui():
    global root, label_search, job_entry, label_city, city_entry
    global label_title, title_entry, label_pages, pages_entry
    global hiring_var, hiring_check, start_button, lang_button

    root = tk.Tk()
    root.title(t("window_title"))
    root.geometry("340x510")
    root.resizable(False, False)

    lang_button = ttk.Button(root, text=t("btn_language"), command=toggle_language)
    lang_button.pack(anchor="ne", padx=10, pady=(5, 0))

    label_search = tk.Label(root, text=t("label_search"))
    label_search.pack(pady=(5, 2))
    job_entry = tk.Entry(root, width=35)
    job_entry.pack(pady=(0, 5))

    label_city = tk.Label(root, text=t("label_city"))
    label_city.pack(pady=(5, 2))
    city_entry = tk.Entry(root, width=35)
    city_entry.pack(pady=(0, 5))

    label_title = tk.Label(root, text=t("label_title"))
    label_title.pack(pady=(5, 2))
    title_entry = tk.Entry(root, width=35)
    title_entry.pack(pady=(0, 5))

    label_pages = tk.Label(root, text=t("label_pages"))
    label_pages.pack(pady=(5, 2))
    pages_entry = tk.Entry(root, width=10)
    pages_entry.insert(0, "3")
    pages_entry.pack(pady=(0, 5))

    hiring_var = tk.BooleanVar()
    hiring_check = tk.Checkbutton(
        root, text=t("checkbox_hiring"), variable=hiring_var
    )
    hiring_check.pack(pady=(5, 5))

    start_button = ttk.Button(root, text=t("btn_start"), command=start_bot_thread)
    start_button.pack(pady=(10, 5))

    global pause_button
    pause_button = ttk.Button(root, text=t("btn_pause"), command=toggle_pause, state="disabled")
    pause_button.pack(pady=(5, 5))

    global clear_db_button
    clear_db_button = ttk.Button(root, text=t("btn_clear_db"), command=clear_history)
    clear_db_button.pack(pady=(5, 10))

    root.mainloop()
