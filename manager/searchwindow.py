"""Window for file search"""

from tkinter import Frame, Toplevel, Listbox, Button, Scrollbar
from tkinter import Entry, StringVar, Menu
import tkinter.simpledialog as dlg
import tkinter.messagebox as msg
import os

SHOW_TAGS, SHOW_FILES = 0, 1

class SearchWindow:
   def __init__(self, master, fileOp):
      self.slave = Toplevel(master)
      self.fo = fileOp
      self.state = SHOW_TAGS

      self.files = Frame(self.slave)
      self.file_lst = Listbox(self.files, selectmode='single', height=20, font='Verdanda 10')
      self.scroll = Scrollbar(self.files, command=self.file_lst.yview)
      self.file_lst.configure(yscrollcommand=self.scroll.set)
      self.files.pack(side='top', fill='x', expand=1)
      self.file_lst.pack(side='left', fill='both', expand=1)
      self.scroll.pack(side='right', fill='y')

      self.var = StringVar()
      self.tags_edt = Entry(self.slave, textvariable=self.var, fg='red', font='Verdanda 10')
      self.tags_edt.pack(fill='x', expand=1)

      self.btn_frame = Frame(self.slave)
      self.search_btn = Button(self.btn_frame, text='Search', width=14)
      self.reset_btn = Button(self.btn_frame, text='Reset', width=14)
      self.search_btn.pack(side='left')
      self.reset_btn.pack(side='right')
      self.btn_frame.pack()

      self.c_menu = Menu(self.slave, tearoff=0)
      self.c_menu.add_command(label='Add', command=lambda: self.exec(1))
      self.c_menu.add_command(label='Rename', command=self.tagRename)
      self.c_menu.add_command(label='Delete', command=self.tagDelete)

      self.reset_btn.bind('<Button-1>', self.reset)
      self.slave.bind('<Control-r>', self.reset)
      self.search_btn.bind('<Button-1>', self.printFiles)
      self.slave.bind('<Control-s>', self.printFiles)
      self.tags_edt.bind('<Return>', self.printFiles)
      self.tags_edt.bind('<Control-Right>', self.wordComplete)
      self.file_lst.bind('<ButtonRelease-1>', self.fileInfo)
      self.file_lst.bind('<Double-ButtonRelease-1>', self.exec)
      self.file_lst.bind('<Return>', self.exec)
      self.file_lst.bind('<ButtonRelease-3>', self.callMenu)
      self.slave.bind('<Escape>', lambda x: self.slave.destroy())
      self.slave.bind('<Control-o>', self.openPath)

      self.open_path = None

      self.last_tag = ""
      self.last_tag_lst = []
      self.last_tag_num = 0

      self.tags = self.fo.tagList()
      self.reset(1)

      self.slave.title(self.fo.baseInfo())

   def run(self):
      "Start execution for search window"
      self.slave.grab_set()
      self.slave.focus_set()
      self.slave.wait_window()
      return self.open_path

   def reset(self, ev):
      "Clear window, add list of tags"
      self.state = SHOW_TAGS
      self.files = []
      self.file_lst.delete(0, 'end')
      self.var.set("")
      self.file_lst['fg'] = 'red'
      for tag in self.tags:
         self.file_lst.insert('end', tag)
      self.file_lst.focus_set()

   def printFiles(self, ev):
      "Show result of search"
      self.state = SHOW_FILES
      tag_str = self.var.get()
      tag_lst = [s.strip() for s in tag_str.split(',')]
      if not tag_lst: return
      self.files = self.fo.findFiles(tag_lst)
      self.file_lst.delete(0, 'end')
      self.file_lst['fg'] = 'black'
      for grp in self.files:
         self.file_lst.insert('end', self.represent(grp))

   def represent(self, grp):
      "String with file representation"
      return "{0:32} /{1}".format(grp[1], os.path.split(grp[0])[-1])

   def fileInfo(self, ev):
      "Tags for current file"
      if self.state == SHOW_FILES and self.files:
         current = self.files[self.file_lst.index('active')]
         tags = self.fo.getTags(*current)
         self.var.set(', '.join(tags))

   def exec(self, ev):
      "Execute file or add tags to entry"
      if self.state == SHOW_FILES and self.files:
         current = self.files[self.file_lst.index('active')]
         return self.fo.execute(os.path.join(*current))
      else:
         add_tag = self.file_lst.get('active')
         cur_tag = self.var.get()
         self.var.set((cur_tag + ', ' + add_tag) if cur_tag else add_tag)

   def openPath(self, ev):
      "Open directory for current file in the file manager"
      if self.state == SHOW_FILES and self.files:
         current = self.files[self.file_lst.index('active')]
         self.open_path = current[0]
         self.slave.destroy()

   def callMenu(self, ev):
      if self.state == SHOW_TAGS:
         self.c_menu.post(ev.x_root, ev.y_root)

   def tagRename(self):
      current = self.file_lst.get('active')
      name = dlg.askstring("Rename tag", current)
      if name:
         self.fo.tagRename(name, current)
         self.tags = self.fo.tagList()
         self.reset(1)

   def tagDelete(self):
      current = self.file_lst.get('active')
      if msg.askyesno("Delete?", current):
         self.fo.tagDelete(current)
         self.tags = self.fo.tagList()
         self.reset(1)

   def wordComplete(self, ev):
      tag_str = self.var.get()
      tag_lst = [s.strip() for s in tag_str.split(',')]
      start = tag_lst[-1]
      if start == "": return
      if start.startswith(self.last_tag) and len(self.last_tag_lst) > 0:
         self.last_tag_num = (self.last_tag_num + 1) % len(self.last_tag_lst)
      else:
         self.last_tag_lst = self.fo.tagsStartsWith(start)
         if len(self.last_tag_lst) == 0: return
         self.last_tag, self.last_tag_num = start, 0
      tag_lst[-1] = self.last_tag_lst[self.last_tag_num]
      self.var.set(', '.join(tag_lst))




