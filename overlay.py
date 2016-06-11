from tkinter import *
import threading

class Overlay(threading.Thread):
    def __init__(self, width, height, xpos, ypos):
        threading.Thread.__init__(self)
        self.width = width
        self.height = height
        self.xpos = xpos
        self.ypos = ypos
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
        self.root.focusmodel('passive')
        self.text = Text(self.root, bg='black', fg='white', state='disabled')
        self.text.pack()
        self.root.mainloop()

    def update(self, user, msg):
        numlines = int(float(self.text.index('end - 1 line')))
        self.text['state'] = 'normal'
        if self.text.index('end-1c') != '1.0':
            self.text.insert('end', '\n')
        self.text.insert('end', "{0}: {1}".format(user, msg))
        self.text.see('end')
        self.text['state'] = 'disabled'


if __name__ == '__main__':
    o = Overlay()
