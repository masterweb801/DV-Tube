from tkinter import Label, Entry, Button, StringVar, Tk, GROOVE, PhotoImage, filedialog
from tkinter.ttk import Combobox
from pytube import YouTube
from ctypes import windll, wintypes, Structure, POINTER, c_wchar_p, byref, WinError
from uuid import UUID
from win10toast import ToastNotifier
from threading import Thread
from vid2aud import convert_video_to_audio
from tkinter.messagebox import showerror

my_appid = 'logic_realm.dvtube.1.2'
windll.shell32.SetCurrentProcessExplicitAppUserModelID(my_appid)


class GUID(Structure):
    _fields_ = [
        ("Data1", wintypes.DWORD),
        ("Data2", wintypes.WORD),
        ("Data3", wintypes.WORD),
        ("Data4", wintypes.BYTE * 8)
    ]

    def __init__(self, uuidstr):
        uuid = UUID(uuidstr)
        Structure.__init__(self)
        self.Data1, self.Data2, self.Data3, \
            self.Data4[0], self.Data4[1], rest = uuid.fields
        for i in range(2, 8):
            self.Data4[i] = rest >> (8-i-1)*8 & 0xff


SHGetKnownFolderPath = windll.shell32.SHGetKnownFolderPath
SHGetKnownFolderPath.argtypes = [
    POINTER(GUID), wintypes.DWORD,
    wintypes.HANDLE, POINTER(c_wchar_p)
]


def _get_known_folder_path(uuidstr):
    pathptr = c_wchar_p()
    guid = GUID(uuidstr)
    if SHGetKnownFolderPath(byref(guid), 0, 0, byref(pathptr)):
        raise WinError()
    return pathptr.value


FOLDERID_Download = '{374DE290-123F-4565-9164-39C4925E467B}'


def get_download_folder():
    return _get_known_folder_path(FOLDERID_Download)


def sndn(folder: str):
    toast = ToastNotifier()
    toast.show_toast(title="Downloading Successfull", msg="Video Downloaded And Saved In\n" + folder, icon_path="icon.ico", threaded=True)


def dsps():
    root.spl.destroy()
    root.st.destroy()
    root.st2.destroy()
    main()


def splash_screen():
    image = PhotoImage(file="icon-png.png")
    image = image.zoom(10)
    image = image.subsample(32)
    root.spl = Label(root, image=image, border=0)
    root.spl.pack(pady=20)
    root.spl.image = image
    root.st = Label(root, text="DV Tube", font="Helvetica 25 bold",
                    border=0, bg="black", fg="white")
    root.st.pack(pady=0)
    root.st2 = Label(root, text="By Logic Realm", font="Helvetica 12 italic", border=0, bg="black", fg="white")
    root.st2.pack(pady=0)
    root.after(2000, dsps)


def main():
    def dl(*args):
        if root.linkText.get() != "":
            root.Download_B["state"] = "disabled"
            t = Thread(target=Download)
            t.start()
        else:
            toast = ToastNotifier()
            toast.show_toast(title="Error", msg="URL Can't Be Empty!", icon_path="icon.ico", threaded=True)

    link_label = Label(root, text="YouTube link :", bg="salmon", fg="#fff", pady=5, padx=5)
    link_label.place(x=10, y=70)

    root.linkText = Entry(
        root, width=35, textvariable=video_Link, font="Arial 14")
    root.linkText.place(x=120, y=72)
    root.linkText.focus()

    destination_label = Label(
        root, text="Destination :", bg="salmon", fg="#fff", pady=5, padx=9)
    destination_label.place(x=10, y=120)

    root.destinationText = Entry(
        root, width=27, textvariable=download_Path, font="Arial 14")
    root.destinationText.place(x=120, y=120)

    browse_B = Button(root, text="Browse", command=Browse, width=10, bg="bisque", relief=GROOVE)
    browse_B.place(x=430, y=120)

    root.Download_B = Button(root, text="Download Video", command=dl, width=20, bg="green", fg="#fff", pady=10, padx=15, relief=GROOVE, font="Georgia, 13")
    root.Download_B.pack(side='bottom', pady=60)
    root.bind('<Return>', dl)


def Browse():
    download_Directory = filedialog.askdirectory(
        initialdir="YOUR DIRECTORY PATH", title="Save Video")
    download_Path.set(download_Directory)


def Download():
    def askres(l: list[str]):
        def ext(*args):
            root.resulation = res_sel.get()
            second.destroy()
        second = Tk()
        second.title("Select Video Resolution")
        second.geometry("300x200")
        second.iconbitmap("icon.ico")
        second.resizable(False, False)
        second.config(background="#000")

        res_label = Label(second, text="Available Video Resolutions:- ", bg="salmon", fg="#fff", pady=5, padx=9, font="Georgia, 13", relief=GROOVE)
        res_label.pack(pady=20)
        res_sel = Combobox(second, width=20, font="Arial 14")
        res_sel.pack(pady=20, padx=30)
        res_sel['values'] = tuple(l)
        res_sel.current(0)
        Download = Button(second, text="Download", width=20, bg="green", fg="#fff", pady=10, padx=15, relief=GROOVE, font="Georgia, 13", command=ext)
        Download.pack(pady=20, ipady=10)
        second.bind('<Return>', ext)
        second.mainloop()

    Youtube_link = video_Link.get()
    ressl = ["Select Resolution ...", 'Audio Mp3']
    video_Link.set('')
    download_Folder = download_Path.get()
    getVideo = YouTube(Youtube_link)
    try:
        resl = getVideo.streams.filter(progressive=True)
        for res in resl:
            r = str(res).split(' res="')
            for i in r:
                if i != "":
                    val = i.split('"')
                    if "p" in val[0]:
                        ressl.append(val[0])
        askres(ressl)
        if root.resulation != "Select Resolution ...":
            if root.resulation != "Audio Mp3":
                videoStream = getVideo.streams.filter(res=root.resulation).first()
                videoStream.download(download_Folder)
                root.Download_B["state"] = "normal"
                sndn(download_Folder)
            else:
                videoStream = getVideo.streams.first()
                if videoStream is not None:
                    videoStream.download(output_path=download_Folder)
                    convert_video_to_audio(download_Folder)
                else:
                    showerror("Error", "videoStream = "+str(videoStream))
                root.Download_B["state"] = "normal"
        else:
            root.Download_B["state"] = "normal"
    except Exception as e:
        # toast = ToastNotifier()
        root.Download_B["state"] = "normal"
        showerror("Error", e)
        # toast.show_toast(title="Error", msg="This Video Is Age Restricted!", icon_path="icon.ico", threaded=True)


root = Tk()
root.geometry("520x280")
root.resizable(False, False)
root.title("DVTube")
root.config(background="#000")
root.iconbitmap("icon.ico")

video_Link = StringVar()
download_Path = StringVar(value=get_download_folder())
root.resulation = StringVar()

splash_screen()

root.mainloop()
