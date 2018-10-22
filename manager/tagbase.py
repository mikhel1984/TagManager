# S.Mikhel, 2016
"""Database manager commands"""

import sqlite3
import os
import random

class TagBase:
   "Management of SQLite3 data base"

   def __init__(self, db_name):
      # check base, open
      new_base = not os.path.exists(db_name)
      self.db = sqlite3.connect(db_name)
      self.db_name = os.path.split(db_name)[1]
      cursor = self.db.cursor()
      cursor.execute("PRAGMA foreign_keys = ON")
      # create new if need
      if new_base:
         cursor.execute("CREATE TABLE files (fid INTEGER PRIMARY KEY, "
                        "f_name TEXT NOT NULL, f_path TEXT NOT NULL,"
                        "UNIQUE(f_name, f_path))")
         cursor.execute("CREATE TABLE tags (tid INTEGER PRIMARY KEY, "
                        "t_name TEXT NOT NULL UNIQUE)")
         cursor.execute("CREATE TABLE filetags (fid INTEGER, tid INTEGER,"
                        "PRIMARY KEY(fid, tid), "
                        "FOREIGN KEY(fid) REFERENCES files ON DELETE CASCADE, "
                        "FOREIGN KEY(tid) REFERENCES tags ON DELETE CASCADE)")
         # delete tags if they are not more in use
         cursor.execute("CREATE TRIGGER tag_del AFTER DELETE ON files "
                        "BEGIN "
                        "DELETE FROM tags WHERE tid NOT IN "
                        "(SELECT DISTINCT tid FROM filetags); "
                        "END")
      self.db.commit()
      # prepare random
      random.seed()

   def addFile(self, path, nm):
      "Insert new file"
      # insert
      cursor = self.db.cursor()
      cursor.execute("INSERT INTO files VALUES (null, ?, ?)", (nm, path))
      self.db.commit()
      # get id
      cursor.execute("SELECT last_insert_rowid()")
      f_id = cursor.fetchone()
      return f_id[0] if f_id else -1

   def fileId(self, path, nm):
      "Get file index"
      cursor = self.db.cursor()
      cursor.execute("SELECT fid FROM files WHERE f_name=? AND f_path=?", (nm, path))
      f_id = cursor.fetchone()
      return f_id[0] if f_id else -1

   def addTag(self, tag):
      "Insert new tag"
      # insert
      cursor = self.db.cursor()
      cursor.execute("INSERT INTO tags VALUES (null, ?)", (tag.lower(),))
      self.db.commit()
      # get id
      cursor.execute("SELECT last_insert_rowid()")
      t_id = cursor.fetchone()
      return t_id[0] if t_id else -1

   def tagId(self, tag):
      "Get tag index"
      cursor = self.db.cursor()
      cursor.execute("SELECT tid FROM tags WHERE t_name=?", (tag.lower(),))
      t_id = cursor.fetchone()
      return t_id[0] if t_id else -1

   def tagsToFile(self, path, nm, tags):
      "Bind tags to file"
      # find file, add if need
      f_id = self.fileId(path, nm)
      if f_id == -1: f_id = self.addFile(path, nm)
      # link tags
      for tag in tags:
         if tag == "": continue   # eliminate empty strings
         # find or add tag
         t_id = self.tagId(tag)
         if t_id==-1: t_id = self.addTag(tag)
         # insert
         self.db.cursor().execute("INSERT INTO filetags VALUES (?, ?)", (f_id, t_id))
      self.db.commit()

   def delFile(self, path, nm):
      "Delete file from database"
      self.db.cursor().execute("DELETE FROM files WHERE f_name=? AND f_path=?", (nm, path))
      self.db.commit()

   def delFolder(self, path):
      "Delete all contestant of folder from database"
      self.db.cursor().execute("DELETE FROM files WHERE f_path LIKE ?",
                                (path+'%',))
      self.db.commit()

   def delTag(self, tname):
      "Delete tag with given name"
      self.db.cursor().execute("DELETE FROM tags WHERE t_name=?", (tname,))
      self.db.commit()


   def changeFileName(self, new_nm, path, old_nm):
      "Change file name"
      self.db.cursor().execute("UPDATE files SET f_name=? WHERE f_name=? AND f_path=?",
                               (new_nm, old_nm, path))
      self.db.commit()

   def changeFilePath(self, new_path, old_path, nm):
      "Change path to file"
      self.db.cursor().execute("UPDATE files SET f_path=? WHERE f_name=? AND f_path=?",
                               (new_path, nm, old_path))
      self.db.commit()

   def changeDirPath(self, new_path, old_path):
      "Change path to directory"
      self.db.cursor().execute("UPDATE files SET f_path=REPLACE(f_path, ?, ?) "
                               "WHERE f_path LIKE ?", (old_path, new_path, old_path+'%'))
      self.db.commit()

   def baseInfo(self):
      "Get information about database"
      cursor = self.db.cursor()
      cursor.execute("SELECT COUNT(*) FROM files")
      f_num = cursor.fetchone()[0]
      cursor.execute("SELECT COUNT(*) FROM tags")
      t_num = cursor.fetchone()[0]
      return "{0} - files:{1}, tags:{2}".format(self.db_name, f_num, t_num)

   def findFiles(self, tags):
      "Find files with given tags"
      # get tag id-s
      tag_id = []
      for tag in tags:
         _id = self.tagId(tag)
         if _id != -1: tag_id.append(str(_id))
      cursor = self.db.cursor()
      cursor.execute("SELECT f_path, f_name FROM files WHERE fid IN "
                     "(SELECT fid FROM filetags WHERE tid IN ({0}) "
                     "GROUP BY fid HAVING COUNT(*) >= {1})".format(','.join(tag_id), len(tag_id)))
      # return list of files (path, name)
      return cursor.fetchall()

   def findByName(self, nm):
      cursor = self.db.cursor()
      cursor.execute("SELECT f_path, f_name FROM files WHERE f_name LIKE ?", ('%'+nm+'%',))
      return cursor.fetchall()
   
   def getFileTags(self, path, nm):
      "Get tags for current file"
      cursor = self.db.cursor()
      cursor.execute("SELECT t_name FROM tags NATURAL JOIN filetags NATURAL JOIN files f "
                     "WHERE f.f_name=? AND f.f_path=?", (nm, path))
      return [tag[0] for tag in cursor.fetchall()]

   def breakLink(self, path, nm, tag):
      "Break link between file and tag"
      self.db.cursor().execute("DELETE FROM filetags WHERE "
         "fid = (SELECT f.fid FROM files f WHERE f.f_name=? AND f.f_path=?) AND "
         "tid = (SELECT t.tid FROM tags t WHERE t.t_name=?)", (nm, path, tag))
      self.db.commit()

   def updateFileTags(self, path, nm, new_tags):
      "Update list of tags for given file"
      old_tags = self.getFileTags(path, nm)
      t_add = [i for i in new_tags if i not in old_tags]  # tags for adding
      t_rem = [j for j in old_tags if j not in new_tags]  # tags for removing
      # remove
      for r in t_rem:
         self.breakLink(path, nm, r)
      # add
      if t_add:
         self.tagsToFile(path, nm, t_add)

   def addFileCopy(self, copy_path, path, nm):
      "Add copy of file"
      tags = self.getFileTags(path, nm)
      if tags:
         self.tagsToFile(copy_path, nm, tags)

   def addDirCopy(self, dst_path, src_path):
      "Add copy of whole directory"
      cursor = self.db.cursor()
      # get files from source directory
      cursor.execute("SELECT f_path, f_name FROM files WHERE f_path LIKE ?", (src_path+'%',))
      file_lst = cursor.fetchall()
      # add new files
      for f in file_lst:
         tags = self.getFileTags(*f)
         if tags:
            self.tagsToFile(f[0].replace(src_path, dst_path), f[1], tags)


   def tagRename(self, new_tag, old_tag):
      "Change tag name"
      self.db.cursor().execute("UPDATE tags SET t_name=? WHERE t_name=?",
                               (new_tag, old_tag))
      self.db.commit()

   def tagList(self):
      "List of all tags"
      cursor = self.db.cursor()
      cursor.execute("SELECT t_name FROM tags ORDER BY t_name")
      return [tag[0] for tag in cursor.fetchall()]

   def correct(self):
      "Remove files which are no more exists"
      cursor = self.db.cursor()
      # get all files
      cursor.execute("SELECT f_path, f_name FROM files")
      # remove if not exist
      for f in cursor.fetchall():
         if not os.path.exists(os.path.join(*f)): self.delFile(*f)

   def tagsStartsWith(self, start):
      "Find tags which starts with current word"
      cursor = self.db.cursor()
      cursor.execute("SELECT t_name FROM tags WHERE t_name LIKE ?"
                     "ORDER BY t_name", (start+'%',))
      return [tag[0] for tag in cursor.fetchall()]

   def printTables(self):
      "Debug: print tables"
      cursor = self.db.cursor()
      cursor.execute("SELECT * FROM files")
      print("\nFiles")
      for f in cursor.fetchall(): print(f)
      cursor.execute("SELECT * FROM tags")
      print("\nTags")
      for t in cursor.fetchall(): print(t)
      cursor.execute("SELECT * FROM filetags")
      print("\nFileTags")
      for ft in cursor.fetchall(): print(ft)

   def close(self):
      "Close database"
      self.db.close()
      
   def getRandom(self):
      "Choose random field from the database"
      cursor = self.db.cursor()
      # get range
      cursor.execute("SELECT MIN(fid) FROM files")
      a = cursor.fetchone()[0]
      cursor.execute("SELECT MAX(fid) FROM files")
      b = cursor.fetchone()[0]
      if a == b:
         return ""
      while True:
         cursor.execute("SELECT f_path, f_name FROM files WHERE fid=?", (random.randint(a,b),))
         lst = cursor.fetchone()
         if lst:
            return os.path.join(*lst)

