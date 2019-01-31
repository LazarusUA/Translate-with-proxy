from threading import Thread
from queue import Queue


class ThreadPool(object):
    __method = None
    __th_list = []

    pool = Queue()

    def __init__(self, size, method, data=None):
        self.__method = method

        for i in range(size):
            self.__th_list.append(Thread(target=self.__work,
                                         daemon=True))

        for el in data:
            self.pool.put(el)

    def __work(self):
        while not self.pool.empty():
            el = self.pool.get()
            try:
                if self.__method:
                    self.__method(el)
            finally:
                self.pool.task_done()

    def start(self):
        for th in self.__th_list:
            th.start()

    def close(self):
        pass

    def join(self):
        self.pool.join()
