import tkinter as tk
from tkinter import * 
from tkinter import filedialog, messagebox
from warnings import showwarning
import numpy as np
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from pydub import AudioSegment





# Fungsi untuk menyimpan file audio ke dalam bentuk array numpy
def load_audio(file_path):
    return np.fromfile(file_path, dtype=np.int16)


# Fungsi untuk menyimpan array numpy ke dalam bentuk file audio
def save_audio(file_path, audio_data):
    audio_data.astype(np.int16).tofile(file_path)


# Fungsi untuk menyembunyikan data rahasia ke dalam audio cover menggunakan algoritma F5
def F5(audio_cover, bitstream_rahasia, ukuran_blok):
    # Inisialisasi variabel
    audio_stego = audio_cover.copy()
    indeks_rahasia = 0
    indeks_blok = 0

    while indeks_rahasia < len(bitstream_rahasia):
        # Ambil blok saat ini
        blok = audio_stego[indeks_blok:indeks_blok + ukuran_blok]

        # Hitung perbedaan antara nilai rata-rata dari sampel di blok tersebut dengan setiap sampel
        perbedaan = [abs(x - np.mean(blok)) for x in blok]

        # Cari sampel dengan perbedaan median
        indeks_median = np.argsort(perbedaan)[len(perbedaan) // 2]

        # Tanamkan bit rahasia berikutnya
        if bitstream_rahasia[indeks_rahasia] == 1:
            audio_stego[indeks_blok + indeks_median] += 1
        else:
            audio_stego[indeks_blok + indeks_median] -= 1

        # Increment counters
        indeks_rahasia += 1
        indeks_blok = (indeks_blok + ukuran_blok) % len(audio_stego)

    return audio_stego


# Fungsi untuk mengenkripsi data rahasia menggunakan algoritma AES
def AES_encrypt(data_rahasia, kunci):
    cipher = AES.new(kunci, AES.MODE_CBC)
    iv = cipher.iv
    data_rahasia = pad(data_rahasia.encode(), AES.block_size)
    encrypted = cipher.encrypt(data_rahasia)
    return iv + encrypted





# Fungsi untuk mendekripsi data rahasia menggunakan algoritma AES
def AES_decrypt(encrypted, kunci):
    iv = encrypted[:AES.block_size]
    cipher = AES.new(kunci, AES.MODE_CBC, iv)
    decrypted = cipher.decrypt(encrypted[AES.block_size:])
    return unpad(decrypted, AES.block_size).decode()


# Fungsi untuk menyembunyikan file teks pada file audio
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
        save_audio(audio_stego_file_path, audio_stego)
        messagebox.showinfo("Success", "Teks berhasil disisipkan dalam audio!")


window = tk.Tk()

def show_gui(filename):
    if filename == "":
        window.destroy()
    else:
        window.title('Show Secret Message')
        window.geometry("440x300")

        def showing_secret_message(secret_message):
            msgbox = messagebox.showinfo("Pesan Rahasia", "Pesan rahasia berhasil diperoleh:\n\n" + secret_message)
            if msgbox == "ok":
               window.destroy()


        def general_validate(filename, input_key):
            if len(filename) == 0:
                msgbox = messagebox.showerror("Error", "Mohon isi semua data yang diperlukan.")
            elif len(input_key) == 0:
                msgbox = messagebox.showerror("Error", "Mohon isi semua data yang diperlukan.")
            else:
                showing_secret_message(showwarning(filename, str(input_key)))

        label_file_explorer = Label(window, text="Directory: " + filename)
        audio = AudioSegment.from_file(filename)
        duration = len(audio) / 1000
        label_audio_duration = Label(window, text="Audio duration: " + str(duration) + " seconds")
        input_key_text = Text(window, height=1, width=50)
        button_show = Button(window, text="Show", font=("Helvetica", 16), width=20, height=2,
                             command=lambda: general_validate(filename, input_key_text.get("1.0", 'end-1c')))

        label_title = Label(window, text="Show Secret Message", font=("Helvetica", 20))
        label_title.grid(row=1, column=1, pady=16)
        label_file_explorer.grid(row=2, column=1, padx=15)
        label_audio_duration.grid(row=3, column=1)
        label_title_key = Label(window, text="Key")
        label_title_key.grid(row=4, column=1, padx=15, pady=(10, 0), sticky='w')
        input_key_text.grid(row=5, column=1, padx=15, sticky='w')
        button_show.grid(row=6, column=1, padx=15, pady=(15, 0))

def hide_gui():
    button_hide_gui = Button(window, text="Hide Secret Message", font=("Plus Jakarta", 16),
                            command=lambda: hide_file(), width=20, height=3)
    button_hide_gui.pack(pady=8)

def browse_file(hide=True):
    if hide:
        filename = filedialog.askopenfilename(initialdir="D:\stegano F5",
                                              title="Select an Input Audio",
                                              filetypes=[("Audio file", ".wav .mp3")])
    else:
        filename = filedialog.askopenfilename(initialdir="D:\stegano F5",
                                              title="Select a Steganography Audio",
                                              filetypes=[("Audio file", ".wav")])
    return filename

def hide_file():
    return browse_file(hide=True)

def show_file():
    return browse_file(hide=False)



def gui():
    window.title('Audio Steganography')
    window.geometry("300x300")

    label_title = Label(window, text="Audio Steganography", font=("Comic Sans MS", 18, "bold"))
    label_title.pack(pady=16)

    button_hide_gui = Button(window, text="Hide Secret Message", font=("Helvetica", 16),
                            command=lambda: [hide_gui()], width=20, height=3)
    button_hide_gui.pack(pady=8)

    button_show_gui = Button(window, text="Show Secret Message", font=("Helvetica", 16),
                            command=lambda: [show_gui()], width=20, height=3)
    button_show_gui.pack(pady=8)

    window.mainloop()

if __name__ == "__main__":
    gui()
# def browse_file(hide=True):
#     #Show open input video file window
#     if hide:
#         filename = filedialog.askopenfilename(initialdir = "C:/Users/Komandan3/Skripsion",
#                                           title = "Select an Input Video",
#                                           filetypes=[("Video file", ".avi .mp4")])

#     #Show open steganography video file window
#     else:
#         filename = filedialog.askopenfilename(initialdir = "C:/Users/Komandan3/Skripsion",
#                                           title = "Select a Steganography Video",
#                                           filetypes=[("Video file", ".avi")])
#     return filename


# def show_gui(filename, input_key):
#     # Initialize window
#     window = tk.Tk()
#     if filename == "":
#         window.destroy()
#     else:
#         window.title('Show Secret Message') 
#         window.geometry("440x300")

#         # Pop up if message successfully obtained
#         def showing_secret_message(secret_message):
#             msgbox = messagebox.showinfo("Secret Message",  "Secret message that have been successfully obtained:\n\n"+secret_message)
#             if msgbox == "ok":
#                 window.destroy()

#         # Field validation
#         def general_validate(filename, input_key):
#             if len (filename) == 0:
#                 msgbox = messagebox.showerror("Error",  "Please input all required data.")
#             elif len (input_key) == 0:
#                 msgbox = messagebox.showerror("Error",  "Please input all required data.")
#             else:
#                 showing_secret_message(show(filename, str(input_key)))

#         # Initialize widget
#         label_file_explorer = Label(window, text="Directory: "+filename)
#         audio = AudioSegment.from_file(filename)
#         duration = audio.duration_seconds
#         label_audio_duration = Label(window, text="Audio duration: "+str(duration)+" seconds")
#         input_key = Text(window, height = 1, width = 50)
#         button_show = Button(window, text = "Show", font=("Helvetica", 16), width=20, height=2,
#                               command =lambda: general_validate(filename, input_key.get("1.0",'end-1c')))

#         # Show widget
#         label_title = Label(window, text = "Show Secret Message", font=("Helvetica", 20)).grid(row=1, column=1, pady=16)
#         label_file_explorer.grid(row=2, column=1, padx=15)
#         label_audio_duration.grid(row=3, column=1)
#         label_title_key = Label(window, text = "Key").grid(row=4, column=1, padx=15, pady=(10,0), sticky='w')
#         input_key.grid(row=5, column=1, padx=15, sticky='w')
#         button_show.grid(row=6, column=1, padx=15, pady=(15,0))

#         window.mainloop()


# def hide_gui():
#     # Hide secret message button
#     button_hide_gui = Button(window, text="Hide Secret Message", font=("Plus Jakarta", 16), command=lambda: hide_file(hide=True), width=20, height=3)
#     button_hide_gui.pack(pady=8)


# def hide_file():
#     #If function called in hide secret message button
#     return browse_file()

# def show_file():
#     #If function called in show secret message button
#     return browse_file(hide=True)


# def gui():
#     #Initialize window
#     window = Tk()
#     window.title('Audio Steganography')
#     window.geometry("300x300")
    
#     label_title = Label(window, text = "Audio Steganography", font=("Comic Sans MS", 18, "bold")).pack(pady=16)

#     #Hide secret message button
#     button_hide_gui = Button(window, text = "Hide Secret Message", font=("Helvetica", 16), command = lambda: [hide_gui(hide_file())], width=20, height=3).pack(pady=8)

#     #Show secret message button
#     button_show_gui = Button(window, text = "Show Secret Message", font=("Helvetica", 16), command = lambda: [show_gui(show_file())], width=20, height=3).pack(pady=8)
    
#     window.mainloop()

# #Main function
# if __name__ == "__main__":
#     gui()
