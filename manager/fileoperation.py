# S.Mikhel, 2016
"""Operation with files and interface for database"""

import os
import shutil
import subprocess
import tkinter.simpledialog as dlg
import tkinter.messagebox as msg

from .tagbase import TagBase

IMG = 'ristretto'
RUN_CMD = {'jpg':IMG, 'bmp':IMG, 'png':IMG}

DB_NAME = './manager/db/tags.db'
TRASH = 'gvfs-trash'

class FileOperation:
   "Execute file operations and contain database inside"

   def __init__(self):
      self.base_name = DB_NAME    # ???
      self.db = TagBase(DB_NAME)

   def rename(self, old_name):
      "Rename file (directory)"
      path = os.path.split(old_name)
      nm, tp = os.path.splitext(path[1])
      # don't change file type
      name = dlg.askstring("Rename", nm)
      if name:
         new_name = name+tp
         full_name = os.path.join(path[0], new_name)
         # change existance
         if (os.path.isfile(old_name) and self.isExistFile(full_name) or
             os.path.isdir(old_name) and self.isExistDir(full_name)): return
         # add to database
         if os.path.isfile(old_name):
            self.db.changeFileName(new_name, *path)
         # rename
         os.rename(old_name, full_name)
         return True
      else:
         return False

   def remove(self, fname):
      "Remove file (directory)"
      path = os.path.split(fname)
      if msg.askyesno("Remove ?", path[1]):
         # update tags
         if os.path.isdir(fname):
            self.db.delFolder(fname)
         else:
            self.db.delFile(*path)
         # remove to trash
         subprocess.call([TRASH, fname])
         return True
      else:
         return False

   def newDir(self, path):
      "Add new folder"
      name = dlg.askstring("New folder", "Enter name")
      if name:
         full_name = os.path.join(path, name)
         # check
         if self.isExistDir(full_name): return
         os.mkdir(full_name)
         return True
      else:
         return False

   def copy(self, src, dst):
      "Copy file (directory)"
      path = os.path.split(src)
      name = path[1]
      if msg.askyesno("Copy", name) and os.path.isdir(dst):
         full_name = os.path.join(dst, name)
         if os.path.isdir(src):
            # check existance
            if self.isExistDir(full_name): return
            # self.db...
            shutil.copytree(src, full_name)
         else:
            # check existance
            if self.isExistFile(full_name): return
            # update database
            self.db.addCopy(dst, *path)
            # copy
            shutil.copyfile(src, full_name)
         return True
      else:
         return False

   def move(self, src, dst):
      "Move file (directory)"
      path = os.path.split(src)
      name = path[1]
      if msg.askyesno("Move", name) and os.path.isdir(dst):
         full_path = os.path.join(dst, name)
         # check existance
         if (os.path.isfile(src) and self.isExistFile(full_path) or
             os.path.isdir(src) and self.isExistDir(full_path)): return
         # self.db...
         # update database
         if os.path.isfile(src):
            self.db.changeFilePath(dst, *path)
         # move
         shutil.move(src, full_path)
         return True
      else:
         return False

   def execute(self, fname):
      "Execute current file"
      nm, tp = os.path.splitext(os.path.split(fname)[1])
      if tp: tp = tp[1:].lower()  # remove '.', correct size
      if tp in RUN_CMD.keys():
         return subprocess.call([RUN_CMD[tp], fname])

   def isExistFile(self, path):
      "Check file existance, show error"
      if os.path.exists(path):
         msg.showerror("File exist", os.path.split(path)[1])
         return True
      return False

   def isExistDir(self, path):
      "Check directory existance, show error"
      if os.path.exists(path):
         msg.showerror("Folder exist", os.path.split(path)[1])
         return True
      return False

   def getTags(self, path, name):
      "Get tag list for current file"
      return self.db.getFileTags(path, name)

   def setTags(self, path, name, tags):
      "Update file tags"
      self.db.updateFileTags(path, name, tags)

   #def getFiles(self, path):
   #   "Get list of files for given folder"
   #   return self.db.getFilesInFolder(path)

   #def deleteFromBase(self, path, nm):
   #   "Delete file from base"
   #   self.db.delFile(path, nm)

   def baseInfo(self):
      "String with statistic about database"
      return self.db.baseInfo()

   def tagList(self):
      "Get list of all tags"
      return self.db.tagList()

   def findFiles(self, tags):
      "Find files with given tags"
      return self.db.findFiles(tags)

   def correctDb(self):
      "Remove from database files wich are no more exist"
      self.db.correct()
      msg.showinfo("DB correction", "Done")

   def tagRename(self, new_name, old_name):
      "Change tag name"
      self.db.tagRename(new_name, old_name)

   def tagDelete(self, tname):
      "Delete tag from database"
      self.db.delTag(tname)

   def tagsStartsWith(self, start):
      "Get list of tags starts with given word"
      return self.db.tagsStartsWith(start)

