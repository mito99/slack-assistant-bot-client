from collections import deque


class OrderedFixedSizeSet:
    def __init__(self, maxsize=10):
        self.maxsize = maxsize
        self.items = deque(maxlen=maxsize)
        self.item_set = set()

    def add(self, item):
        if item not in self.item_set:
            if len(self.items) >= self.maxsize:
                old_item = self.items.popleft()
                self.item_set.remove(old_item)
            self.items.append(item)
            self.item_set.add(item)

    def __contains__(self, item):
        return item in self.item_set

    def __len__(self):
        return len(self.items)

    def __str__(self):
        return str(list(self.items))
