from tkinter import *
from tkinter import messagebox
from random import randint, choice, shuffle
import sqlite3

global USER
# --------------------------------ENCRYPT PASSWORD ------------------------------------#
encrypt_dict = {'X': 'W', 'H': 'J', 'e': '!', 'g': '9', 'R': '^', 'J': 'G', '7': 'S', '&': 'I', 'y': 'e', '6': 'u', 
               '?': '8', '2': 'L', 'h': 'O', 'r': 'q', 'K': 'H', ')': '&', 'Q': 'x', '~': 'V', '3': 'g', 'm': 'y',
               '$': 'D', 'T': 'N', 'C': 'E', 'd': '@', 'Z': '5', 'L': 'w', '1': '1', 'x': '3', '*': '`', 'k': 'r',
               '_': 'a', 'S': 'k', 'I': 'Z', 'B': 't', 'E': 'h', 't': '-', 'c': 's', 'z': 'T', '9': '=', '^': 'v',
               's': 'm', '#': 'j', 'V': 'U', '(': '7', '!': 'A', '%': 'z', 'G': 'i', 'O': 'C', 'N': 'd', '`': 'n',
               'q': '6', '4': 'o', 'U': 'Y', '+': 'K', '-': 'R', '5': 'b', 'n': '_', 'w': 'M', 'v': '(', 'o': 'X',
               'u': ')', 'b': 'B', 'A': '#', 'M': '?', '=': 'l', '0': '2', '@': 'c', 'a': 'F', 'j': '~', 'P': '0',
               'D': '4', 'Y': '$', 'f': 'Q', 'l': '*', '8': 'f', 'i': 'p', 'p': 'P', 'W': '%', 'F': '+'}

decrypt_dict = {value: key for (key, value) in encrypt_dict.items()} # switch the key and value from encrypt_dict

def decrypt_pw(code): # get(letter, letter) if letter in decrypt_dict, get the vale else use the original letter
    pw = [decrypt_dict.get(letter, letter) for letter in code] 
    return "".join(pw)

def encrypt_pw(pw):
    code = [encrypt_dict.get(letter, letter) for letter in pw]
    return "".join(code)

def setup_db():# Set up the database for user
    global USER
    conn = sqlite3.connect('passwords.db')
    c = conn.cursor()
    c.execute(f'''CREATE TABLE IF NOT EXISTS {USER}_passwords (
                    website TEXT PRIMARY KEY,
                    username TEXT,
                    password TEXT)''')
    conn.commit() 
    conn.close()  

def is_pw_strong(password): # check if pw is strong, return T or F and a message
    if len(password) < 8:
        return False, "Password should be at least 8 characters long."

    has_upper = False
    has_lower = False
    has_digit = False
    has_special = False
    special_characters = "!#$%&()*@^-_+=~`?"

    for char in password:
        if char.isupper():
            has_upper = True
        elif char.islower():
            has_lower = True
        elif char.isdigit():
            has_digit = True
        elif char in special_characters:
            has_special = True

    if not has_upper:
        return False, "Password should have at least one uppercase letter."
    if not has_lower:
        return False, "Password should have at least one lowercase letter."
    if not has_digit:
        return False, "Password should have at least one digit."
    if not has_special:
        return False, "Password should have at least one special character."

    return True, "Password is strong."

def generate_pw():
    lower_case = list('abcdefghijklmnopqrstuvwxyz') # turn the string into list
    upper_case = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    numbers = list('0123456789')
    symbols = list('!#$%&()*@^-_+=~`?')

    password_list = ([choice(lower_case) for _ in range(randint(4, 6))] + # Generate random pw 
                    [choice(upper_case) for _ in range(randint(4, 6))] + # using list comprehension
                    [choice(symbols) for _ in range(randint(2, 4))] + 
                    [choice(numbers) for _ in range(randint(2, 4))])
    shuffle(password_list)
    password = "".join(password_list) # it was a list. now join the list and make it a string.

    password_entry.delete(0, END)
    password_entry.insert(0, password)

def add_pw(): # Save pw
    global USER
    website_input = website_entry.get().title()
    username_input = username_entry.get()
    password_input = password_entry.get()
    encrypted_pw = encrypt_pw(password_entry.get())

    if website_input and username_input and password_input:
        is_valid, msg = is_pw_strong(password_input) 
        if is_valid:
            conn = sqlite3.connect('passwords.db')
            c = conn.cursor() # create cursor object to interact with the database
            try:
                # Inserts the website, username, and encrypted password into the user table.
                c.execute(f"INSERT INTO {USER}_passwords (website, username, password) VALUES (?, ?, ?)",
                        (website_input, username_input, encrypted_pw))
                conn.commit()
                messagebox.showinfo(title="Success", message="Password saved successfully!")
            except sqlite3.IntegrityError: # if they website already exist, update it
                c.execute(f"UPDATE {USER}_passwords set password = ?, username = ? where website = ?",
                        (encrypted_pw, username_input, website_input))
                conn.commit() 
                messagebox.showinfo(title="Updated", message="Password updated sucessfully!")
            finally:
                conn.close()

            clear_entries()
        else:
            messagebox.showinfo(title="Weak Password", message=msg)
    else:
        messagebox.showinfo(title="Oops", message="Please make sure you haven't left any fields empty.")

def search(event=None): # search for a pw
    # Searches for the username and encrypted password.
    website_name = website_entry.get().title()
    conn = sqlite3.connect('passwords.db')
    c = conn.cursor()
    c.execute(f"SELECT username, password FROM {USER}_passwords WHERE website = ?", (website_name,))
    result = c.fetchone() # Retrieves the information as tuple
    conn.close()  # Closes connection.

    if result: # if data exist
        username, encrypted_pw = result  #  result is a tuple
        decrypted_pw = decrypt_pw(encrypted_pw)  # decrypted the password before displaying it.
        username_entry.delete(0, "end")
        username_entry.insert(0, username)
        password_entry.delete(0, "end")
        password_entry.insert(0, decrypted_pw)
        # messagebox.showinfo(title=f"{website_name}", message=f"Email: {username} \nPassword: {decrypted_pw}")
    else:
        messagebox.showinfo(title="Oops", message=f"No details for {website_name} found.")
        clear_entries()
    # website_entry.delete(0,"end")

def clear_entries():
        website_entry.delete(0, "end")  # clear the entry
        password_entry.delete(0, "end")
        username_entry.delete(0, "end")

# ----------------------------MAIN GUI SETUP ------------------------------- #
def main(id, logout_callback=None):

    def logout():# close pw manager and go back to main
        window.destroy() 
        if logout_callback:
            logout_callback()

    global USER 
    USER = id
    setup_db()
    window = Tk()
    window.title("Password Manager")
    window.config(padx=50, pady=50)
    window.bind("<Return>", search)

    canvas = Canvas(width=197, height=245, highlightthickness=0)
    logo_image = PhotoImage(file="lock.png")
    canvas.create_image(98, 122, image=logo_image)
    canvas.grid(row=0, column=1)

    # Labels
    Label(text="Website name:").grid(row=1, column=0)
    Label(text="Email/Username:").grid(row=2, column=0)
    Label(text="Password:").grid(row=3, column=0)

    # Entries
    global website_entry, username_entry, password_entry
    website_entry = Entry(width=33)
    website_entry.grid(row=1, column=1)
    website_entry.focus()
    username_entry = Entry(width=51)
    username_entry.grid(row=2, column=1, columnspan=2)
    # username_entry.insert(0, "example@gmail.com")
    password_entry = Entry(width=33)
    password_entry.grid(row=3, column=1)

    # Buttons
    Button(text="Search", width=14, command=search).grid(row=1, column=2)
    Button(text="Generate Password", command=generate_pw).grid(row=3, column=2)
    Button(text="Add/Update", width=43, command=add_pw).grid(row=4, column=1, columnspan=2)
    Button(text="Clear", width=43, command=clear_entries).grid(row=5, column=1, columnspan=2)
    Button(text="Log out",width=14, command=logout).grid(row=6, column=2, columnspan=2)
    window.mainloop()

