import json
import os
from random import randint

class DataIO():
    def save_json(self, filename, data):
        r = randint(1024,2048)
        p, e = os.path.splitext(filename)
        ftmp = "{}-{}.tmp".format(p,r)
        self._save_json(ftmp, data)
        try:
            self._read_json(ftmp)
        except:
            return False
        os.replace(ftmp, filename)

    def load_json(self, filename):
        try:
            return self._read_json(filename)
        except:
            return []

    def check_json(self, filename):
        try:
            self._read_json(filename)
            return True
        except FileNotFoundError:
            return False
        except json.decoder.JSONDecodeError:
            return False
        except:
            return False

    def _read_json(self, filename):
        with open(filename, mode='r', encoding='utf-8') as f:
            data = json.load(f)
        return data


    def _save_json(self, filename, data):
        with open(filename, mode='w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, separators=(',', ' : '), sort_keys=True)
        return data

    def file_io(self, filename, mode, data=None):
        if mode == "w" and data is not None:
            return self.save_json(filename, data)
        elif mode == "r" and data is None:
            return self.load_json(filename)
        elif mode == "c" and data is None:
            return self.check_json(filename)
        else:
            pass

dataIO = DataIO()
fileIO = dataIO.file_io
