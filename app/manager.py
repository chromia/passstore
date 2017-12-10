# -*- coding: utf-8 -*-

import os
import shutil
import dataobject
from cipher import Cipher

# Where to save the encrypted data files
datafolder = "./.data"

# Where to back up datafolder temporary
backupfolder = "./.backup"

# Extension of data file(any)
extension = '.dat'

# your favorite encoding
encodemethod = "utf-8"


def makepath(title):
    return datafolder + '/' + title + extension


class Entry:
    def __init__(self, filepath, title="", data=None):
        self.filepath = filepath
        self.title = title
        self.data = data


class Manager:
    """
    Manager is a class handling encrypeted file and its record data.
    It has various operations such as read/write/rename/remove/update.
    You can access to each file information via self.files( is list of 'Entry' )
    """
    def __init__(self, passphrase):
        self.cipher = Cipher(passphrase)

    def fileread(self, filepath):
        (success, rawdata) = self.cipher.load(filepath)
        if not success:
            return (success, None)
        else:
            data = dataobject.Data()
            data.load(rawdata)
            return (success, data)

    def filewrite(self, filepath, data):
        text = data.store()
        if not os.path.exists(datafolder):
            os.mkdir(datafolder)
        return self.cipher.save(filepath, text)

    def load(self):
        self.files = []
        if not os.path.exists(datafolder):
            return True
        for file in os.listdir(datafolder):
            if not os.path.isdir(file):
                print('[' + file + ']')
                title, ext = os.path.splitext(file)
                if ext != extension:
                    continue
                filepath = makepath(title)
                (success, data) = self.fileread(filepath)
                print(filepath, success)
                if not success:
                    print("error: data read failed {}. ".format(file))  # Fatal read error
                    return False
                else:
                    e = Entry(filepath, title, data)
                    self.files.append(e)
        return True

    def update(self, entry):
        index = self.files.index(entry)
        if index != -1:
            return self.filewrite(entry.filepath, entry.data)
        else:
            return False

    def add(self, filetitle):
        for file in self.files:
            if file.title == filetitle:
                return False
        filepath = makepath(filetitle)
        e = Entry(filepath, filetitle, dataobject.Data())
        self.files.append(e)
        self.filewrite(e.filepath, e.data)
        return True

    def remove(self, entry):
        index = self.files.index(entry)
        try:
            os.remove(entry.filepath)
        except OSError:
            return False
        else:
            self.files.pop(index)
            return True

    def rename(self, entry, newname):
        for file in self.files:
            if file.title == newname:
                return False
        else:
            try:
                newpath = makepath(newname)
                os.rename(entry.filepath, newpath)
            except OSError:
                return False
            else:
                entry.title = newname
                entry.filepath = newpath
                return True

    def backup(self):
        if os.path.exists(backupfolder):
            try:
                shutil.rmtree(backupfolder)
            except:
                return False
        try:
            shutil.copytree(datafolder, backupfolder)
        except:
            return False
        else:
            return True

    def rollback(self):
        try:
            shutil.rmtree(datafolder)
            shutil.copytree(backupfolder, datafolder)
        except:
            return False  # give up
            # TODO : logging more detailed information for recovery
        else:
            return True

    def update_password(self, newpass):
        # Save all data file again with new passphrase
        # Backup current data folder just in case
        if not self.backup():
            print('backup failed.')
            return False
        # Recreate cipher with new passphrase
        self.cipher = Cipher(newpass)
        # Encrypting all
        try:
            for file in self.files:
                if not self.filewrite(file.filepath, file.data):
                    raise Exception
        except:
            # Unfortunately there was a failed operation, so rollback everything
            if not self.rollback():
                pass  # umm...
            return False
        else:
            return True


if __name__ == '__main__':
    pass
