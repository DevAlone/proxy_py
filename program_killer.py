import signal


class ProgramKiller:
    kill = False
    killingAttempts = 0

    def __init__(self):
        signal.signal(signal.SIGINT, self.set_kill_flag)
        signal.signal(signal.SIGTERM, self.set_kill_flag)

    def set_kill_flag(self, signum, frame):
        self.kill = True
        self.killingAttempts += 1
        if self.killingAttempts >= 2:
            exit(1)
