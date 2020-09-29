class Size:

    def __init__(self, width, height):
        self.width = width
        self.height = height

    def scale(self, factor):
        return Size(self.width * factor, self.height * factor)

    def formatted(self):
        return f'{int(self.height)}x{int(self.width)}'

class Device:

    def __init__(self, name, id):
        self.name = name
        self.id = id
