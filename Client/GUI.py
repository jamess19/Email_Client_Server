import tkinter as tk
from tkinter import messagebox
from test import check_login

def on_button_click(input_user, input_pass):
    # Kiểm tra tên người dùng và mật khẩu ở đây, và thực hiện đăng nhập thành công
    successful_login = check_login(input_user.get(), input_pass.get())

    if successful_login:
        messagebox.showinfo("Thông báo", "Đăng nhập thành công!")
        switch_to_work_area()
    else:
        messagebox.showinfo("Thông báo", "Sai tên đăng nhập hoặc mật khẩu!")


def switch_to_work_area():
    win2 = tk.Tk()
    win2.title('EMAIL WINDOW')
    win2.geometry('500x500')
    win2['bg'] = '#FFF8DC'

    but1 = tk.Button(win2, text="Send Mail")
    but1.place(x=200, y=100, width=100, height=30)

    but2 = tk.Button(win2, text="Mail List")
    but2.place(x=200, y=200, width=100, height=30)

    win2.mainloop()

def main():
    win = tk.Tk()
    win.title('EMAIL WINDOW')
    win.geometry('500x500')
    win['bg'] = '#FFF8DC'

    name = tk.Label(win, text="EMAIL", font=('Arial', 15, 'bold'), bg='#006666', fg='#FEB692', bd=1.3, relief="solid")
    name.place(x=150, y=30, width=200, height=30)

    user = tk.Label(win, text="User", font=('Times New Roman', 12, 'bold'), bg='#006666', fg='#99FFFF', anchor='center', bd=1.2, relief="solid")
    user.place(x=20, y=100, width=100, height=20)

    input_user = tk.Entry(win, width=30, bd=1.2, relief="solid")
    input_user.place(x=140, y=100, width=320, height=20)

    password = tk.Label(win, text="Password", font=('Times New Roman', 12, 'bold'), bg='#006666', fg='#99FFFF', anchor='center', bd=1.2, relief='solid')
    password.place(x=20, y=140, width=100, height=20)

    input_pass = tk.Entry(win, width=30, bd=1.2, relief="solid", show="*")
    input_pass.place(x=140, y=140, width=320, height=20)

    but1 = tk.Button(win, text="Login", command=lambda: on_button_click(input_user, input_pass))
    but1.place(x=200, y=200, width=100, height=30)

    win.mainloop()

if __name__ == "__main__":
    main()
