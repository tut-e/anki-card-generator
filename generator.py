import csv
import io
import os
import sys
import pyperclip  # Читает текст из буфера обмена (Ctrl+C)
from gtts import gTTS


def create_flashcards_from_clipboard():
    # Забираем скопированный текст из буфера обмена
    data_str = pyperclip.paste()

    if not data_str.strip() or "Verb" not in data_str:
        print(
            "[-] Ошибка: Вы не скопировали таблицу. Откройте Excel, выделите строки (вместе с шапкой #, Verb...), нажмите Ctrl+C и снова нажмите Run.")
        return

    sound_dir = "sound_cards"
    if not os.path.exists(sound_dir):
        os.makedirs(sound_dir)

    # Сначала считываем все строки в память, чтобы узнать их точное количество для процентов
    f = io.StringIO(data_str.strip())
    reader = list(csv.DictReader(f, delimiter="\t"))

    # Фильтруем пустые строки или строки без глагола
    valid_rows = [row for row in reader if 'Verb' in row and row['Verb'] and row['Verb'].strip()]
    total_cards = len(valid_rows)

    if total_cards == 0:
        print("[-] Ошибка: В скопированных данных не найдено строк с глаголами.")
        return

    cards = []

    print(f"[+] Данные успешно подтянулись! Найдено строк для обработки: {total_cards}")
    print("[+] Начинаю генерацию. Пожалуйста, подождите...\n")

    for index, row in enumerate(valid_rows, start=1):
        verb = row['Verb'].strip()
        v2 = row.get('V2', '').strip()
        v3 = row.get('V3', '').strip()
        translation = row.get('Перевод / основные значения', '').strip()
        collocs = row.get('5 полезных collocations', '').strip()
        phrasal = row.get('Phrasal verbs', '').strip()
        example = row.get('Пример', '').strip()

        # --- ГЕНЕРАЦИЯ АУДИО ФАЙЛОВ ---

        # 1. Озвучка для основного глагола
        verb_audio_name = f"{verb}.mp3"
        verb_audio_path = os.path.join(sound_dir, verb_audio_name)
        if not os.path.exists(verb_audio_path):
            tts_verb = gTTS(text=verb, lang='en')
            tts_verb.save(verb_audio_path)

        # 2. Озвучка для коллокаций
        collocs_audio_name = f"{verb}_collocations.mp3"
        collocs_audio_path = os.path.join(sound_dir, collocs_audio_name)
        has_collocs_audio = False
        if collocs and collocs != '—':
            collocs_clean_text = collocs.replace(';', ', ')
            if not os.path.exists(collocs_audio_path):
                tts_collocs = gTTS(text=collocs_clean_text, lang='en')
                tts_collocs.save(collocs_audio_path)
            has_collocs_audio = True

        # 3. Озвучка для фразовых глаголов
        phrasal_audio_name = f"{verb}_phrasal.mp3"
        phrasal_audio_path = os.path.join(sound_dir, phrasal_audio_name)
        has_phrasal_audio = False
        if phrasal and phrasal != '—':
            phrasal_clean_text = phrasal.replace(';', ', ')
            if not os.path.exists(phrasal_audio_path):
                tts_phrasal = gTTS(text=phrasal_clean_text, lang='en')
                tts_phrasal.save(phrasal_audio_path)
            has_phrasal_audio = True

        # 4. Озвучка для примера
        example_audio_name = f"{verb}_example.mp3"
        example_audio_path = os.path.join(sound_dir, example_audio_name)
        has_example_audio = False
        if example and example != '—':
            if not os.path.exists(example_audio_path):
                tts_example = gTTS(text=example, lang='en')
                tts_example.save(example_audio_path)
            has_example_audio = True

        # --- HTML-ВЕРСТКА КАРТОЧКИ ---
        front = f"<div style='font-size: 28px; font-weight: bold; color: #2c3e50; text-align: center;'>{verb}</div>[sound:{verb_audio_name}]"

        back_elements = [
            f"<div style='font-size: 20px; font-weight: bold; color: #e74c3c; text-align: center; margin-bottom: 8px;'>{v2} / {v3}</div>",
            f"<div style='font-size: 16px; color: #34495e; margin-bottom: 12px; text-align: center;'><b>{translation}</b></div>"
        ]

        if collocs and collocs != '—':
            collocs_list = [f"• {c.strip()}" for c in collocs.split(';')]
            collocs_html = "<br>".join(collocs_list)
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

        # --- РАСЧЕТ И ОТРИСОВКА ПРОЦЕНТОВ ---
        percent = int((index / total_cards) * 100)
        bar_length = 20
        filled_length = int(bar_length * index // total_cards)
        bar = '█' * filled_length + '░' * (bar_length - filled_length)

        # \r возвращает курсор в начало строки вывода, обновляя её динамически
        sys.stdout.write(f"\rПрогресс: [{bar}] {percent}% ({index}/{total_cards}) -> Озвучен: {verb:<15}")
        sys.stdout.flush()

    output_filename = "anki_audio_flashcards.csv"
    with open(output_filename, mode="w", encoding="utf-8", newline="") as out_file:
        writer = csv.writer(out_file, delimiter=";")
        writer.writerows(cards)

    print(f"\n\n[+] Успешно! Файл '{output_filename}' обновлен.")
    print(f"[+] Все аудиофайлы лежат в папке '{sound_dir}'.")


if __name__ == "__main__":
    create_flashcards_from_clipboard()

