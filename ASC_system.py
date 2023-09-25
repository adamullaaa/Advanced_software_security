import tkinter as tk
import mysql.connector
from tkinter import messagebox
from mysql.connector import cursor
from tkinter import filedialog
import bcrypt
import shutil
import os
import subprocess



conn= mysql.connector.connect(host='localhost', password ="Adamulla@2001", user= "root", database= "asc_system")
if conn.is_connected():
    print("connection established")

global username_entry, password_entry
def register():
    global username_entry, password_entry
    register_window = tk.Toplevel(root)
    register_window.title("Register New Account")
    register_window.geometry("300x300")
    tk.Label(register_window, text="Username").grid(row=0, pady=(10, 5))
    username_entry = tk.Entry(register_window)
    username_entry.grid(row=0, column=1)

    tk.Label(register_window, text="Password").grid(row=1, pady=(10, 5))
    password_entry = tk.Entry(register_window, show="#")
    password_entry.grid(row=1, column=1)


    r_button = tk.Button(register_window, text="Create an Account", command=create_account)
    r_button.grid(row=2, column=1)


    #return username_entry, password_entry


def create_account():
    cursor = conn.cursor()
    username = username_entry.get()
    password = password_entry.get()

    print(username)
    print(password)

    if not username or not password:
        tk.messagebox.showwarning("Warning", "Both fields are required!")
        return 0

        # Hash the password before storing
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    sql = "INSERT INTO user_accounts (username, password) VALUES (%s, %s)"
    val = (username, hashed_password.decode('utf-8'))  # decode hashed_password to store as VARCHAR in the database
    cursor.execute(sql, val)

    conn.commit()  # Commit changes to the database

    cursor.close()
    conn.close()

    # Inform the user and close the registration window
    tk.messagebox.showinfo("Info", "Account created successfully!")



def open_file_upload_window():

    upload_root = tk.Toplevel()
    upload_root.title("Upload PDF")

    def upload_file():
        # Ask the user to select a PDF file
        file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])

        if file_path:
            # Get the file name from the file path
            filename = os.path.basename(file_path)

            # Decorate the filename with the current username
            username_decorated_filename = f"{current_username}_{filename}"

            # Define the destination directory
            destination_directory = "D:/ASC Assignment/Stored_files"

            # Copy the file to the destination directory
            shutil.copy(file_path, os.path.join(destination_directory, username_decorated_filename))

            # Scan the copied file
            is_safe, message = scan_file(destination_directory, username_decorated_filename)

            if is_safe:
                print("The file is safe.")
                messagebox.showinfo("Success", f"File {file_path} uploaded successfully!")
            else:
                print(f"The file is potentially harmful. {message}")
                # Optionally, you could remove the harmful file from your directory here
                os.remove(os.path.join(destination_directory, username_decorated_filename))

    upload_button = tk.Button(upload_root, text="Upload PDF", command=upload_file)
    upload_button.pack(pady=50)
    root.geometry("400x300")
    upload_root.mainloop()


current_username = None

def check_credentials():
    global current_username  # Declare the variable as global in the function

    cursor = conn.cursor()
    username = username_entry.get()
    entered_password = password_entry.get()

    cursor.execute("SELECT password FROM user_accounts WHERE username=%s", (username,))
    result = cursor.fetchone()

    if result:
        stored_password = result[0]
        if bcrypt.checkpw(entered_password.encode(), stored_password.encode()):
            current_username = username  # Set the global variable
            open_file_upload_window()
        else:
            tk.messagebox.showwarning("Warning", "Incorrect password!")
    else:
        tk.messagebox.showwarning("Warning", "Username not found!")
    cursor.close()


def scan_file(destination_directory, username_decorated_filename):
    full_path = os.path.join(destination_directory, username_decorated_filename)

    try:
        result = subprocess.run(['C:\\Program Files\\ClamAV\\clamscan.exe', full_path], capture_output=True, text=True)

        if "FOUND" in result.stdout:
            return False, result.stdout
        else:
            return True, result.stdout
    except Exception as e:
        return False, str(e)




# Create the main window
root = tk.Tk()
root.title("Login Interface")

root.geometry("400x500")
# Create a label and entry for the username
username_label = tk.Label(root, text="Username:")
username_label.pack(pady=20)

username_entry = tk.Entry(root, width=30)
username_entry.pack(pady=10)

# Create a label and entry for the password
password_label = tk.Label(root, text="Password:")
password_label.pack(pady=20)

password_entry = tk.Entry(root, width=30, show="*")
password_entry.pack(pady=10)

# Create a login button
login_button = tk.Button(root, text="Login", command=check_credentials)
login_button.pack(pady=20)

register_button = tk.Button(root, text="Create a New Account", command=register)
register_button.pack(pady=20)

# Run the app
root.mainloop()
