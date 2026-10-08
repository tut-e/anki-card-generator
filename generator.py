import csv
import io
import os
import sys
import pyperclip
from gtts import gTTS


def clean_filename(filename):
    invalid_chars = ['/', '\\', '?', '*', ':', '"', '<', '>', '|']
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename


def get_existing_verbs(filepath):
    existing_verbs = set()
    if os.path.exists(filepath):
        try:
            with open(filepath, mode="r", encoding="utf-8") as f:
                reader = csv.reader(f, delimiter=";")
                for row in reader:
                    if row:
                        raw_front = row[0]
                        if "font-size" in raw_front:
                            # Безопасно вытаскиваем глагол из обновленной верстки
                            verb = raw_front.split(";'>")[-1].split("</div>")[0]
                            existing_verbs.add(verb.strip().lower())
        except Exception:
            pass
    return existing_verbs


def create_flashcards_from_clipboard_no_header():
    data_str = pyperclip.paste()

    if not data_str.strip():
        print("[-] Error: Clipboard is empty. Copy lines from your table and run again.")
        return

    sound_dir = "sound_cards"
    output_filename = "anki_audio_flashcards.csv"

    if not os.path.exists(sound_dir):
        os.makedirs(sound_dir)

    existing_verbs = get_existing_verbs(output_filename)

    f = io.StringIO(data_str.strip())
    reader = csv.reader(f, delimiter="\t")

    rows = []
    for row in reader:
        if not row or len(row) < 7:
            continue
        if "verb" in row[1].lower() or "перевод" in row[4].lower() if len(row) > 4 else False:
            continue

        verb_to_check = row[1].strip()
        if verb_to_check.lower() in existing_verbs:
            continue

        rows.append(row)

    total_cards = len(rows)

    if total_cards == 0:
        print("[~] No new verbs found. All copied verbs are already in your CSV file!")
        return

    cards = []
    print(f"[+] New rows to process: {total_cards}\n")

    # Общие CSS-стили для контейнера-карточки, чтобы она не зависела от темы телефона
    card_style = (
        "font-family: Arial, sans-serif; "
        "max-width: 420px; "
        "margin: 10px auto; "
        "padding: 20px; "
        "background-color: #ffffff; "  # Всегда белый фон самой карточки
        "border-radius: 12px; "  # Скругление углов
        "box-shadow: 0 4px 15px rgba(0,0,0,0.1); "  # Мягкая тень
        "border: 1px solid #e1e8ed; "
        "text-align: center;"
    )

    for index, row in enumerate(rows, start=1):
        verb = row[1].strip()
        v2 = row[2].strip()
        v3 = row[3].strip()
        translation = row[4].strip()
        collocs = row[5].strip()
        phrasal = row[6].strip()
        example = row[7].strip() if len(row) > 7 else ""

        safe_verb_name = clean_filename(verb)

        # --- AUDIO GENERATION ---
        verb_audio_name = f"{safe_verb_name}.mp3"
        verb_audio_path = os.path.join(sound_dir, verb_audio_name)
        if not os.path.exists(verb_audio_path):
            gTTS(text=verb, lang='en').save(verb_audio_path)

        collocs_audio_name = f"{safe_verb_name}_collocations.mp3"
        collocs_audio_path = os.path.join(sound_dir, collocs_audio_name)
        has_collocs_audio = False
        if collocs and collocs != '—':
            if not os.path.exists(collocs_audio_path):
                gTTS(text=collocs.replace(';', ', '), lang='en').save(collocs_audio_path)
            has_collocs_audio = True

        phrasal_audio_name = f"{safe_verb_name}_phrasal.mp3"
        phrasal_audio_path = os.path.join(sound_dir, phrasal_audio_name)
        has_phrasal_audio = False
        if phrasal and phrasal != '—':
            if not os.path.exists(phrasal_audio_path):
                gTTS(text=phrasal.replace(';', ', '), lang='en').save(phrasal_audio_path)
            has_phrasal_audio = True

        example_audio_name = f"{safe_verb_name}_example.mp3"
        example_audio_path = os.path.join(sound_dir, example_audio_name)
        has_example_audio = False
        if example and example != '—':
            if not os.path.exists(example_audio_path):
                gTTS(text=example, lang='en').save(example_audio_path)
            has_example_audio = True

        # --- HTML LAYOUT (STYLIZED & ADAPTIVE) ---

        # Лицевая сторона упакована в белый блок с фиксированным темным текстом
        front = (
            f"<div style='{card_style}'>"
            f"<div style='font-size: 32px; font-weight: bold; color: #2c3e50;'>{verb}</div>"
            f"</div>[sound:{verb_audio_name}]"
        )

        # Оборотная сторона
        back_elements = [
            f"<div style='font-size: 22px; font-weight: bold; color: #e74c3c; margin-bottom: 6px;'>{v2} / {v3}</div>",
            f"<div style='font-size: 17px; color: #34495e; margin-bottom: 16px;'><b>{translation}</b></div>"
        ]

        if collocs and collocs != '—':
            collocs_html = "<br>".join([f"• {c.strip()}" for c in collocs.split(';')])
            audio_tag = f" [sound:{collocs_audio_name}]" if has_collocs_audio else ""
            back_elements.append(
                f"<div style='font-size: 13px; text-align: left; background-color: #f8f9fa; padding: 10px; "
                f"border-left: 4px solid #3498db; margin-bottom: 10px; border-radius: 4px; color: #2c3e50;'>"
                f"<b style='color: #2c3e50;'>Collocations:</b>{audio_tag}<br>{collocs_html}</div>"
            )

        if phrasal and phrasal != '—':
            phrasal_formatted = ", ".join([p.strip() for p in phrasal.split(';')])
            audio_tag = f" [sound:{phrasal_audio_name}]" if has_phrasal_audio else ""
            back_elements.append(
                f"<div style='font-size: 13px; text-align: left; color: #8e44ad; margin-bottom: 10px; "
                f"background-color: #fbf5fc; padding: 8px; border-radius: 4px; border-left: 4px solid #9b59b6;'>"
                f"<b style='color: #8e44ad;'>Phrasal Verbs:</b> {phrasal_formatted}{audio_tag}</div>"
            )

        if example and example != '—':
            audio_tag = f" [sound:{example_audio_name}]" if has_example_audio else ""
            back_elements.append(
                f"<div style='font-size: 14px; font-style: italic; color: #555555; border-top: 1px dashed #bdc3c7; "
                f"padding-top: 8px; margin-top: 10px; text-align: left;'>"
                f"<b style='color: #2c3e50; font-style: normal;'>Example:</b> {example}{audio_tag}</div>"
            )

        back = f"<div style='{card_style}'>{''.join(back_elements)}</div>"
        cards.append([front, back])

        # Progress Bar
        percent = int((index / total_cards) * 100)
        bar = '█' * int(20 * index // total_cards) + '░' * (20 - int(20 * index // total_cards))
        sys.stdout.write(f"\rProgress: [{bar}] {percent}% ({index}/{total_cards}) -> Modernized: {verb:<15}")
        sys.stdout.flush()

    with open(output_filename, mode="a", encoding="utf-8", newline="") as out_file:
        writer = csv.writer(out_file, delimiter=";")
        writer.writerows(cards)

    print(f"\n\n[+] Success! Modernized and added {total_cards} cards to '{output_filename}'")

    # --- AUTO-OPENING DIRECTORIES ---
    print("[+] Opening system folders...")
    os.startfile(os.path.abspath(sound_dir))

    local_pkg_path = os.path.join(os.path.expanduser("~"), "AppData", "Local", "Packages")
    anki_found = False
    if os.path.exists(local_pkg_path):
        for folder in os.listdir(local_pkg_path):
            if "Anki" in folder or "anki" in folder.lower():
                target_media = os.path.join(local_pkg_path, folder, "LocalState", "Anki2", "User 1", "collection.media")
                if os.path.exists(target_media):
                    os.startfile(target_media)
                    anki_found = True
                    break
    if not anki_found:
        roaming_media = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "Anki2", "User 1",
                                     "collection.media")
        if os.path.exists(roaming_media):
            os.startfile(roaming_media)


if __name__ == "__main__":
    create_flashcards_from_clipboard_no_header()

