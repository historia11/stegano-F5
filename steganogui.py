import tkinter as tk
from tkinter import filedialog, messagebox
from Crypto.Cipher import AES
import numpy as np
import ffmpeg
from tkinter import *



def AES_encrypt(plaintext, key):
    cipher = AES.new(key, AES.MODE_ECB)
    return cipher.encrypt(plaintext)

def F5(audio_file_path, pesan, ukuran_blok):
    audio = ffmpeg.input(audio_file_path)
    audio = ffmpeg.output(audio, 'pipe:', format='wav')
    audio = audio.run(capture_stdout=True, capture_stderr=True)

    audio_data = np.frombuffer(audio[0], np.int16)
    panjang_pesan = len(pesan)

    for i in range(panjang_pesan):
        blok_audio = audio_data[i * ukuran_blok: (i + 1) * ukuran_blok]
        audio_data[i * ukuran_blok: (i + 1) * ukuran_blok] = blok_audio & 0xFFFE | int(pesan[i])

    return audio_data.tobytes()

def hide_text_in_audio():
    # Buka file audio
    audio_file_path = filedialog.askopenfilename(filetypes=[("WAV files", "*.wav")])
    if not audio_file_path:
        return

    # Buka file teks
    text_file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    if not text_file_path:
        return

    # Baca teks dari file
    with open(text_file_path, 'r') as f:
        plaintext = f.read()

    # Enkripsi teks dengan AES
    kunci = b'super_secret_key'
    encrypted = AES_encrypt(plaintext, kunci)


    # Sisipkan panjang teks terenkripsi ke dalam audio cover
    audio_stego = F5(audio_file_path, str(len(encrypted)), ukuran_blok=512)

    # Sisipkan teks terenkripsi ke dalam audio cover
    audio_stego = F5(audio_stego, encrypted, ukuran_blok=512)

    # Simpan audio stego
    audio_stego_file_path = filedialog.asksaveasfilename(filetypes=[("WAV files", "*.wav")])
    if audio_stego_file_path:
        with open(audio_stego_file_path, 'wb') as f:
            f.write(audio_stego)
        messagebox.showinfo("Success", "Teks berhasil disisipkan dalam audio!")


def show_gui(filename, input_key):
    root = tk.Tk()
    root.title('Audio Steganography')
    root.geometry("300x300")


    label_title = Label(root, text="Audio Steganography", font=("Comic Sans MS", 18, "bold"))
    label_title.pack(pady=16)
    def button_hide():
        hide_text_in_audio()

    def button_show():
        # Buka file audio
        audio_file_path = filedialog.askopenfilename(filetypes=[("WAV files", "*.wav")])
        if not audio_file_path:
            return

        # Baca audio cover
        audio_data = np.fromfile(audio_file_path, np.int16)

        # Ekstrak panjang teks terenkripsi
        panjang_teks = ""
        for i in range(32):
            blok_audio = audio_data[i * 512: (i + 1) * 512]
            bit_terakhir = str(blok_audio[-1] & 1)
            panjang_teks += bit_terakhir

        panjang_teks = int(panjang_teks, 2)

        # Ekstrak teks terenkripsi
        teks_terenkripsi = ""
        for i in range(32, 32 + panjang_teks * 8):
            blok_audio = audio_data[i * 512: (i + 1) * 512]
            bit_terakhir = str(blok_audio[-1] & 1)
            teks_terenkripsi += bit_terakhir

        # Dekripsi teks terenkripsi
        kunci = input_key.get().encode()
        cipher = AES.new(kunci, AES.MODE_ECB)
        decrypted = cipher.decrypt(bytes(int(teks_terenkripsi[i:i + 8], 2) for i in range(0, len(teks_terenkripsi), 8)))

        # Tampilkan teks terdekripsi
        messagebox.showinfo("Teks Terdekripsi", decrypted.decode())

    hide_button = tk.Button(root, text="Sisipkan Teks", command=button_hide)
    hide_button.pack(padx=10,pady=10,fill="x")

    show_button = tk.Button(root, text="Ekstrak Teks", command=button_show)
    show_button.pack(padx=10,pady=10, fill="x")

    root.mainloop()

# Run the GUI
input_key = tk.StringVar 
show_gui('filename', 'input_key')
