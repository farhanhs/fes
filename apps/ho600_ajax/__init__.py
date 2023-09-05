# core.ajax
__all__ = ['views', 'AJAXForbiddenError', 'controller', 'register', 'callback', 'helper']

from ho600_ajax import views
from ho600_ajax.views import AJAXForbiddenError
from ho600_ajax.views import controller


register = controller.register
callback = controller.callback
helper = controller.helper