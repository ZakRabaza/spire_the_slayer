class Color:
    RESET = "\033[0m"
    BOLD = "\033[1m"

    # text colors
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # bright variants
    BRED = "\033[91m"
    BGREEN = "\033[92m"
    BYELLOW = "\033[93m"
    BBLUE = "\033[94m"
    BCYAN = "\033[96m"

    @staticmethod
    def red(text):    return f"\033[31m{text}\033[0m"

    @staticmethod
    def green(text):  return f"\033[32m{text}\033[0m"

    @staticmethod
    def yellow(text): return f"\033[33m{text}\033[0m"

    @staticmethod
    def blue(text):   return f"\033[34m{text}\033[0m"

    @staticmethod
    def cyan(text):   return f"\033[36m{text}\033[0m"

    @staticmethod
    def bold(text):   return f"\033[1m{text}\033[0m"

    @staticmethod
    def hp_color(hp: int, max_hp: int) -> str:
        ratio = hp / max_hp
        if ratio > 0.5:
            return Color.green(f"{hp}/{max_hp}")
        elif ratio > 0.25:
            return Color.yellow(f"{hp}/{max_hp}")
        else:
            return Color.red(f"{hp}/{max_hp}")
