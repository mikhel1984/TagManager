# S.Mikhel, 2016-2020
"""Main window of file manager"""

from tkinter import Frame, Menubutton, Menu, Image
import tkinter.messagebox as msg

from .filelist import FileList, PREVIOUS_DIR
from .fileoperation import FileOperation
from .searchwindow import SearchWindow

ABOUT = \
"TagManager - double panel manager with file tags\n\n\
   2016-2020 S.Mikhel - mikhel.sk@gmail.com"

KEYS = \
"Manager: \n\
Lelt, Right - change directory\n\
= - make panels equal\n\
[ - tag edit\n\
Ctrl+Right - word complete\n\
/ - open search window\n\
\nSearch window: \n\
Ctrl+S - search \n\
Ctrl+R - reset\n\
Ctrl+O - open directory with file\n\
? word - find files with this word"


class TagManager:
   "Double panel manager window"

   def __init__(self, root):
      self.root = root
      self.fo = FileOperation()
      # widgets
      self.panel = (FileList(self, self.fo, 0),
                    FileList(self, self.fo, 1))
      self.bar = Frame(self.root)
      self.bar.grid(row=0, column=0, sticky='we')
      self.menuFile()
      self.menuTag()
      self.menuHelp()
      self.panel[0].grid(row=1, column=0, sticky='ns')
      self.panel[1].grid(row=1, column=1, sticky='ns')
      # bind events
      self.root.bind('<F5>', self.copy)
      self.root.bind('<F6>', self.move)
      self.root.bind('<F1>', lambda x: msg.showinfo("Keys", KEYS))
      self.root.bind('<F9>', lambda x: self.fo.execute(self.fo.getRandomFile()))
      self.root.bind('/', self.openSearch)    
      self.root.bind('<Control-q>', lambda x: self.root.destroy())
      self.root.bind('=',self.makeEqual)
      # icon, title
      img = Image("photo", file="./manager/img/tm.gif")
      self.root.call('wm', 'iconphoto', self.root._w, img)
      self.root.title('TagManager')
      # evaluate
      self.root.mainloop()

   def copy(self, ev):
      "Copy file (directory)"
      # get path
      src, dst = self.src, 1-self.src
      src_path = self.panel[src].getFocus()
      if src_path.endswith(PREVIOUS_DIR): return
      dst_path = self.panel[dst].getPath()
      # copy
      if self.fo.copy(src_path, dst_path):
         self.panel[dst].refresh()

   def move(self, ev):
      "Move file (directory)"
      # get path
      src, dst = self.src, 1-self.src
      src_path = self.panel[src].getFocus()
      if src_path.endswith(PREVIOUS_DIR): return
      dst_path = self.panel[dst].getPath()
      # move
      if self.fo.move(src_path, dst_path):
         self.panel[src].refresh()
         self.panel[dst].refresh()

   def makeEqual(self, ev):
      "Make filelist in dst equal to src"
      src, dst = self.src, 1-self.src
      self.panel[dst].writeFiles(self.panel[src].getPath())

   def menuTag(self):
      "Set menu for working with tags"
      fbutton = Menubutton(self.bar, text='Tags', underline=0)
      fbutton.grid(row=0, column=1, sticky='w')
      menu = Menu(fbutton, tearoff = 0)
      menu.add_command(label='Search... (/)', command=lambda: self.openSearch(1))
      menu.add_command(label='Edit ([)', command=lambda: self.panel[self.src].tagEdit(1))
      menu.add_command(label="Don't save (Esc)", command=lambda: self.panel[self.src].tagExit(1))
      menu.add_command(label='Correct DB', command=lambda: self.fo.correctDb())
      fbutton.configure(menu=menu)

   def menuFile(self):
      "Set menu for file commands"
      cbutton = Menubutton(self.bar, text='Files', underline=0)
      cbutton.grid(row=0, column=0, sticky='w')
      menu = Menu(cbutton, tearoff=0)
      menu.add_command(label='Rename (F2)', command=lambda: self.panel[self.src].rename(1))
      menu.add_command(label='Copy (F5)', command=lambda: self.copy(1))
      menu.add_command(label='Move (F6)', command=lambda: self.move(1))
      menu.add_command(label='New folder (F7)', command=lambda: self.panel[self.src].newDir(1))
      menu.add_command(label='Equal panels (=)', command=lambda: self.makeEqual(1))
      menu.add_separator({})
      menu.add_command(label='Quit (Ctrl+Q)', command=lambda: self.root.destroy())
      cbutton.configure(menu=menu)

   def menuHelp(self):
      "Set menu with help information"
      hbutton = Menubutton(self.bar, text='Help', underline=0)
      hbutton.grid(row=0, column=2, sticky='w')
      menu = Menu(hbutton, tearoff=0)
      menu.add_command(label='Keys (F1)', command=lambda: msg.showinfo("Keys", KEYS))
      menu.add_command(label='About', command=lambda: msg.showinfo("About", ABOUT))
      hbutton.configure(menu=menu)

   def openSearch(self, ev):
      "Open window for file search"
      # open window
      search = SearchWindow(self.root, self.fo)
      open_path = search.run()
      # open directory if need
      if open_path: self.panel[self.src].writeFiles(open_path)


