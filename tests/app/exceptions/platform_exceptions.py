class PlatformSupportError(Exception):
    def __init__(self, message, field_name=None):
        self.message = message
        self.field_name = field_name
        super().__init__(self.message)

    def __str__(self):
        if self.field_name:
            return f"[{self.field_name}] {self.message}"
        return self.message
