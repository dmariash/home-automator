import wiringpi
import argparse

wiringpi.wiringPiSetup()


class PlugSender(object):

    PULSE_WIDTH = 450

    PLUGS = {
        1: {1: 859124533, 2: 861090613, 3: 892547893, 4: 1395864373},
        2: {1: 859124563, 2: 861090643, 3: 892547923, 4: 1395864403},
        3: {1: 859125043, 2: 861091123, 3: 892548403, 4: 1395864883},
        4: {1: 859132723, 2: 861098803, 3: 892556083, 4: 1395872563}
    }

    STATES = {'on': 13107, 'off': 21299}

    def __init__(self, pin, repeat=10):
        self.pin = pin
        self.repeat = repeat
        wiringpi.pinMode(self.pin, wiringpi.OUTPUT)

    def send(self, channel, button, state):
        bin_list = self.command_as_bin_list(channel, button, state)
        packet = self.encode_packet(bin_list)
        for _ in range(self.repeat):
            for bit in packet:
                wiringpi.digitalWrite(self.pin, bit)
                wiringpi.delayMicroseconds(self.PULSE_WIDTH)


    def encode_packet(self, bin_list):
        preamble = [0] * 26
        sync = [1]
        postamble = [0] * 2
        return preamble + sync + self.encode_as_state_list(bin_list) + postamble

    def command_as_bin_list(self, channel, button, state):
        plug_code = self.int_to_bin_list(self.PLUGS[channel][button], 32)
        state_code = self.int_to_bin_list(self.STATES[state], 16)
        return  plug_code + state_code

    def encode_as_state_list(self, bin_list):
        result = []
        state = 0
        for bin in bin_list:
            result.extend([state] if bin == 0 else [state] * 3)
            state = 1 - state
        return result

    def int_to_bin_list(self, dec, length):
        """Returns back a list of binary values."""
        max_dec = int('1' * length, 2)
        if dec <= max_dec:
            bin_temp = [int(x) for x in list('{0:0b}'.format(dec))]
            bin_list = [0] * (length - len(bin_temp)) + bin_temp
            return bin_list[::-1]
        else:
            return [0] * length

def send(pin, channel, button, state):
    plugsender = PlugSender(pin)
    plugsender.send(channel, button, state)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--pin', type=int, default=0)
    parser.add_argument('-c', '--channel', type=int, default=1)
    parser.add_argument('-b', '--button', type=int, default=1)
    parser.add_argument('-s', '--state', default='on')
    args = parser.parse_args()

    send(args.pin, args.channel, args.button, args.state)
