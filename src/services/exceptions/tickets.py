class TicketNotFoundException(Exception):
    def __init__(self):
        super().__init__("Ticket with given ID is not found")


class IncorrectTicketAmountException(Exception):
    def __init__(self):
        super().__init__("Ticket payment amount is less than sum of products cost")

