import struct
import socket


class TCPPacket:
    def __init__(self, src, dest, seq, ack_num=0, data=b''):
        self.src = src
        self.dest = dest
        self.seq = seq
        self.ack_num = ack_num
        self.data_offset = 5
        self.reserved = 0
        self.urg = 0
        self.ack = 0
        self.psh = 0
        self.rst = 0
        self.syn = 0
        self.fin = 0
        self.window = 0xFFFF
        self.check = 0
        self.urgent = 0
        self.options = []
        self.data = data

    @classmethod
    def unpack(cls, data, src_addr, dest_addr):
        """
        Unpack received data in bytes and create a TCP packet
        """
        header = struct.unpack("!HHLL2sHHH", data[0:20])
        src_port = header[0]
        dest_port = header[1]
        seq = header[2]
        ack_num = header[3]
        dataoffset_reserved_flags = int.from_bytes(header[4], 'big')
        window = header[5]
        check = header[6]
        urgent_ptr = header[7]

        data_offset = dataoffset_reserved_flags >> 12
        reserved = (dataoffset_reserved_flags >> 6) & 0b111111

        flags = dataoffset_reserved_flags & 0b111111
        urg = (flags & 0x20) >> 5
        ack = (flags & 0x10) >> 4
        psh = (flags & 0x08) >> 3
        rst = (flags & 0x04) >> 2
        syn = (flags & 0x02) >> 1
        fin = flags & 0x01

        packet = cls((src_addr, src_port), (dest_addr, dest_port), seq, ack_num, b'')
        packet.data_offset = data_offset
        packet.reserved = reserved
        packet.urg = urg
        packet.ack = ack
        packet.psh = psh
        packet.rst = rst
        packet.syn = syn
        packet.fin = fin
        packet.window = window
        packet.check = check
        packet.urgent = urgent_ptr

        packet.set_options(data[20: data_offset * 4])
        packet.data = data[data_offset * 4:]

        packet.bytes = data

        return packet

    @property
    def flags(self):
        """
        Convert the flags to a single int.
        """
        flags = self.fin + (self.syn << 1) + (self.rst << 2) + (self.psh << 3) + (self.ack << 4) + (self.urg << 5)
        return flags

    def set_options(self, bytes):
        """
        Set options from bytes
        """
        options = []
        index = 0
        offset_bytes = 4 * (self.data_offset - 5)
        while index < offset_bytes:
            byte = bytes[index]
            if byte == 0 or byte == 1:
                options.append({'kind': byte})
                index += 1
                break
            elif byte == 2:
                length = bytes[index + 1]
                value = int.from_bytes(bytes[index + 2: index + length], 'big')
                option = {'kind': 2, 'length': length, 'value': value}
                options.append(option)
                index += 2 + length
            else:
                pass
        self.options = options

    def convert_options(self):
        """
        Convert the options to bytes
        """
        if self.data_offset == 5:
            return b''

        options = b''
        for option in self.options:
            if option['kind'] == 0:
                options += b'\x00'
            elif option['kind'] == 1:
                options += b'\x01'
            elif option['kind'] == 2:
                l = option['length']
                options += b'\x02' + l.build(1, 'big') + option['value'].build(l - 2, 'big')

        # Add padding to reach a multiple of 4 bytes
        pad_size = 4 - len(options) % 4
        options += (0).to_bytes(pad_size, 'big')

        return options

    @property
    def pseudo_header(self):
        """
        Construct the pseudo-header used in the checksum.
        :return: the pseudo-header
        """
        return struct.pack("!4s4sBBH",
                           socket.inet_aton(self.src[0]),
                           socket.inet_aton(self.dest[0]),
                           0, 6, len(self))

    def build(self):
        """
        The main purpose of this class.
        :return: Bytes to send over the network.
        """
        dataoffset_reserved_flags = 0
        dataoffset_reserved_flags = dataoffset_reserved_flags | ((self.data_offset & 0b1111) << 12)
        dataoffset_reserved_flags = dataoffset_reserved_flags | (self.flags & 0b111111)
        dataoffset_reserved_flags = dataoffset_reserved_flags.to_bytes(2, 'big')

        header = struct.pack('!HHLL2sHHH', self.src[1], self.dest[1], self.seq, self.ack_num, dataoffset_reserved_flags,
                             self.window, self.check, self.urgent)

        return header + self.convert_options() + self.data

    def checksum(self):
        """
        calculate and set checksum of the packet
        """
        pseudo_header = struct.pack("!4s4sBBH", socket.inet_aton(self.src[0]), socket.inet_aton(self.dest[0]), 0, 6,
                                    self.data_offset * 4 + len(self.data))
        check = 0
        bytes = pseudo_header + self.build()
        bytes_length = len(bytes)
        i = 0

        while bytes_length > 1:
            # Add all the shorts together
            b = bytes[i:i + 2]
            val = int.from_bytes(b, 'big')
            check += val
            bytes_length -= 2
            i += 2

        if bytes_length > 0:
            # Add the last odd byte if there is one
            check += bytes[i] << 8

        check = (check >> 16) + (check & 0xffff)
        check += check >> 16

        # Flip the sum
        check = ~check & 0xffff
        self.check = check