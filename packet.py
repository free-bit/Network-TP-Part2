from sys import argv
from hashlib import md5
# Define max allowed field sizes for each field
CHKSUM_FIELD = 16
SEQNUM_FIELD = 2
ACKNUM_FIELD = 2
PAYLEN_FIELD = 2
PAYLOAD_SIZE = 978

def packetize(seq_num, ack_num, payload_len, payload):
	# Check sizes of each input
	if(len(seq_num)!=SEQNUM_FIELD or
		 len(ack_num)!=ACKNUM_FIELD or 
		 len(payload_len)!=PAYLEN_FIELD or 
		 len(payload)>PAYLOAD_SIZE):
		print("Error in sizes")
		return None
	# Get header without the checksum
	preheader=seq_num+ack_num+payload_len
	# Convert actual length of payload from bytes to int
	pay_len_as_int=int.from_bytes(payload_len, byteorder='little')
	# Pad the end of the payload with zero if required
	padding=bytes(PAYLOAD_SIZE-pay_len_as_int)
	# Get packet without the checksum
	prepacket=preheader+payload+padding
	# Find checksum in 16 bytes
	checksum=md5(prepacket).digest()
	# Form the packet and return
	packet=checksum+prepacket
	return packet

def convertBytesOfLength(value, len):
	return value.to_bytes(len, byteorder='little')

def parsePacket(packet):
	# Get transmitted checksum
	old_chksum_bytes=packet[:CHKSUM_FIELD]
	# Get the remainder of the packet to calculate a new checksum out of it
	remainder=packet[CHKSUM_FIELD:]
	# Calculate the checksum as _hashlib.HASH object
	new_checksum=md5(remainder)
	# Calculate the checksum as bytes
	new_chksum_bytes=new_checksum.digest()
	# Compare against corruption
	if(old_chksum_bytes!=new_chksum_bytes):
		print("Packet is corrupted")
		return None
	else:
		# Calculate offsets of each field in the packet
		ack_start_offset=SEQNUM_FIELD
		plsize_start_offset=ack_start_offset+ACKNUM_FIELD
		pl_start_offset=plsize_start_offset+PAYLEN_FIELD
		# Convert bytes to human readable formats
		seq_num = int.from_bytes(remainder[:ack_start_offset], byteorder='little')
		ack_num = int.from_bytes(remainder[ack_start_offset:plsize_start_offset], byteorder='little')
		payload_len = int.from_bytes(remainder[plsize_start_offset:pl_start_offset], byteorder='little')
		# Get original payload excluding padding
		pl_end_offset=pl_start_offset+payload_len
		payload = remainder[pl_start_offset:pl_end_offset]
		# Return all of the parsed values
		return (new_checksum.hexdigest(), seq_num, ack_num, payload_len, payload)

def main(argv):
	seq_num=convertBytesOfLength(10, SEQNUM_FIELD)
	ack_num=convertBytesOfLength(10, ACKNUM_FIELD)
	payload_len=convertBytesOfLength(5, PAYLEN_FIELD)
	payload="Erkin".encode()
	packet=packetize(seq_num, ack_num, payload_len, payload)
	print(len(packet))
	print(parsePacket(packet))

if __name__ == "__main__":
    main(argv[1:])