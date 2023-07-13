import tkinter as tk
from tkinter import filedialog, messagebox
from Crypto.Cipher import AES
import numpy as np
import ffmpeg
from tkinter import *
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes


# Fungsi untuk mengenkripsi data rahasia menggunakan algoritma AES
def aes_encrypt(data_rahasia, kunci):
    cipher = AES.new(kunci, AES.MODE_CBC)
    data_rahasia_padded = np.pad(
        data_rahasia, (0, AES.block_size - len(data_rahasia) % AES.block_size)
    )
    data_rahasia_encrypted = cipher.encrypt(data_rahasia_padded)
    iv = cipher.iv
    return iv + data_rahasia_encrypted


# # Fungsi untuk mendekripsi data rahasia menggunakan algoritma AES
def AES_decrypt(encrypted, kunci):
    iv = encrypted[: AES.block_size]
    cipher = AES.new(kunci, AES.MODE_CBC, iv)
    decrypted = cipher.decrypt(encrypted[AES.block_size :])
    return np.trim_zeros(decrypted, "b").decode()


def f5_encode(audio_file_path: str, message: str, block_size: int) -> bytes:
    # Menyandikan pesan ke dalam file audio
    audio_input = ffmpeg.input(audio_file_path)
    audio_output = ffmpeg.output(audio_input, "pipe:", format="wav")
    audio = audio_output.run(capture_stdout=True, capture_stderr=True)

    # Mengonversi byte audio menjadi array numpy
    audio_data = np.frombuffer(audio[0], np.int16)

    # Melakukan loop pada setiap karakter pesan dan memodifikasi data audio
    for i in range(len(message)):
        # Mendapatkan blok audio saat ini
        start = i * block_size
        end = (i + 1) * block_size
        block_audio = audio_data[start:end]

        # Menyematkan karakter pesan saat ini ke dalam blok data audio
        message_char = message[i]
        block_audio = np.bitwise_and(block_audio, 0xFFFE)
        block_audio = np.bitwise_or(block_audio, int(message_char))

        # Memperbarui data audio dengan blok data audio yang telah dimodifikasi
        audio_data_new = audio_data.copy()
        audio_data_new [start:end] = block_audio

    # Mengonversi data audio yang telah dimodifikasi kembali ke byte dan mengembalikannya
    return audio_data.tobytes()


def get_audio_file():
    return filedialog.askopenfilename(filetypes=[("WAV files", "*.wav")])


def get_text_file():
    return filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])


def read_plaintext_from_file(file_path):
    with open(file_path, "r") as f:
        return f.read()


def encrypt_plaintext(plaintext: str, key: bytes) -> bytes:
    cipher = AES.new(key, AES.MODE_ECB)
    plaintext_terpadding = pad(plaintext.encode(), AES.block_size)
    teks_terenkripsi = cipher.encrypt(plaintext_terpadding)
    return teks_terenkripsi

def hide_text_in_audio(
    audio_file: bytes, text_to_hide: str, block_size: int = 512) -> bytes:
    key = b"super_secret_key"
    encrypted_text = encrypt_plaintext(text_to_hide, key)
    text_length = str(len(encrypted_text))
    steganographed_audio_data = F5(audio_file, text_length, block_size)
    return F5(steganographed_audio_data, encrypted_text, block_size)


def save_audio_stego(audio_stego):
    audio_stego_file = filedialog.asksaveasfilename(filetypes=[("WAV files", "*.wav")])
    if audio_stego_file:
        with open(audio_stego_file, "wb") as f:
            f.write(audio_stego)
        messagebox.showinfo("Success", "Teks berhasil disisipkan dalam audio!")


def hide_text_in_audio():
    audio_file = get_audio_file()
    if not audio_file:
        return
    text_file = get_text_file()
    if not text_file:
        return

    # Baca teks dari file
    plaintext = read_plaintext_from_file(text_file)

    # Enkripsi teks
    key = b"super_secret_key"
    encrypted_text = encrypt_plaintext(plaintext, key)

    # Sisipkan teks terenkripsi ke dalam audio
    steganographed_audio_data = f5_encode(audio_file, encrypted_text, block_size=512)

    # Simpan audio hasil penyisipan
    save_audio_stego(steganographed_audio_data)


def show_gui(filename, input_key):
    root = tk.Tk()
    root.title("Audio Steganography")
    root.geometry("300x300")
    label_title = Label(
        root, text="Audio Steganography", font=("Comic Sans MS", 18, "bold")
    )
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
            blok_audio = audio_data[i * 512 : (i + 1) * 512]
            bit_terakhir =  str (blok_audio[-1] & 1)
            panjang_teks += bit_terakhir

        panjang_teks = int(panjang_teks, 2)

        # Ekstrak teks terenkripsi
        teks_terenkripsi = ""
        for i in range(32, 32 + panjang_teks * 8):
            blok_audio = audio_data[i * 512 : (i + 1) * 512]
            bit_terakhir =  blok_audio[-1] & 1
            teks_terenkripsi += bit_terakhir

        # Dekripsi teks terenkripsi
        kunci = input_key.get().encode()
        cipher = AES.new(kunci, AES.MODE_ECB)
        decrypted = cipher.decrypt(
            bytes(
                int(teks_terenkripsi[i : i + 8], 2)
                for i in range(0, len(teks_terenkripsi), 8)
            )
        )

        # Tampilkan teks terdekripsi
        messagebox.showinfo("Teks Terdekripsi", decrypted.decode())

    hide_button = tk.Button(root, text="Sisipkan Teks", command=button_hide)
    hide_button.pack(padx=10, pady=10, fill="x")

    show_button = tk.Button(root, text="Ekstrak Teks", command=button_show)
    show_button.pack(padx=10, pady=10, fill="x")

    root.mainloop()


# Run the GUI
input_key = tk.StringVar
show_gui("filename", "input_key")
