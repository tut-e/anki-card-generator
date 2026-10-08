# Table to Anki Flashcards Generator with Audio 🚀

A lightweight Python script designed for language learners. It automatically grabs tabular data (such as irregular verb sheets or vocabulary lists) directly from your clipboard (Excel, Google Sheets) and converts it into fully formatted, bilingual HTML flashcards for **Anki**, complete with automated Text-to-Speech (TTS) voiceovers.

## ✨ Features
- **Zero Configuration:** No need to manually export CSV files. Just copy (`Ctrl+C`) in Excel and hit Run!
- **No Headers Required:** Parses your raw data row-by-row flawlessly from any index selection.
- **Full Text-to-Speech Voiceover:** Generates individual `.mp3` files via Google TTS for main words, collocations, phrasal verbs, and examples.
- **Pre-styled HTML/CSS Cards:** Beautiful modern layout for both mobile and desktop Anki apps.
- **Visual Progress Bar:** Displays completion percentages and an animated loading bar in your execution console.

## 🛠️ Installation

You can install the required dependencies using one of the methods below:

### Method 1 (Easiest for Beginners)
Simply run the included `install.py` script by double-clicking it or hitting **Run** in your IDE. It will configure everything automatically.

### Method 2 (Via Terminal)
If you prefer using your system terminal or command line, run:
```bash
pip install pyperclip gTTS
```

## 🚀 How to Use

1. Open your vocabulary table (e.g., in Excel, Numbers, or Google Sheets).
2. Select your data rows (**without headers**) and copy them (`Ctrl + C` or `Cmd + C`).
3. Run the main script (`generator.py`).
4. Look for the newly generated `anki_audio_flashcards.csv` file and the `sound_cards` folder next to your script.

## 📥 Importing into Anki

1. Copy all `.mp3` files inside the `sound_cards` folder into your active Anki profile's `collection.media` folder.
   - *Windows shortcut:* Press `Win + R`, type `%APPDATA%\Anki2`, open your profile folder, and locate `collection.media`.
   - *Mac shortcut:* In Finder, press `Cmd + Shift + G`, paste `~/Library/Application Support/Anki2`, open your profile folder, and locate `collection.media`.
2. Open **Anki**, click **Import File** in the bottom center, and select your `anki_audio_flashcards.csv`.
3. Configure the following import settings:
   - **Delimiter:** Set to **Semicolon ( ; )**.
   - **Note Type:** Select **Basic** (or any custom 2-field card layout).
   - **Allow HTML in fields:** **[CHECK THIS BOX]** *(Crucial for styles and audio playback!)*
4. Click **Import** and start reviewing! 🎉
