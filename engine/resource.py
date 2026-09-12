

class Resource:

    def __init__(self, starting_amount: int, name: str = "Resource") -> None:
        self.resource = starting_amount
        self.name = name

    def gain_resource(self, amount: int) -> int:
        self.resource += amount
        return self.resource

    def spend_resource(self, amount: int) -> int:
        if amount < 0:
            # TODO: Add logging here for error notification
            return self.resource

        self.resource -= amount
        if self.resource < 0:
            self.resource = 0
        return self.resource