

class Resource:

    def __init__(self, starting_amount: int, name: str = "Resource") -> None:
        self.amount = starting_amount
        self.name = name

    def gain_resource(self, amount: int) -> int:
        self.amount += amount
        return self.amount

    def spend_resource(self, amount: int) -> int:
        if amount < 0:
            # TODO: Add logging here for error notification
            return self.amount

        self.amount -= amount
        if self.amount < 0:
            self.amount = 0
        return self.amount

    def set_resource(self, amount: int) -> int:
        self.amount = amount
        return self.amount