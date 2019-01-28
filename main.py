#!./translate_venv/bin/python3

from py_translator import Translator
from polib import pofile
from threading import Thread
from proxies import Proxies
from queue import Queue


class TranslatePO(object):

    def __init__(self, dest: str = 'en', src: str = 'auto',
                 proxy_size=20, th_size=0):
        self.dest = dest
        self.src = src

        self.proxies = Proxies(proxy_len=proxy_size)
        self.proxies.verify_proxies()
        self.pool = Queue()
        self.loading_index = 0
        self.loading_len = 0
        self.th_size = th_size

    def __translate(self):
        while not self.pool.empty():
            line = self.pool.get()

            print(f'Loading: {self.loading_index * 100 // self.loading_len}%',
                  end='\r')

            curr_proxy = self.proxies.pool.get_nowait()
            tr = Translator(proxies=curr_proxy, timeout=30)

            res = None

            try:
                res = tr.translate(line.msgid,
                                   dest=self.dest, src=self.src)
            except Exception:
                curr_proxy = self.proxies.pool.get_nowait()
                tr = Translator(proxies=curr_proxy, timeout=30)
                res = tr.translate(line.msgid,
                                   dest=self.dest, src=self.src)
            finally:
                self.proxies.pool.put_nowait(curr_proxy)
                line.msgstr = res.text if res else ''
                self.loading_index += 1
                self.pool.task_done()

    def po_translate(self, file: str, out='res.po'):
        po_file = pofile(file)
        self.loading_len = len(po_file)

        for line in po_file:
            self.pool.put(line)

        if self.th_size:
            for i in range(self.th_size):
                th = Thread(target=self.__translate)
                th.setDaemon(True)
                th.start()

            self.pool.join()
        else:
            self.__translate()

        print('\nFINISH')

        with open(out, 'w') as out_file:
            for po_line in po_file:
                out_file.write(f'{str(po_line)}\n\n')


if __name__ == '__main__':
    trans = TranslatePO(dest='de', src='en', proxy_size=40, th_size=20)
    trans.po_translate('de.po')
