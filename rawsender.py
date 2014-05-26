import wiringpi
import argparse

wiringpi.wiringPiSetup()


class RawSender(object):

    PULSE_WIDTH_MAP = {1: 350, 2: 650}

    def __init__(self, pin, repeat=10, protocol=1):
        self.pin = pin
        self.protocol = protocol
        self.repeat = repeat
        self.pulse_length = self.PULSE_WIDTH_MAP[self.protocol]
        self.PULSE_MAP = {
            1: {
                0: {
                    'HIGH': 1 * self.pulse_length,
                    'LOW': 3 * self.pulse_length,
                },
                1: {
                    'HIGH': 3 * self.pulse_length,
                    'LOW': 1 * self.pulse_length,
                },
                'sync': {
                    'HIGH': 1 * self.pulse_length,
                    'LOW': 31 * self.pulse_length,
                }
            },
            2: {
                0: {
                    'HIGH': 1 * self.pulse_length,
                    'LOW': 2 * self.pulse_length,
                },
                1: {
                    'HIGH': 2 * self.pulse_length,
                    'LOW': 1 * self.pulse_length,
                },
                'sync': {
                    'HIGH': 1 * self.pulse_length,
                    'LOW': 10 * self.pulse_length,
                }
            }
        }
        wiringpi.pinMode(self.pin, wiringpi.OUTPUT)

    def send(self, code, length=32):
        """Sends the decimal code after converting to a binary list."""
        bits = self.int_to_bin_list(code, length)
        for _ in xrange(self.repeat):
            for bit in bits:
                self.transmit(bit)
            self.transmit('sync')

    def transmit(self, bit):
        """Transmits a 0, a 1, or a 'sync', as specified in the pulse_map"""
        wiringpi.digitalWrite(self.pin, wiringpi.HIGH)
        wiringpi.delayMicroseconds(self.delay(bit, 'HIGH'))
        wiringpi.digitalWrite(self.pin, wiringpi.LOW)
        wiringpi.delayMicroseconds(self.delay(bit, 'LOW'))

    def delay(self, bit, value):
        return self.PULSE_MAP[self.protocol][bit][value]

    def int_to_bin_list(self, dec, length):
        """Returns back a list of binary values."""
        max_dec = int('1' * length, 2)
        if dec <= max_dec:
            bin_temp = [int(x) for x in list('{0:0b}'.format(dec))]
            bin_list = [0] * (length - len(bin_temp)) + bin_temp
            return bin_list
        else:
            return [0] * length


def send(pin, code):
    rawsender = RawSender(pin)
    rawsender.send(code)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--pin', type=int, default=0)
    parser.add_argument('-c', '--code', type=int, default=1)
    args = parser.parse_args()

    send(args.pin, args.code)
