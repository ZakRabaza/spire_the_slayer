class Color:
    # style
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = '\033[2m'
    NORMAL = '\033[22m'

    # text colors
    BLACK = '\033[30m'
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = '\033[35m'
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    @staticmethod
    def black(text):
        return f"{Color.BLACK}{text}{Color.RESET}"

    @staticmethod
    def red(text):
        return f"{Color.RED}{text}{Color.RESET}"

    @staticmethod
    def green(text):
        return f"{Color.GREEN}{text}{Color.RESET}"

    @staticmethod
    def yellow(text):
        return f"{Color.YELLOW}{text}{Color.RESET}"

    @staticmethod
    def blue(text):
        return f"{Color.BLUE}{text}{Color.RESET}"

    @staticmethod
    def magenta(text):
        return f"{Color.MAGENTA}{text}{Color.RESET}"

    @staticmethod
    def cyan(text):
        return f"{Color.CYAN}{text}{Color.RESET}"

    @staticmethod
    def bold(text):
        return f"{Color.BOLD}{text}{Color.RESET}"

    @staticmethod
    def hp_color(hp: int, max_hp: int) -> str:
        ratio = hp / max_hp
        if ratio > 0.5:
            return Color.green(f"{hp}/{max_hp}")
        elif ratio > 0.25:
            return Color.yellow(f"{hp}/{max_hp}")
        else:
            return Color.red(f"{hp}/{max_hp}")
