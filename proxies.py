from queue import Queue
from py_translator import Translator
from threading import Thread


class Proxies(object):

    def __init__(self, proxy_len, proxy_file='proxylist.txt'):
        self.finder_pool = Queue()
        self.__proxy_lines = self.__proxy_list(proxy_file)
        self.done_proxies = List()
        self.proxy_len = proxy_len

    @staticmethod
    def __proxy_list(proxy_file):
        with open(proxy_file, 'r') as file:
            lines = [line.replace('\n', '') for line in file.readlines()]

            return [
                {'https': 'http://%s' % line} for line in lines if line
            ]

    def __clear(self):
        if len(self.done_proxies) >= self.proxy_len:
            while not self.finder_pool.empty():
                self.finder_pool.get()
                self.finder_pool.task_done()

    def __loading(self):
        progress = len(self.done_proxies) * 100 // self.proxy_len
        print('Find proxy: %s%%' % progress, end='\r')

    def __find(self, timeout):
        while not self.finder_pool.empty():
            self.__loading()
            proxy = self.finder_pool.get()

            try:
                translator = Translator(proxies=proxy, timeout=timeout)
                translator.translate('Hello', dest='de')
            except Exception:
                pass
            else:
                if self.finder_pool.qsize():
                    self.done_proxies.put(proxy)
            finally:
                self.finder_pool.task_done()
                self.__clear()

    def verify_proxies(self, timeout=1, th_size=20):
        for proxy in self.__proxy_lines:
            self.finder_pool.put(proxy)

        for i in range(th_size):
            th = Thread(target=self.__find, args=(timeout,))
            th.setDaemon(True)
            th.start()

        self.finder_pool.join()


class List(list):
    def put(self, el):
        self.append(el)

    def get_last(self):
        return self.pop(-1) if self else None

    def get(self):
        return self.pop(0) if self else None
