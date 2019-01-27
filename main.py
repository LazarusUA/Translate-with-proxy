from py_translator import Translator
from polib import pofile
from threading import Thread


class TranslatePO(object):

    def __init__(self, dest: str = 'en', src: str = 'auto'):
        self.proxy = {
            'https': 'http://95.47.116.93:58865',
        }
        self.proxy_index = 0
        self.dest = dest
        self.src = src

    def __str__(self):
        res = {
            'proxy': self.proxy,
            'proxy_index': self.proxy_index
        }
        return f'{res}'

    @property
    def proxy_list(self, f_proxy: str = 'proxylist.txt') -> list:

        with open(f_proxy, 'r') as file:
            lines = file.readlines()

        return [line.replace('\n', '') for line in lines]

    def verify_proxy(self) -> str:
        proxy_list = self.proxy_list[self.proxy_index:]

        for i, proxy in enumerate(proxy_list):
            try:
                translator = Translator(proxies={
                    'https': 'http://%s' % proxy
                }, timeout=2)
                translator.translate('Hello', dest='de')
            except Exception:
                continue
            else:
                self.proxy_index += i
                print(f'proxy: {proxy}')
                return proxy

    def __translate(self, po_file):
        for i, po_line in enumerate(po_file):

            print(f'Loading: {i * 100 // len(po_file)}%', end='\r')

            tr = Translator(proxies=self.proxy, timeout=30)

            try:
                res = tr.translate(po_line.msgid,
                                   dest=self.dest, src=self.src)
            except Exception:
                self.proxy = {
                    'https': 'http://%s' % self.verify_proxy()
                }
                tr = Translator(proxies=self.proxy, timeout=30)
                res = tr.translate(po_line.msgid,
                                   dest=self.dest, src=self.src)

            po_line.msgstr = res.text

    @staticmethod
    def chunk(po_list, n):
        po_len = len(po_list)
        assert 0 < n <= po_len
        s = po_len // n
        return [po_list[p:p + s] for p in range(0, po_len, s)]

    def po_translate(self, file: str, out='res.po', is_thread=False):
        po_file = pofile(file)

        if is_thread:
            th_list = []

            for i, p in enumerate(self.chunk(po_file, 10)):
                th_list.append(Thread(target=self.__translate, args=(p,)))

            for i in th_list:
                i.start()

            for i in th_list:
                i.join()
        else:
            self.__translate(po_file)

        print('\nFINISH')

        with open(out, 'w') as out_file:
            for po_line in po_file:
                out_file.write(f'{str(po_line)}\n\n')


if __name__ == '__main__':
    trans = TranslatePO(dest='de', src='en')
    trans.po_translate('de.po', is_thread=True)
