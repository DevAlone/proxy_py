class Proxy:
    def __init__(self, protocols, domain, port):
        self.protocols = protocols
        self.domain = domain
        self.port = port

    domain = ""
    port = 0
    protocols = []

    lastCheckedTime = 0
    checkingPeriod = 60 * 5
    lastCheckResult = True
    numberOfBadChecks = 0

    def toUrl(self, protocol=None):
        if protocol is None:
            if len(self.protocols) > 0:
                result = self.protocols[0]
            else:
                result = "http"
        else:
            result = protocol
        result += "://" + self.domain + ":" + self.port
        return result

    def __eq__(self, other):
        return self.protocols == other.protocols and \
               self.domain == other.domain and \
               self.port == other.port

    def __hash__(self):
        return hash((self.domain, self.port))
