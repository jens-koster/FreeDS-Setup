import loguru
import sys
import typing
loguru.logger.remove()  # Remove default handler
loguru.logger.add(
    sys.stderr,
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {level.icon}{message}",
    level="DEBUG"
)

loguru.logger.level("COMMENCE", no=25, color="<light-blue>", icon="🚀 ")
loguru.logger.level("START", no=20, color="<light-blue>", icon="🎬 ")
loguru.logger.level("PROGRESS", no=20, color="<white>", icon="🔄 " )
loguru.logger.level("SUCCEED", no=20, color="<green>", icon="✅ ")
loguru.logger.level("FAIL", no=20, color="<red>", icon="❌ ")
loguru.logger.level("COMPLETE", no=25, color="<green>", icon="✨ ")

loguru.logger.level("DEBUG", icon="")
loguru.logger.level("INFO", icon="")
loguru.logger.level("WARNING", icon="")
loguru.logger.level("ERROR", icon="❌ ")


class Flogger:
    """module level logger, standardize messages for tracking execution."""
    def __init__(self):
        self.logger = loguru.logger
        self.info = self.logger.info
        self.debug = self.logger.debug
        self.warning = self.logger.warning
        self.error = self.logger.error
        self.epic = ''
        self.task = ''

    def header(self, title):
        """Log message in a "box" using the FreeDS logger, a bit nicer output for starting a section of actions."""
        char = '='
        space = 5
        vert_char = char
        width = len(title) + space * 2
        self.logger.info(char * width)
        row = vert_char + " " * (space - 1) + title + " " * (space - 1) + vert_char
        self.logger.info(row)
        self.logger.info(char * width)

    def commence(self, epic, *a, **k):
        self.epic = epic
        msg = f'{epic}...'
        self.logger.opt(depth=1).log("COMMENCE", msg, *a, **k)

    def start(self, task, *a, **k):
        self.task = task
        msg = f'{task}...'
        self.logger.opt(depth=1).log("START", msg, *a, **k)

    def progress(self, msg, *a, **k):
        self.logger.opt(depth=1).log("PROGRESS", msg, *a, **k)
    def succeed(self, *a, **k):
        msg = f'{self.task} succeeded'
        self.logger.opt(depth=1).log("SUCCEED", msg, *a, **k)

    def fail(self, *a, **k):
        msg = f'{self.epic} -> {self.task}: failed'
        self.logger.opt(depth=1).log("FAIL", msg, *a, **k)

    def complete(self, *a, **k):
        msg = f'{self.epic} completed.'
        self.logger.opt(depth=1).log("COMPLETE", msg, *a, **k)

logger = Flogger()

if __name__ == '__main__':
    logger.commence("Initialize Freeds")
    logger.start("Cloning repos")
    logger.debug('debug')
    logger.info('info')
    logger.warning('warning')
    logger.error('error')
    logger.succeed()
    logger.fail()
    logger.complete()