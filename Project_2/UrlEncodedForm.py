
import binascii
import re


def encode(string):
    """
    URL encode a string
    :param string: The string to encode
    :return: The URL encoded string
    """
    alphaNumSpace = re.compile("[a-zA-Z0-9 ]")
    string = \
        map(lambda c: "%" +
                      str(binascii.hexlify(c.encode()), "ascii") if not alphaNumSpace.match(c) else c,
            string)
    string = "".join(string)
    string = string.replace(" ", "+")
    return string


class UrlEncodedForm:
    """
    This is a model the encapsulates the formulation of a URL encoded form.
    """

    def __init__(self, values):
        """
        :param values: A dictionary of values to put in the form.
        """
        self.values = values

    def __str__(self):
        """
        Convert the form to a url encoded string.
        :return: A url encoded string containing the form data
        """
        return "&".join(["{}={}".format(encode(key),
                                        encode(self.values[key]))
                         for key in self.values])
