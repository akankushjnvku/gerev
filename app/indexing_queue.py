import logging
import queue
import threading
from queue import Queue
from typing import List

from data_source_api.basic_document import BasicDocument


class IndexingQueue:
    __instance = None
    __lock = threading.Lock()

    @classmethod
    def get(cls):
        with cls.__lock:
            if cls.__instance is None:
                cls.__instance = cls()
        return cls.__instance

    def __init__(self):
        if IndexingQueue.__instance is not None:
            raise RuntimeError("DocsQueue is a singleton, use DocsQueue.get() to get the instance")

        self.queue: Queue[BasicDocument] = queue.Queue()
        self.condition = threading.Condition()

    def feed_single(self, doc: BasicDocument):
        self.feed([doc])

    def feed(self, docs: List[BasicDocument]):
        with self.condition:
            for doc in docs:
                self.queue.put(doc)

            self.condition.notify_all()

    def consume_all(self, max_docs=5000, timeout=1) -> List[BasicDocument]:
        with self.condition:
            self.condition.wait(timeout=timeout)

            docs = []
            count = 0
            while not self.queue.empty() and count < max_docs:
                docs.append(self.queue.get())
                count += 1

            return docs

    def get_how_many_left(self) -> int:
        return self.queue.qsize()
