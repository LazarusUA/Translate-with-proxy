from py_translator import Translator


class TranslateFile(object):

    def __init__(self, dest: str, src: str = 'auto'):
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
    def proxy_list(self, f_proxy='proxylist.txt') -> list:

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
                self.proxy_index = i
                print(f'proxy: {proxy}')
                return proxy

    def f_translate(self, file: str, out='res.po'):
        with open(file, 'r') as ofile:
            text_file = ofile.readlines()
            with open(out, 'w') as ifile:

                tr = Translator(proxies=self.proxy, timeout=30)

                for i, line in enumerate(text_file):
                    if i % 10 == 0:
                        print(f'Loading: {i * 100 // len(text_file)}%',
                              end='\r')

                    before_lst = text_file[i - 1].split('\"')
                    if 'msgstr' in line.split() and 'msgid ' in before_lst[0]:
                        text = before_lst[1]

                        try:
                            res = tr.translate(text,
                                               dest=self.dest, src=self.src)
                        except Exception:
                            self.proxy = {
                                'https': 'http://%s' % self.verify_proxy()
                            }
                            tr = Translator(proxies=self.proxy, timeout=30)
                            res = tr.translate(text,
                                               dest=self.dest, src=self.src)

                        ifile.write(f"msgstr \"{res.text}\"\n")
                    else:
                        ifile.write(line)

                print('\nFinish.')


if __name__ == '__main__':
    trans = TranslateFile(dest='de', src='en')
    trans.f_translate('de.po')
