import _base
from components.html5lib.sanitizer import HTMLSanitizerMixin

class Filter(_base.Filter, HTMLSanitizerMixin):
    def __iter__(self):
        for token in _base.Filter.__iter__(self):
            token = self.sanitize_token(token)
            if token: yield token
