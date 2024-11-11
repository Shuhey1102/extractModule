class Stack:
    def __init__(self):
        self.items = []  # スタックを初期化
    def push(self, item):
        self.items.append(item)  # 要素を追加
    def pop(self):
        return self.items.pop()  # 要素を取り出し
    def peek(self):
        return self.items[-1] if not self.is_empty() else None  # 先頭要素を確認
    def is_empty(self):
        return len(self.items) == 0  # スタックが空か確認
    def size(self):
        return len(self.items)  # スタックのサイズを取得

