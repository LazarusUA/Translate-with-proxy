from threading import Thread
from queue import Queue


class ThreadPool(Queue):
    __th_list = []

    def __init__(self, size, method, data=None):
        super(ThreadPool, self).__init__()
        self.__method = method

        for i in range(size):
            self.__th_list.append(Thread(target=self.__work, daemon=True))

        for el in data:
            self.put(el)

    def __work(self):
        while not self.empty():
            el = self.get()
            try:
                if self.__method:
                    self.__method(el)
            finally:
                self.task_done()

    def start(self):
        for th in self.__th_list:
            th.start()

    def clear(self):
        while not self.empty():
            self.get_nowait()
            self.task_done()
