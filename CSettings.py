import os
from dataIO import fileIO

SERVER = 'localhost'
PORT = 8833
SDP_PORT = 4095  # Server Discovery Port
SDP_ADDRESS = "239.255.4.3"

class CSettings():
    def __init__(self, object=None, server=SERVER, port=PORT, sdp_port=SDP_PORT, sdp_address=SDP_ADDRESS, filename='conf'):
        self.s = {"server":server, "port":port, "sdp":{"address":sdp_address, "port":sdp_port}}
        self.sdp = True
        self.server = server
        self.port = port
        self.sdp_port = sdp_port
        self.sdp_address = sdp_address
        self.filename = filename
        self.pre_init()
        self._init_check()
        self.post_init()

    def _init_check(self):
        if not os.path.exists("config"):
            os.makedirs("config")
            fileIO("config/{}.json".format(self.filename), "w", self.s)
        else:
            fs = fileIO("config/{}.json".format(self.filename),"r")
            # =====================
            self.file_checks(fs)
            # =====================
            self.s = fileIO("config/{}.json".format(self.filename),"r")
        if not fileIO("config/{}.json".format(self.filename), "c"):
            fileIO("config/{}.json".format(self.filename), "w", self.s)

    # === Surcharge me : ===

    def file_checks(self, fs):
        """ File checking = check according to fs (config file) if the struct match conditions """
        pass

    def pre_init(self):
        """ Pre-Init function : change variables here, also do stuff """
        pass

    def post_init(self):
        """ Post-Init function : Post file-check operations (start srcipt ...) """
        pass

    def pre_write(self):
        """ Pre-Saving function : Store variables into dict """
        pass

    # === Dont't change me : ===

    def write_config(self):
        self.pre_write()
        fileIO("config/{}.json".format(self.filename), "w", self.s)

    def get_s(self):
        return self.s
