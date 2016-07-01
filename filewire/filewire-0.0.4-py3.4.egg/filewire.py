from filewire import send, recv
import sys
import argparse

def main():
	print("hello")
	parser = argparse.ArgumentParser(description="Sends or receives file over LAN.")
	parser.add_argument("-v", "--verbose", help="prints verbose output", action="store_true")
	subparsers = parser.add_subparsers(help="selection", dest="selection")
	parser_send = subparsers.add_parser("send", help="sends file", aliases=["s"])
	parser_send.add_argument("ip", type=str)
	parser_send.add_argument("file", type=str)
	parser_recv = subparsers.add_parser("recv", help="receives file", aliases=["r"])

	args = parser.parse_args()

	if args.selection == "recv":
		with recv.Receiver(verbose=args.verbose) as receiver:
			receiver.run()
	elif args.selection == "send":
		with send.Sender(args.ip, args.file, verbose=args.verbose) as sender:
			sender.run()

if __name__ == "__main__":
	main()
