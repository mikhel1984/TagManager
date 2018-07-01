# S.Mikhel, 2016
"""Represent list of files as a panel"""

import os
import time
from tkinter import ttk
from tkinter import Frame, Label, StringVar, Entry, PhotoImage

NAME, TYPE, SIZE, DATE = 'Name', 'Type', 'Size', 'Date'
PREVIOUS_DIR = "  ..  "
INIT_PATH = ".."     # parent directory

class FileList(Frame):
   "File representation as list with properties"

   def __init__(self, root, fileOp, index):
      Frame.__init__(self, root.root) # base class
      # additional paremeters
      self.isactive = (index == 0)
      self.root = root
      self.index = index
      self.reverse = False  # using reverse sorting
      # widgets
      self.dir_var = StringVar()
      self.sum_var = StringVar()
      self.tag_var = StringVar()
      self.dir = Label(self, textvariable=self.dir_var, fg='blue')
      self.summary = Label(self, textvariable=self.sum_var)
      self.taglist = Entry(self, textvariable=self.tag_var, state='readonly')
      self.list = ttk.Treeview(self, height=15)
      ysb = ttk.Scrollbar(self, orient='vertical', command=self.list.yview)
      self.list.configure(yscroll=ysb.set)
      self.list["columns"]=("#1","#2","#3")
      self.list.column("#0", stretch=True)
      self.list.column("#1", width=80, minwidth=80)
      self.list.column("#2", width=80, minwidth=80)
      self.list.column("#3", width=80, minwidth=80)
      self.list.heading("#0", text=NAME, command=lambda: self.sort(NAME))
      self.list.heading("#1", text=TYPE, command=lambda: self.sort(TYPE))
      self.list.heading("#2", text=SIZE, command=lambda: self.sort(SIZE))
      self.list.heading("#3", text=DATE, command=lambda: self.sort(DATE))
      self.list.tag_configure('dir', foreground='blue')
      # event binding
      self.list.tag_bind('dir', '<Return>', self.changeDirectory)
      self.list.tag_bind('dir', '<Right>', self.changeDirectory)
      self.list.tag_bind('dir', '<<TreeviewSelect>>', lambda x: self.tag_var.set(""))
      self.list.tag_bind('file', '<Return>', self.openFile)
      self.list.tag_bind('file', '<<TreeviewSelect>>', self.showTags)
      self.list.tag_bind('file', '<Control-t>', self.tagEdit)
      self.list.bind('<F2>', self.rename)
      self.list.bind('<F7>', self.newDir)
      self.list.bind('<Delete>', self.remove)
      self.list.bind('<Left>', self.previousDirectory)
      self.taglist.bind('<Double-ButtonRelease-1>', self.tagEdit)
      self.taglist.bind('<Return>', self.tagApply)
      self.taglist.bind('<Escape>', self.tagExit)
      self.taglist.bind('<Control-Right>', self.wordComplete)
      self.bind('<FocusIn>', self.makeActiveExt)
      self.bind('<FocusOut>', self.makeNonActive)
      # pack
      self.dir.grid(row=0, column=0, sticky='ns')
      self.list.grid(row=1, column=0, sticky='ns')
      ysb.grid(row=1, column=1, sticky='ns')
      self.summary.grid(row=2, column=0)
      self.taglist.grid(row=3, column=0, columnspan=2, sticky='ew')
      self.grid()
      # class for file operations
      self.fo = fileOp
      # autocompleting
      self.last_tag = ""
      self.last_tag_lst = []
      self.last_tag_num = 0
      self.position = None
      self.hash = 0
      # images for elements
      self.folder_img = PhotoImage(file="./manager/img/folder.gif")
      self.file_img = PhotoImage(file="./manager/img/file.gif")
      # path initialisation
      abspath = os.path.abspath(INIT_PATH)
      # fill panel
      self.writeFiles(abspath)

   def writeFiles(self, path):
      "Show list of files in current path"
      self.dir_var.set(path)
      # read files
      self.path_dir = []
      self.path_file = []
      self.hash = 0
      for p in os.listdir(path):
         if p.startswith('.'): continue    # hidden files
         if os.path.isdir(os.path.join(path,p)):
            self.path_dir.append(p)
         else:
            self.path_file.append(p)
         self.hash += hash(p)
      # read tags from base
      self.path_tags = {}
      for f in self.path_file:
         self.path_tags[f] = self.fo.getTags(path, f)
      # sort and insert
      self.sort(NAME, False)
      if self.isactive:
         self.makeActive()

   def filesize(self, x):
      "Pretty print for file size"
      letter = ("", " K", " M", " G")
      n = 0
      while x > 1023 and n < 3:
         x /= 1024.0
         n += 1
      return "%.1f%s" % (x, letter[n])

   def changeDirectory(self, ev):
      "Change current directory"
      folder = self.currentItem()[0]
      current_path = self.dir_var.get()
      if folder == PREVIOUS_DIR:
         self.writeFiles(os.path.split(current_path)[0])
      else:
         self.writeFiles(os.path.join(current_path, folder))

   def previousDirectory(self, ev):
      "Go to the previous directory"
      c_path = self.dir_var.get()
      self.writeFiles(os.path.split(c_path)[0])

   def makeActiveExt(self, ev):
      # check for changings
      tmp = 0
      for p in os.listdir(self.getPath()):
         if p.startswith('.'): continue
         tmp += hash(p)
      # update if need
      if tmp != self.hash:
         self.refresh()
      self.makeActive()


   def makeActive(self):
      "Set focus and cursor"
      self.isactive = True
      self.root.src = self.index
      iid = self.position if self.position else self.list.get_children()[0]
      # set selection
      self.list.selection_set(iid)
      self.list.focus_set()
      self.list.focus(iid)

   def makeNonActive(self, ev):
      "Clear cursor"
      self.isactive = False
      self.position = self.list.focus()
      # clear selection
      self.list.selection_remove(self.list.get_children())

   def currentItem(self):
      "Return name and type under cursor"
      focus = self.list.focus() if self.isactive else self.position
      item = self.list.item(focus)
      tp = item['values'][0] if item['values'] else ''
      return item['text'], tp

   def rename(self, ev):
      "Change name of a file (directory)"
      if self.fo.rename(self.getFocus()):
         self.refresh()

   def remove(self, ev):
      "Remove file (directory)"
      if self.fo.remove(self.getFocus()):
         self.refresh()

   def newDir(self, ev):
      "Create new directory"
      if self.fo.newDir(self.getPath()):
         self.list.focus_set()
         self.refresh()

   def getPath(self):
      "Get current folder path"
      return self.dir_var.get()

   def getName(self):
      "Get name under cursor as string"
      item = self.currentItem()
      return item[0] + item[1]

   def getFocus(self):
      "Get full path to the file under cursor"
      return os.path.join(self.dir_var.get(), self.getName())

   def refresh(self):
      "Refresh panel state"
      self.writeFiles(self.dir_var.get())

   def openFile(self, ev):
      "Execute file under cursor"
      self.fo.execute(self.getFocus())

   def sort(self, col, rev=True):
      "Sort file list according the parameter"
      path = self.dir_var.get()
      if col==NAME:
         self.path_dir.sort(reverse=self.reverse)
         self.path_file.sort(reverse=self.reverse)
      elif col==SIZE:
         self.path_file.sort(key=lambda x: os.path.getsize(os.path.join(path, x)),
                             reverse=self.reverse)
      elif col==TYPE:
         self.path_file.sort(key=lambda x: x.rsplit('.',1)[1] if '.' in x else '',
                             reverse=self.reverse)
      elif col==DATE:
         self.path_dir.sort(key=lambda x: os.path.getmtime(os.path.join(path,x)),
                            reverse=self.reverse)
         self.path_file.sort(key=lambda x: os.path.getmtime(os.path.join(path,x)),
                             reverse=self.reverse)
      else:
         return
      # change reversion if need
      if rev: self.reverse = not self.reverse
      # clear and start a new list
      self.list.delete(*self.list.get_children())
      self.position = self.list.insert("", 0, text=PREVIOUS_DIR, tags='dir')
      # folders
      for d in self.path_dir:
         tm = os.path.getmtime(os.path.join(path,d))
         self.list.insert("", "end", text=d, image=self.folder_img, values=
                   ("","<DIR>",time.strftime("%d.%m.%Y", time.gmtime(tm))), tags='dir')
      # files
      f_sum = 0
      for f in self.path_file:
         stat = os.stat(os.path.join(path,f))
         tm = stat.st_mtime
         sz = stat.st_size
         f_sum += sz
         nm, tp = os.path.splitext(f)
         self.list.insert("", "end", text=nm, tags='file', image=self.file_img, values=
                           (tp, self.filesize(sz), time.strftime("%d.%m.%Y", time.gmtime(tm))))
      self.sum_var.set("Folders: %d  Files: %d  Size: %s" % (
                          len(self.path_dir), len(self.path_file), self.filesize(f_sum)))

   def tagEdit(self, ev):
      "Open entry for tag edition"
      self.position = self.list.focus()
      self.taglist['state']='normal'
      self.taglist.focus_set()
      self.taglist.icursor('end')

   def tagApply(self, ev):
      "Apply tag modification"
      tag_str = self.tag_var.get()
      tag_lst = [s.strip() for s in tag_str.split(',')]
      if tag_lst:
         # save to database
         self.fo.setTags(self.getPath(), self.getName(), tag_lst)
      self.taglist['state']='readonly'
      self.path_tags[self.getName()] = tag_lst # add to current dictionary
      self.makeActive()

   def tagExit(self, ev):
      "Exit without saving"
      # return last state
      self.tag_var.set(self.path_tags[self.getName()])
      # exit
      self.taglist['state']='readonly'
      self.makeActive()

   def showTags(self, ev):
      "Show tags for current file"
      fname = self.getName()
      self.tag_var.set(', '.join(self.path_tags[fname]))

   def wordComplete(self, ev):
      "Complete tag by Ctrl+Right"
      # get last tag
      tag_str = self.tag_var.get()
      tag_lst = [s.strip() for s in tag_str.split(',')]
      start = tag_lst[-1]
      if start == "": return
      if start.startswith(self.last_tag) and len(self.last_tag_lst) > 0:
         # not first key press for current word
         self.last_tag_num = (self.last_tag_num + 1) % len(self.last_tag_lst)
      else:
         # first key press
         self.last_tag_lst = self.fo.tagsStartsWith(start)  # find similar tags
         if len(self.last_tag_lst) == 0: return
         self.last_tag, self.last_tag_num = start, 0
      # change string
      tag_lst[-1] = self.last_tag_lst[self.last_tag_num]
      self.tag_var.set(', '.join(tag_lst))

