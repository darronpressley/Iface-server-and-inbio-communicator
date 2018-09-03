from tkinter import *
import tkinter.messagebox as tkm
import sqlconns
import decimal
import sys
import gl

VERSION = "0.0.1"


def leftclick(event):
    if entry_1.get() == "":
        tkm.showinfo('User Alert!!','Server is empty...')
        return
    if entry_2.get() == "":
        tkm.showinfo('User Alert!!','SQL login is empty...')
        return
    if entry_3.get() == "":
        tkm.showinfo('User Alert!!','Password is empty...')
        return
    if entry_4.get() == "":
        tkm.tkinter.messagebox.showinfo('User Alert!!','Database is empty...')
        return
    gl.SERVER =   entry_1.get()
    gl.SQL_LOGIN =entry_2.get()
    gl.PASSWORD = entry_3.get()
    gl.DATABASE = entry_4.get()
    sqlConnect = sqlconns.testsql(gl.SERVER,gl.SQL_LOGIN,gl.PASSWORD,gl.DATABASE)

    if sqlConnect == 0:
        tkm.showinfo('User Information','Cannot connect to Sql database or login denied.')
        return
    if sqlConnect == 1:
        answer = tkm.askquestion('User Information','Database connection successful, do you want to save to connection file.')
        if answer == 'no': return
        if answer == 'yes':
            temp1 = sqlconns.writesql_connection(gl.SERVER,gl.SQL_LOGIN,gl.PASSWORD,gl.DATABASE)
            if temp1 == 1:
                tkm.showinfo('User Information','Sql Connection file successfully changed.')
                root.destroy()
            if temp1 == 0: tkm.showinfo('User Alert!!!','Error Creating SQL Connection.')
            
    
root = Tk()

root.title(VERSION + " SQL server connector")
root.iconbitmap("python_small.ico")
root.geometry("300x300")
root.minsize(width=300, height=300)
root.maxsize(width=300, height=300)

photo = PhotoImage(file=gl.logo_path)
w=Label(root, image=photo)
w.photo = photo
w.grid(row=0, column=1)

label_title = Label(root, text=" Enter Details for SQL Server")
label_1 = Label(root, text="Server")
label_2 = Label(root, text="SQL login")
label_3 = Label(root, text="Password")
label_4 = Label(root, text="Database")

entry_1 = Entry(root)
entry_1.focus_set()
entry_2 = Entry(root)
entry_3 = Entry(root,show='*')
entry_4 = Entry(root)

button_1 = Button(root,text = "Test Connection",underline = 0)
button_1.bind("<ButtonRelease-1>", leftclick)
root.bind("<Return>", leftclick)
root.bind('<Alt-t>', leftclick)


label_title.grid(row = 1,column = 1,sticky = W+E)
label_1.grid(row = 5,sticky = E)
label_2.grid(row = 7,sticky = E)
label_3.grid(row = 9,sticky = E)
label_4.grid(row = 11,sticky = E)

entry_1.grid(row = 5,column = 1,sticky = W+E)
entry_2.grid(row = 7,column = 1,sticky = W+E)
entry_3.grid(row = 9,column = 1,sticky = W+E)
entry_4.grid(row = 11,column =1,sticky = W+E)

button_1.grid(row = 13,column = 1)


root.mainloop()


