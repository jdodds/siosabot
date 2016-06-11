from tkinter import *
import threading
import random
import win32api
import win32con
import pywintypes

class UserColor:
    def __init__(self):
        self.colors = [
            '#0000ff',
            '#ff7f50',
            '#1e90ff',
            '#00ff7f',
            '#9acd32',
            '#00ff00',
            '#ff4500',
            '#ff0000',
            '#daa520',
            '#ff69b4',
            '#5f9ea0',
            '#2e8b57',
            '#d2691e',
            '#8a2be2',
            '#b22222',
        ]
        self.user_colors = {}

    def color(self, user):
        if not user in self.user_colors:
            self.user_colors[user] = random.choice(self.colors)
        return self.user_colors[user]


class Overlay(threading.Thread):
    def __init__(self, width, height, xpos, ypos):
        threading.Thread.__init__(self)
        self.width = width
        self.height = height
        self.xpos = xpos
        self.ypos = ypos
        self.user_colors = UserColor()
        self.start()

    def die(self):
        self.root.quit()

    def run(self):
        self.root = Tk()
        self.root.geometry("%dx%d+%d+%d" % (self.width, self.height,
                                            self.xpos, self.ypos))
        self.root.protocol('WM_DELETE_WINDOW', self.die)
        self.root.resizable(width=False, height=False)
        self.root.overrideredirect(1)
        self.root.minsize(width=self.width, height=self.height)
        self.root.maxsize(width=self.width, height=self.height)
        self.root.attributes(
            '-alpha', 0.6,
            '-topmost', True,
            '-disabled', True,
        )

        self.text = Text(self.root, bg='black', fg='white', state='disabled')
        self.text.configure(font=('Helvetica', 10, 'bold'))
        self.text.pack()
        self.root.lift()
        hWindow = pywintypes.HANDLE(int(self.root.frame(), 16))
        exStyle = win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT | win32con.WS_EX_NOACTIVATE
        win32api.SetWindowLong(hWindow, win32con.GWL_EXSTYLE, exStyle)
        self.root.mainloop()

    def update(self, user, msg):
        numlines = int(float(self.text.index('end - 1 line')))
        self.text['state'] = 'normal'
        if self.text.index('end-1c') != '1.0':
            self.text.insert('end', '\n')
        self.text.insert('end', "{0}: {1}".format(user, msg))
        color = self.user_colors.color(user)
        self.text.tag_config(user, foreground=color, relief=RAISED)
        self.text.tag_add(user, 'end-1l', 'end-1l wordend')
        self.text.see('end')
        self.text['state'] = 'disabled'


if __name__ == '__main__':
    o = Overlay()
