import os
import threading
import tkinter as tk
from tkinter import DISABLED, NORMAL, RAISED, IntVar, Label, Menu, Menubutton, Radiobutton, StringVar, ttk
from tkinter import filedialog as fd
from translation import translate_video
from reprocess import reprocess_video

from_language="es-ES"

# create the root window
root = tk.Tk()
root.title('IAC TRANSLATOR')
root.geometry('175x500')
folder_path=StringVar()
translation_status=StringVar()
video_path=[]
gender = StringVar(root, "male")

def switch(btn):
    if btn.state == NORMAL:
        btn.state = DISABLED
    else:
        btn.state = NORMAL

def browse_button():
    # Allow user to select a directory and store it in global var
    # called folder_path
    global folder_path
    filename = fd.askdirectory()
    folder_path.set(filename)
    #print(filename)

def translation_thread():
    threading.Thread(target=translation_loop).start()

def translation_loop():
    global video_path
    global from_language
    global gender
    global folder_path
    global video_name
    try:
        to_languages=[]
        for i in range(len(variables)):
            if variables[i].get()==1:
                to_languages.append(languages[i][:2].lower())
        for i in video_path:
            video_name=os.path.basename(os.path.normpath(i))
            trs = translate_video(i,video_name,folder_path.get(),from_language,to_languages,gender.get())
            trs.translation_continuous()
            del trs
        translation_status.set("Done!")
        open_button["state"]= NORMAL
        select_path["state"]= NORMAL
        translation_button["state"]= NORMAL
        mb["state"]= NORMAL
    except Exception as e:
        print(e)
        translation_status.set("Error. Try Again...")
        open_button["state"]= NORMAL
        select_path["state"]= NORMAL
        translation_button["state"]= NORMAL
        mb["state"]= NORMAL

def translate_button():
    # Allow user to select a directory and store it in global var
    # called folder_path
    global folder_path
    global video_path
    global translation_status
    translation_status.set("Translation Started....")
    open_button["state"]= DISABLED
    select_path["state"]= DISABLED
    translation_button["state"]= DISABLED
    mb["state"]= DISABLED
    translation_thread()

def select_file():
    global video_path
    filetypes = (
        ("Videos", ".mp4"),
        ("Videos", ".flv"),
        ("Videos", ".avi"),
    )
    filename = fd.askopenfilenames(
        title='Select Videos',
        initialdir='/',
        filetypes=filetypes)
    video_path=(list(filename))
    #print(filename)
    video_text=[]
    for i in list(filename):
        video_text.append(os.path.basename(os.path.normpath(i)))
    lbl1.config(text=video_text)

# open button
open_button = ttk.Button(
    root,
    text='Select Videos',
    command=select_file
)

select_path = ttk.Button(
    root,
    text='Select Destination',
    command=browse_button
)


translation_button = ttk.Button(
    root,
    text='Start Translation',
    command=translate_button
)

mb=  Menubutton ( root, text="Languages", relief=RAISED )
mb.grid()
mb.menu =  Menu ( mb, tearoff = 0 )
mb["menu"] =  mb.menu

english = IntVar()
italian = IntVar()
french = IntVar()
languages=["English","Italian","French"]
variables=[english,italian,french]

for i in range(len(languages)):
    mb.menu.add_checkbutton ( label=languages[i], variable=variables[i])

lbl5 = Label(master=root,text="Translate",font='Helvetica 14 bold')
lbl5.place(x=30,y=25,width=115,height=25)

lbl1 = Label(master=root,text=video_path)
lbl1.place(x=145,y=60,height=25)
open_button.place(x=30,y=60,width=115,height=25)

select_path.place(x=30,y=95,width=115,height=25)
lbl2 = Label(master=root,textvariable=folder_path)
lbl2.place(x=145,y=95,height=25)

Radiobutton(root, text = "Male", variable = gender,
        value = "male").place(x=15,y=130,width=70,height=25)
Radiobutton(root, text = "Female", variable = gender,
        value = "female").place(x=85,y=130,width=70,height=25)

mb.place(x=30,y=165,width=115,height=25)

translation_button.place(x=30,y=200,width=115,height=25)

lbl3 = Label(master=root,textvariable=translation_status)
lbl3.place(x=30,y=235,width=115,height=25)


separator = ttk.Separator(root, orient='horizontal')
separator.place(x=20,y=270,width=135)

lbl4 = Label(master=root,text="Reprocess",font='Helvetica 14 bold')
lbl4.place(x=30,y=285,width=115,height=25)

folder_path2=StringVar()
reprocess_status2=StringVar()
gender2 = StringVar(root, "male")

def browse_button2():
    # Allow user to select a directory and store it in global var
    # called folder_path
    global folder_path2
    filename = fd.askdirectory()
    folder_path2.set(filename)

def reprocess_thread2():
    threading.Thread(target=reprocess_loop2).start()

def reprocess_loop2():
    global from_language
    global gender2
    global folder_path2
    try:
        to_languages2=[]
        for i in range(len(variables2)):
            if variables2[i].get()==1:
                to_languages2.append(languages2[i][:2].lower())
        trs = reprocess_video(folder_path2.get(),from_language, gender2.get(),to_languages2)
        trs.reprocess()
        del trs
        reprocess_status2.set("Done!")
        select_path2["state"]= NORMAL
        reprocess_button2["state"]= NORMAL
    except Exception as e:
        print(e)
        reprocess_status2.set("Error. Try Again...")
        select_path2["state"]= NORMAL
        reprocess_button2["state"]= NORMAL

def reprocess_buttoncmd2():
    # Allow user to select a directory and store it in global var
    # called folder_path
    global folder_path2
    global video_path2
    global translation_status2
    reprocess_status2.set("Process Started....")
    select_path2["state"]= DISABLED
    reprocess_button2["state"]= DISABLED
    reprocess_thread2()

select_path2 = ttk.Button(
    root,
    text='Select Folder',
    command=browse_button2
)

reprocess_button2 = ttk.Button(
    root,
    text='Reprocess',
    command=reprocess_buttoncmd2
)

mb2=  Menubutton ( root, text="Languages", relief=RAISED )
mb2.grid()
mb2.menu =  Menu ( mb2, tearoff = 0 )
mb2["menu"] =  mb2.menu

english2 = IntVar()
italian2 = IntVar()
french2 = IntVar()
languages2=["English","Italian","French"]
variables2=[english2,italian2,french2]

for i in range(len(languages2)):
    mb2.menu.add_checkbutton ( label=languages2[i], variable=variables2[i])

select_path2.place(x=30,y=320,width=115,height=25)
lbl2_2 = Label(master=root,textvariable=folder_path2)
lbl2_2.place(x=145,y=320,height=25)

mb2.place(x=30,y=355,width=115,height=25)

Radiobutton(root, text = "Male", variable = gender2,
        value = "male").place(x=15,y=390,width=70,height=25)
Radiobutton(root, text = "Female", variable = gender2,
        value = "female").place(x=85,y=390,width=70,height=25)

reprocess_button2.place(x=30,y=425,width=115,height=25)

lbl3_2 = Label(master=root,textvariable=reprocess_status2,anchor="w")
lbl3_2.place(x=30,y=460,width=115,height=25)
# run the application


root.mainloop()