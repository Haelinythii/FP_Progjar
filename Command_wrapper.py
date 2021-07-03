class Command_Wrapper:
    def __init__(self, command, dest, args) -> None:
        self.command = command
        self.dest = dest
        self.args = args

    def __sizeof__(self) -> int:
        pass