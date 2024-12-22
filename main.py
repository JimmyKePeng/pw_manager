from tkinter import *
from tkinter import messagebox
import pw_manager
import sqlite3
def main():
    def setup_db(): # set up the data base.
        conn = sqlite3.connect('passwords.db')
        # Connects to a database file named 'passwords.db' or creates it if it doesn't exist.
        c = conn.cursor()
        # Creates a table named 'accounts'.
        c.execute('''CREATE TABLE IF NOT EXISTS accounts (
                        ID TEXT PRIMARY KEY,
                        PW TEXT)''')
        conn.commit()  # Saves changes.
        conn.close()   

    def log_in(event=None): #long in to existing account if id and pw correct
        entered_id = id_entry.get()
        entered_pw = password_entry.get()

        pw = is_account_exist(entered_id)

        if pw: # if data exist
            decrypted_pw = pw_manager.decrypt_pw(pw[0]) # pw is a tuple, so i need [0] to access the first string
            if entered_pw == decrypted_pw:
                window.destroy()
                pw_manager.main(entered_id, logout_callback=main) # pass the main function for callback
            else:
                messagebox.showerror("Error", "Incorrect password. Please try again.")
        else:
            messagebox.showinfo(title="Oops", message=f"No details for {entered_id} found.")

    def is_account_exist(id): # check if account exist and return pw tuple
        conn = sqlite3.connect('passwords.db')
        c = conn.cursor()
        c.execute(f"SELECT PW FROM accounts WHERE ID = ?", (id,))
        pw = c.fetchone() # Retrieves the information as tuple
        conn.close()  # Closes connection.
        return pw

    def create_account(): # create new account
        entered_id = id_entry.get()
        entered_pw = password_entry.get()
        is_valid, msg = pw_manager.is_pw_strong(entered_pw) 
        if is_valid:
            encrypted_pw = pw_manager.encrypt_pw(entered_pw)
            pw = is_account_exist(entered_id)
            if pw: # if data exist already
                messagebox.showinfo(title="Oops", message=f"account ID: {entered_id} already exist.")
            else:
                conn = sqlite3.connect('passwords.db')
                c = conn.cursor() # create cursor object to interact with the database
                c.execute(f"INSERT INTO accounts (ID, PW) VALUES (?, ?)", (entered_id, encrypted_pw))
                conn.commit()  # Saves (commits) the changes.
                messagebox.showinfo(title="Created", message=f"account ID: {entered_id} created")
                window.destroy()
                pw_manager.main(entered_id, logout_callback=main) # go back to long in screen when logout button pressed
        else:
            messagebox.showinfo(title="Weak Password", message=msg)
        
    setup_db()
# ---------------------------- GUI SETUP ------------------------------- #
    window = Tk()
    window.title("Log in for PW manager")
    window.config(padx=40, pady=40)
    window.bind("<Return>", log_in)

    # Entry and Button
    Label(text="log in / create account").grid(row=1, column=0, columnspan=2)
    Label(text="ID: ").grid(row=2, column=0)
    id_entry = Entry(width=30)
    id_entry.grid(row=2, column=1)
    Button(text="Log in", width=11, command=log_in).grid(row=2, column=2)

    Label(text="PW: ").grid(row=3, column=0)
    password_entry = Entry(show="*", width=30)
    password_entry.grid(row=3, column=1)
    Button(text="Create account", command=create_account).grid(row=3, column=2)

    window.mainloop()
main()