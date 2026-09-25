class Read:
    def __init__(self, share_data):
        self.share_data = share_data

    def Read_QR(self, qr_data):
        share_block = []
        share_list = []
        data = qr_data.split('\n')

        file_path = data[0]
        share_strength = int(data[1])
        threshold = int(data[2])
        ramp = int(data[3])
        secret_length = int(data[4])
        data_index = 5

        for i in range(share_strength):
            share_index = int(data[data_index])
            data_index += 1
            data_length = int(data[data_index])
            data_index += 1
            share_list.append(share_index)

            for j in range(data_length):
                share_block.append(int(data[data_index]))
                data_index += 1

            share_list.append(share_block)
            share_block = []
            self.share_data.append(share_list)
            share_list = []

        return threshold, ramp, secret_length, file_path