"""
Service exception are raised by services
"""


class ServiceException(Exception):
    def __init__(self, code, message):
        Exception(code, ":", message)
        self.code = code
        self.message = message

    def __str__(self):
        return "{}:{}".format(self.code, self.message)

    def to_dict(self):
        return {"error_code": self.code, "error_message": self.message}


class ExtractionError(Exception):
    pass


class NoResultException(Exception):
    pass


class InvalidBSNException(Exception):
    pass


messages = {
    "000": "Onbekende fout",
}


def onbekende_fout():
    return ServiceException("000", messages["000"])
