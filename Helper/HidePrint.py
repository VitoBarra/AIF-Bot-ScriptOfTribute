import os, sys

class HiddenPrints:
    _original_stdout = None
    def __init__(self):
        pass
    def __enter__(self):
        HiddenPrints.ResumePrint()

    def __exit__(self, exc_type, exc_val, exc_tb):
        HiddenPrints.ResumePrint()

    @staticmethod
    def HidePrint():
        HiddenPrints._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    @staticmethod
    def ResumePrint():
        sys.stdout.close()
        sys.stdout = HiddenPrints._original_stdout