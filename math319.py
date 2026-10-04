import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
from Crypto.Cipher import AES
import json
import os
import hashlib
import io

# =========================  USER DATABASE  =========================

USERS_FILE = "users.json"

def hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    try:
        with open(USERS_FILE, "r") as file:
            return json.load(file)
    except Exception:
        return {}

def save_users(users):
    with open(USERS_FILE, "w") as file:
        json.dump(users, file)


# =========================  AES HELPERS  =========================

def derive_key(password):
    """Derive 256-bit AES key from password using SHA-256."""
    return hashlib.sha256(password.encode("utf-8")).digest()


# =========================  AES ENCRYPTION  =========================

def encrypt_file_aes(input_path, output_path, password):
    key = derive_key(password)
    cipher = AES.new(key, AES.MODE_GCM)

    with open(input_path, "rb") as f:
        plaintext = f.read()

    ciphertext, tag = cipher.encrypt_and_digest(plaintext)

    with open(output_path, "wb") as f:
        f.write(cipher.nonce)
        f.write(tag)
        f.write(ciphertext)


# =========================  AES DECRYPTION  =========================

def decrypt_file_to_bytes(input_path, password):
    key = derive_key(password)

    with open(input_path, "rb") as f:
        nonce = f.read(16)
        tag = f.read(16)
        ciphertext = f.read()

    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    plaintext = cipher.decrypt_and_verify(ciphertext, tag)

    return plaintext


# =========================  THEME  =========================

def apply_theme(widget):
    style = ttk.Style()
    style.theme_use("clam")
    widget.configure(bg="#EADDD3")

    style.configure("Earth.TFrame", background="#C4B6AB", relief="flat")
    style.configure(
        "Earth.TLabel",
        background="#C4B6AB",
        foreground="#2D1E17",
        font=("Segoe UI", 12, "bold"),
    )
    style.configure(
        "Earth.TEntry",
        fieldbackground="white",
        foreground="#2D1E17",
        padding=7,
        borderwidth=2,
        relief="solid",
    )
    style.configure(
        "Earth.TButton",
        background="#796254",
        foreground="white",
        padding=8,
        font=("Segoe UI", 11, "bold"),
        relief="flat",
    )
    style.map("Earth.TButton", background=[("active", "#523F31")])


# =========================  UPLOAD IMAGE  =========================

def upload_image(win, image_path_var, image_label):
    path = filedialog.askopenfilename(
        filetypes=[
            ("All Supported", "*.jpg *.jpeg *.png *.bmp *.gif *.bin"),
            ("Encrypted Files", "*.bin"),
            ("Image Files", "*.jpg *.jpeg *.png *.bmp *.gif"),
        ]
    )

    if not path:
        return None

    image_path_var.set(path)

    if path.endswith(".bin"):
        image_label.configure(
            image="",
            text="Encrypted file loaded\nPress Decrypt Photo",
            font=("Segoe UI", 12, "bold"),
            bg="#EADDD3",
        )
        image_label.image = None
        return path

    try:
        img = Image.open(path)
        img.thumbnail((220, 160))
        photo = ImageTk.PhotoImage(img)
        image_label.configure(image=photo, text="", bg="#EADDD3")
        image_label.image = photo
    except:
        messagebox.showerror("Error", "Cannot display this file.")

    return path


# =========================  MAIN APP AFTER LOGIN  =========================

def main_app(username, password):
    win = tk.Toplevel()
    win.title("Secure Photo Gallery - Home")
    win.geometry("600x500")
    apply_theme(win)

    frame = ttk.Frame(win, padding=25, style="Earth.TFrame")
    frame.place(relx=0.5, rely=0.4, anchor="center")

    ttk.Label(
        frame,
        text=f"Welcome, {username}",
        style="Earth.TLabel",
        font=("Segoe UI", 16, "bold"),
    ).pack(pady=10)

    ttk.Label(
        frame,
        text="Secure Photo Gallery",
        style="Earth.TLabel",
        font=("Segoe UI", 14),
    ).pack(pady=10)

    image_path_var = tk.StringVar()
    image_label = tk.Label(win, bg="#EADDD3", text="")
    image_label.place(relx=0.5, rely=0.78, anchor="center")

    # =========================  ENCRYPTION BUTTON  =========================

    def encrypt_photo_action():
        path = image_path_var.get()
        if not path:
            messagebox.showerror("Error", "Please upload a photo first")
            return

        if path.endswith(".bin"):
            messagebox.showerror("Error", "This file is already encrypted.")
            return

        base, ext = os.path.splitext(path)
        encrypted_path = base + "_encrypted.bin"

        try:
            encrypt_file_aes(path, encrypted_path, password)
            messagebox.showinfo(
                "Success",
                f"Photo encrypted and saved as:\n{encrypted_path}",
            )
        except Exception as e:
            messagebox.showerror("Error", f"Encryption failed:\n{e}")

    # =========================  DECRYPTION BUTTON  =========================

    def decrypt_photo_action():
        path = image_path_var.get()
        if not path:
            messagebox.showerror("Error", "Please upload a photo first")
            return

        if path.endswith(".bin"):
            encrypted_path = path
            base_no_ext = os.path.splitext(path)[0].replace("_encrypted", "")
            decrypted_path = base_no_ext + "_decrypted.png"
        else:
            base, ext = os.path.splitext(path)
            encrypted_path = base + "_encrypted.bin"
            decrypted_path = base + "_decrypted" + ext

        if not os.path.exists(encrypted_path):
            messagebox.showerror("Error", "Encrypted file not found.")
            return

        try:
            plaintext = decrypt_file_to_bytes(encrypted_path, password)
        except Exception as e:
            messagebox.showerror("Error", f"Decryption failed:\n{e}")
            return

        try:
            with open(decrypted_path, "wb") as f:
                f.write(plaintext)
        except:
            messagebox.showerror("Error", "Could not save decrypted file.")
            return

        try:
            img = Image.open(io.BytesIO(plaintext))
            img.thumbnail((220, 160))
            photo = ImageTk.PhotoImage(img)
            image_label.configure(image=photo, text="", bg="#EADDD3")
            image_label.image = photo

            messagebox.showinfo("Success", f"Photo decrypted:\n{decrypted_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Cannot preview image:\n{e}")

    # =========================  BUTTONS UI  =========================

    ttk.Button(
        frame,
        text="Upload Photo / Encrypted File",
        style="Earth.TButton",
        width=30,
        command=lambda: upload_image(win, image_path_var, image_label),
    ).pack(pady=5)

    ttk.Entry(
        frame,
        textvariable=image_path_var,
        width=40,
        state="readonly",
        style="Earth.TEntry",
    ).pack(pady=5)

    ttk.Button(
        frame,
        text="Encrypt Photo",
        style="Earth.TButton",
        width=30,
        command=encrypt_photo_action,
    ).pack(pady=5)

    ttk.Button(
        frame,
        text="Decrypt Photo",
        style="Earth.TButton",
        width=30,
        command=decrypt_photo_action,
    ).pack(pady=5)

    ttk.Button(
        frame,
        text="Exit",
        style="Earth.TButton",
        width=30,
        command=win.destroy,
    ).pack(pady=10)


# =========================  SIGNUP SCREEN  =========================

def signup_screen(login_window):
    login_window.withdraw()

    sign = tk.Toplevel()
    sign.title("Create Account")
    sign.geometry("400x330")
    apply_theme(sign)

    frame = ttk.Frame(sign, padding=20, style="Earth.TFrame")
    frame.place(relx=0.5, rely=0.5, anchor="center")

    ttk.Label(frame, text="New Username", style="Earth.TLabel").pack(pady=5)
    username_entry = ttk.Entry(frame, style="Earth.TEntry")
    username_entry.pack()

    ttk.Label(frame, text="Password", style="Earth.TLabel").pack(pady=5)
    password_entry = ttk.Entry(frame, show="*", style="Earth.TEntry")
    password_entry.pack()

    ttk.Label(frame, text="Confirm Password", style="Earth.TLabel").pack(pady=5)
    confirm_entry = ttk.Entry(frame, show="*", style="Earth.TEntry")
    confirm_entry.pack()

    def confirm_signup():
        username = username_entry.get().strip()
        password = password_entry.get().strip()
        confirm = confirm_entry.get().strip()

        if not username or not password or not confirm:
            messagebox.showerror("Error", "Please fill in all fields")
            return

        if password != confirm:
            messagebox.showerror("Error", "Passwords do not match")
            return

        users = load_users()
        if username in users:
            messagebox.showerror("Error", "Username already exists")
            return

        users[username] = hash_password(password)
        save_users(users)

        messagebox.showinfo("Success", "Account created successfully")
        sign.destroy()
        login_window.deiconify()

    ttk.Button(
        frame,
        text="Create Account",
        style="Earth.TButton",
        width=30,
        command=confirm_signup,
    ).pack(pady=15)

    ttk.Button(
        frame,
        text="Cancel",
        style="Earth.TButton",
        width=30,
        command=lambda: (sign.destroy(), login_window.deiconify()),
    ).pack()


# =========================  LOGIN SCREEN  =========================

def login_screen():
    login = tk.Tk()
    login.title("Login")
    login.geometry("400x300")
    apply_theme(login)

    frame = ttk.Frame(login, padding=25, style="Earth.TFrame")
    frame.place(relx=0.5, rely=0.5, anchor="center")

    ttk.Label(frame, text="Username", style="Earth.TLabel").pack(pady=5)
    username_entry = ttk.Entry(frame, style="Earth.TEntry")
    username_entry.pack()

    ttk.Label(frame, text="Password", style="Earth.TLabel").pack(pady=5)
    password_entry = ttk.Entry(frame, show="*", style="Earth.TEntry")
    password_entry.pack()

    def login_action():
        username = username_entry.get().strip()
        password = password_entry.get().strip()

        if not username or not password:
            messagebox.showerror("Error", "Please enter username and password")
            return

        users = load_users()

        if username not in users:
            messagebox.showerror("Error", "User not found")
            return

        if users[username] != hash_password(password):
            messagebox.showerror("Error", "Incorrect password")
            return

        messagebox.showinfo("Success", "Login successful")
        login.withdraw()
        main_app(username, password)

    ttk.Button(
        frame,
        text="Login",
        style="Earth.TButton",
        width=30,
        command=login_action,
    ).pack(pady=15)

    ttk.Button(
        frame,
        text="Create New Account",
        style="Earth.TButton",
        width=30,
        command=lambda: signup_screen(login),
    ).pack()

    login.mainloop()


# =========================  START APP  =========================

if __name__ == "__main__":
    login_screen()
