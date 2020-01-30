from pystrich.datamatrix import DataMatrixEncoder

class DataMatrixGenerator:
    def generate(self):
        encoder = DataMatrixEncoder("Hello world, this is a testing barcode.")
        return encoder.get_ascii()