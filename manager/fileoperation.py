"""
Operation with files and interface for database
"""

import os
import shutil
import subprocess
import tkinter.simpledialog as dlg
import tkinter.messagebox as msg

from .tagbase import TagBase
from tmconfig import programs, delete

DB_NAME = './manager/db/tags.db'

class FileOperation:
   "Execute file operations and contain database inside"

   def __init__(self):
      self.db = TagBase(DB_NAME)
      # get program list
      self.run_cmd = {}
      for k in programs:
        for elt in programs[k]:
          self.run_cmd[elt] = k

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
         # remove (to trash)
         subprocess.call([delete, fname])
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
            self.db.addDirCopy(full_name, src)
            shutil.copytree(src, full_name)
         else:
            # check existance
            if self.isExistFile(full_name): return
            # update database
            self.db.addFileCopy(dst, *path)
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
         # update database
         if os.path.isfile(src):
            self.db.changeFilePath(dst, *path)
         else:
            self.db.changeDirPath(full_path, src)
         # move
         shutil.move(src, full_path)
         return True
      else:
         return False

   def execute(self, fname):
      "Execute current file"
      nm, tp = os.path.splitext(os.path.split(fname)[1])
      if tp: tp = tp[1:].lower()  # remove '.', correct size
      if tp in self.run_cmd.keys():
         return subprocess.call([self.run_cmd[tp], fname])

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

   def baseInfo(self):
      "String with statistic about database"
      return self.db.baseInfo()

   def tagList(self):
      "Get list of all tags"
      return self.db.tagList()

   def findFiles(self, tags):
      "Find files with given tags"
      return self.db.findFiles(tags)
      
   def findByName(self, name):
      "Find files using part of file name"
      return self.db.findByName(name)

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

   def getRandomFile(self):
      "Get random element from the database"
      return self.db.getRandom()
