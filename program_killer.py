import signal

class ProgrammKiller:
    kill = False
    killingAttempts = 0
    def __init__(self):
        signal.signal(signal.SIGINT, self.setKillFlag)
        signal.signal(signal.SIGTERM, self.setKillFlag)

    def setKillFlag(self, signum, frame):
        self.kill = True
        self.killingAttempts += 1
        if self.killingAttempts >= 3:
            exit(1)
