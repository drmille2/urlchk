#!/usr/bin/env python
import argparse
import requests
import re
import sys

parser = argparse.ArgumentParser()
parser.add_argument('-cm', '--content-match', help='Regex to required to match in response content')
parser.add_argument('-cf', '--content-fail', help='Regex to fail if found in response content')
parser.add_argument('-sm', '--status-match', help='Comma delimited list of acceptable HTTP status codes')
parser.add_argument('-sf', '--status-fail', help='Comma delimited list of HTTP status codes to fail on')
parser.add_argument('-u', '--url', required=True, help='URL of the site to check')
parser.add_argument('-t', '--timeout', default=10, type=float, help='Timeout in seconds (default 10)')
parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
parser.add_argument('-k', '--insecure', default=True, action='store_false', help='Skip SSL verification')
parser.add_argument('-r', '--retries', default=2, type=int, help='Number of times to retry connection (default 2)')

args = parser.parse_args()

def check_content(c):
	out = [0,""]

	if args.content_fail is not None:
		expr = re.compile(args.content_fail)
		match = expr.findall(c)
		mIter = expr.finditer(c)
		if match != []:
			out[0] = 1
			out[1] = "\tContent fail-check failed, matches for pattern {} found at coordinates:\n\n".format(args.content_fail)
			for m in mIter:
				out[1] = out[1]+"{}: {}\n".format(m.group(),m.span())
		else:
			out[0] = 0
			out[1] = "\tContent fail-check succeeded, matches for pattern {} not-found.\n".format(args.content_fail)
		if out[0] == 1:
			return out


	if args.content_match is not None:
		expr = re.compile(args.content_match)
		match = expr.findall(c)
		mIter = expr.finditer(c)
		if match != []:
			out[0] = 0
			out[1] = out[1]+"\tContent match-check succeeded, matches for pattern {} found at coordinates:\n\n".format(args.content_match)
			for m in mIter:
				out[1] = out[1]+"{}: {}\n".format(m.group(),m.span())
		else:
			out[0] = 1
			out[1] = out[1]+"\tContent match-check failed, matches for pattern {} not-found.\n\tResponse contained below:\n\n{}".format(args.content_match,c)

	return out

def check_status(r):
	out = [0,""]

	if args.status_fail is not None:
		badCodes = []
		for c in args.status_fail.split(','):
			if c != '':
				badCodes.append(int(c.strip()))
		if r in badCodes:
			out[0] = 1
			out[1] = "\tStatus fail-check failed, code {} matched in failure status code list {}\n".format(r, badCodes)
			return out
		else:
			out[0] = 0
			out[1] = "\tStatus fail-check succeeded, code {} not-matched in failure status code list {}\n".format(r, badCodes)

	if args.status_match is not None:
		goodCodes = []
		for c in args.status_match.split(','):
			if c != '':
				goodCodes.append(int(c.strip()))
		if r in goodCodes:
			out[0] = 0
			out[1] = out[1]+"\tStatus match-check succeeded, code {} matched in successful status code list {}\n".format(r,goodCodes)
		else:
			out[0] = 1
			out[1] = out[1]+"\tStatus match-check failed, code {} not-matched in successful status code list {}\n".format(r,goodCodes)

	return out


def main():
	out, att = 0, 0
	err = False
	
	while att <= args.retries:
		err = False
		try:
			r = requests.get(args.url, timeout=args.timeout, verify=args.insecure)
		except Exception:
			err = True
			err_detail = sys.exc_info()
		if not err:
			break
		else:
			att = att+1
	if err:
		if err_detail[0] == requests.exceptions.ConnectTimeout:
			print("URL Check for {} failed with read timeout after {} seconds ({} retries).".format(args.url, \
																									args.timeout, \
																									args.retries))
			sys.exit(1)
		elif err_detail[0] == requests.exceptions.ConnectionError:
			print("URL Check for {} failed with connection error ({} retries).".format(args.url, \
																					   args.retries))
			sys.exit(1)
		else:
			print("URL Check for {} failed with error message {} ({} retries).".format(args.url, \
																				       err_detail[0].__doc__,
																					   args.retries))
			sys.exit(1)

	if args.status_match is not None or args.status_fail is not None:
		status_out = check_status(r.status_code)
		if status_out[0] == 0:
			print("Status check for {} successful.".format(args.url))
		else:
			print("Status check for {} failed.".format(args.url))
		out = out+status_out[0]

	if args.content_match is not None or args.content_fail is not None:
		content_out = check_content(r.text)
		if content_out[0] == 0:
			print("Content check for {} successful.".format(args.url))
		else:
			print("Content check for {} failed.".format(args.url))
		out = out+content_out[0]

	if args.verbose:
		try:
			if len(content_out[1]) > 0:
				print("\nContent check details:\n{}".format(content_out[1]))
		except Exception:
			pass
		try:
			if len(status_out[1]) > 0:
				print("\nStatus check details:\n{}".format(status_out[1]))
		except Exception:
			pass

	sys.exit(out)


if __name__ == '__main__':
	main()
