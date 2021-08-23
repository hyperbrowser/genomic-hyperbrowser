from asteval import Interpreter as OrigInterpreter


class Interpreter(OrigInterpreter):
    def eval(self, expr, lineno=0, show_errors=True):
        res = OrigInterpreter.eval(self, expr, lineno=lineno, show_errors=show_errors)
        if len(self.error) > 0:
            for err in self.error:
                t, v, tb = err.exc_info
                raise t, v, tb
        return res
