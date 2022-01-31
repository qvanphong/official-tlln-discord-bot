class AdvancedRandomModel:
    minimum = 0
    maximum = 100
    owner = None
    channel_id = None

    def __init__(self, owner, minimum, maximum, channel_id):
        self.owner = owner
        self.minimum = minimum
        self.maximum = maximum
        self.channel_id = channel_id
        self.exclude = []

