# -*- coding: utf-8 -*-

from io import StringIO

"""
Too simple key-value store
The format is "key:value" in each line
key is duplicate possible
"""


class DataPair:
    def __init__(self, key, value):
        self.key = key
        self.value = value


class Data:
    def __init__(self):
        self.pairs = []  # list of DataPair

    def load(self, datatext):
        ss = StringIO(datatext)
        for line in ss:
            t = line.rstrip()
            if len(t) == 0:
                continue
            p = t.find(':')
            if p != -1:
                key = t[:p]
                value = t[p + 1:]
                self.pairs.append(DataPair(key, value))
            else:
                print('error: bad entry is detected.', t)

    def store(self):
        ss = StringIO()
        for rawdata in self.pairs:
            line = rawdata.key + ':' + rawdata.value
            ss.write(line + '\n')
        return ss.getvalue()


if __name__ == '__main__':
    pass
