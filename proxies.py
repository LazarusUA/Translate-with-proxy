from queue import Queue
from py_translator import Translator
from threading import Thread


class Proxies(object):

    def __init__(self, proxy_len, proxy_file='proxylist.txt'):
        self.pool = Queue()
        self.finder_pool = Queue()
        self.__proxy_lines = self.__proxy_list(proxy_file)
        self.verify_proxy_lines = []
        self.proxy_len = proxy_len

    @staticmethod
    def __proxy_list(proxy_file):
        with open(proxy_file, 'r') as file:
            lines = [line.replace('\n', '') for line in file.readlines()]

            return [
                {'https': f'http://{line}'} for line in lines if line
            ]

    def __clear(self):
        if len(self.verify_proxy_lines) >= self.proxy_len:
            while not self.finder_pool.empty():
                self.finder_pool.get()
                self.finder_pool.task_done()

    def __find(self, timeout):
        while not self.finder_pool.empty():
            proxy = self.finder_pool.get()

            try:
                translator = Translator(proxies=proxy, timeout=timeout)
                translator.translate('Hello', dest='de')
            except Exception:
                pass
            else:
                if self.finder_pool.qsize():
                    print(f'Proxy: {proxy}')
                    self.verify_proxy_lines.append(proxy)
                    self.pool.put_nowait(proxy)
            finally:
                self.finder_pool.task_done()
                self.__clear()

    def verify_proxies(self, timeout=2):
        print('Verify proxies: START')

        for proxy in self.__proxy_lines:
            self.finder_pool.put(proxy)

        for i in range(20):
            th = Thread(target=self.__find, args=(timeout,))
            th.setDaemon(True)
            th.start()

        self.finder_pool.join()
