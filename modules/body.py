# encoding: utf-8


class Body(object):
    """ Represents a decision making body
    """
    def __init__(self, name, body_id):
        self.name = name
        self.id = body_id

    def __repr__(self):
        return (u'<Body: %s>' % (self.name)).encode('utf8')
