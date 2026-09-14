from models import Node, Session, Duration

class Monthlist:
    def __init__(self):
        self.head: Node | None = None

    def insert_sorted(self, session): 
        new_node = Node(session)

        if self.head is None or session.when < self.head.session.when:
            new_node.next = self.head
            self.head = new_node
            return

        current = self.head
        while current.next is not None and current.next.session.when < session.when:
            current = current.next

        new_node.next = current.next
        current.next = new_node
