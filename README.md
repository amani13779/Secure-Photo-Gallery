# Secure Photo Gallery

## Description

Secure Photo Gallery is a Python application that provides a secure way to upload, encrypt, and decrypt image files.

The application includes a login and account creation system. Users can create an account, log in, upload photos, encrypt them using AES encryption, and decrypt encrypted files when needed.

## Features

* Create a new user account
* Login authentication
* Password hashing using SHA-256
* Upload image files
* Upload encrypted files
* Encrypt photos using AES-GCM
* Decrypt encrypted photos
* Preview uploaded images
* Preview decrypted images
* Save encrypted files as `.bin`
* Save decrypted images as `.png` or their original image format

## Technologies Used

* Python
* Tkinter
* SQLite
* PyCryptodome
* Pillow (PIL)
* AES-GCM
* SHA-256
* JSON

## Security

Passwords are stored as SHA-256 hashes instead of plain text passwords.

The application derives a 256-bit AES key from the user's password using SHA-256 and uses AES-GCM to encrypt and decrypt photo files.

## How It Works

### 1. Create Account

The user enters:

* Username
* Password
* Confirm Password

The password is hashed before being stored in the `users.json` file.

### 2. Login

The user enters their username and password.

The application checks the stored username and compares the hashed password before allowing access to the main application.

### 3. Upload Photo

Users can upload supported image formats such as:

* JPG
* JPEG
* PNG
* BMP
* GIF

Encrypted `.bin` files can also be uploaded.

### 4. Encrypt Photo

After selecting a photo, the user can select **Encrypt Photo**.

The encrypted file is saved with the following format:

```text
_originalname_encrypted.bin
```

The encryption uses AES-GCM.

### 5. Decrypt Photo

The user can select an encrypted `.bin` file and choose **Decrypt Photo**.

The decrypted image is saved and displayed in the application.

## Required Libraries

Install the required libraries using:

```bash
pip install pillow pycryptodome
```

## How to Run

Run the Python file:

```bash
python math319.py
```

The application will open the Login screen.



## User Interface

The application contains:

* Login screen
* Create Account screen
* Secure Photo Gallery home screen
* Upload Photo / Encrypted File button
* Encrypt Photo button
* Decrypt Photo button
* Exit button


