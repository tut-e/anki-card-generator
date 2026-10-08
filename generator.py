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
    # Метод проверяет, какие глаголы уже есть в CSV-файле, чтобы не дублировать их
    existing_verbs = set()
    if os.path.exists(filepath):
        try:
            with open(filepath, mode="r", encoding="utf-8") as f:
                reader = csv.reader(f, delimiter=";")
                for row in reader:
                    if row:
                        # Извлекаем чистый глагол из HTML-верстки лицевой стороны
                        raw_front = row[0]
                        if "font-size" in raw_front:
                            verb = raw_front.split(";'>")[1].split("</div>")[0]
                            existing_verbs.add(verb.strip().lower())
        except Exception:
            pass  # Если файл поврежден или пуст, просто возвращаем пустой сет
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

    # Загружаем список уже существующих в файле глаголов
    existing_verbs = get_existing_verbs(output_filename)

    f = io.StringIO(data_str.strip())
    reader = csv.reader(f, delimiter="\t")

    rows = []
    for row in reader:
        if not row or len(row) < 7:
            continue
        if "verb" in row[0].lower() or "перевод" in row[4].lower():
            continue

        verb_to_check = row[1].strip()
        # ЗАЩИТА: Если такой глагол уже есть в файле, полностью пропускаем его
        if verb_to_check.lower() in existing_verbs:
            continue

        rows.append(row)

    total_cards = len(rows)

    if total_cards == 0:
        print("[~] No new verbs found. All copied verbs are already in your CSV file!")
        return

    cards = []
    print(f"[+] New rows to process: {total_cards}\n")

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

        # --- HTML LAYOUT ---
        front = f"<div style='font-size: 28px; font-weight: bold; color: #2c3e50; text-align: center;'>{verb}</div>[sound:{verb_audio_name}]"

        back_elements = [
            f"<div style='font-size: 20px; font-weight: bold; color: #e74c3c; text-align: center; margin-bottom: 8px;'>{v2} / {v3}</div>",
            f"<div style='font-size: 16px; color: #34495e; margin-bottom: 12px; text-align: center;'><b>{translation}</b></div>"
        ]

        if collocs and collocs != '—':
            collocs_html = "<br>".join([f"• {c.strip()}" for c in collocs.split(';')])
            audio_tag = f" [sound:{collocs_audio_name}]" if has_collocs_audio else ""
            back_elements.append(
                f"<div style='font-size: 13px; text-align: left; background: #f8f9fa; padding: 8px; border-left: 4px solid #3498db; margin-bottom: 8px;'><b>Коллокации:</b>{audio_tag}<br>{collocs_html}</div>")

        if phrasal and phrasal != '—':
            phrasal_formatted = ", ".join([p.strip() for p in phrasal.split(';')])
            audio_tag = f" [sound:{phrasal_audio_name}]" if has_phrasal_audio else ""
            back_elements.append(
                f"<div style='font-size: 13px; color: #8e44ad; margin-bottom: 8px;'><b>Фразовые глаголы:</b> {phrasal_formatted}{audio_tag}</div>")

        if example and example != '—':
            audio_tag = f" [sound:{example_audio_name}]" if has_example_audio else ""
            back_elements.append(
                f"<div style='font-size: 14px; font-style: italic; color: #7f8c8d; border-top: 1px dashed #bdc3c7; padding-top: 6px;'><b>Пример:</b> {example}{audio_tag}</div>")

        back = f"<div style='font-family: Arial, sans-serif; max-width: 400px; margin: 0 auto;'>{''.join(back_elements)}</div>"
        cards.append([front, back])

        # Progress Bar
        percent = int((index / total_cards) * 100)
        bar = '█' * int(20 * index // total_cards) + '░' * (20 - int(20 * index // total_cards))
        sys.stdout.write(f"\rProgress: [{bar}] {percent}% ({index}/{total_cards}) -> Generated: {verb:<15}")
        sys.stdout.flush()

    # РЕЖИМ "a" (Append) — теперь строки дописываются в конец файла, не стирая старые
    with open(output_filename, mode="a", encoding="utf-8", newline="") as out_file:
        writer = csv.writer(out_file, delimiter=";")
        writer.writerows(cards)

    print(f"\n\n[+] Success! Added {total_cards} new cards to '{output_filename}'")

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
            anki_found = True


if __name__ == "__main__":
    create_flashcards_from_clipboard_no_header()

