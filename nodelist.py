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

    def get_all(self):
        results = []
        current = self.head
        while current is not None:
            results.append(current.session)
            current = current.next
        return results

    def get_for_day(self, day):
        sessions = []
        for s in self.get_all():
            if s.when == day:
                sessions.append(s)
        return sessions

    def delete(self, day, index):
        current = self.head
        prev = None
        count = 0

        while current is not None:
            if current.session.when == day:
                if count == index:
                    if prev is None:
                        self.head = current.next
                    else:
                        prev.next = current.next
                    return True
                count += 1
            prev = current
            current = current.next


        return False

if __name__ == "__main__":
    from datetime import date
    from models import Duration, Session

    list = Monthlist()
    list.insert_sorted(Session("kväll", date(2026, 6, 1), 5.0, Duration(1, 30, 45)))
    list.insert_sorted(Session("morgon", date(2026, 6, 1), 5.0, Duration(1, 10, 0)))
    list.insert_sorted(Session("eftermiddag", date(2026, 6, 1), 5.0, Duration(1, 23, 34)))

    for s in list.get_all():
        print(s.when, s.description, s.duration)

    print("day 5:", [s.description for s in list.get_for_day(date(2026, 6, 1))])
    list.delete(date(2026, 6, 1), 1)
    print("After deletion:")
    for s in list.get_all():
        print(s.when, s.description, s.duration)