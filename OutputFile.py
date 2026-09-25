class OutputFile:
    def __init__(self, number):
        self.number = number

    def number_to_binary(self):
        return self.number.to_bytes((self.number.bit_length() + 7) // 8, byteorder='big')

    def export_binary(self, file_path):
        with open(file_path, 'wb') as file:
            file.write(self.number_to_binary())

    def export_file(self, file_path):
        self.export_binary(file_path)