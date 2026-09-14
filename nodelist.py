from models import Node, Session, Duration

class Monthlist:
    def __init__(self):
        self.head: Node | None = None

    def insert_sorted(self, session): 
        new_node = Node(session)
        