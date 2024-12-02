# urlchk
URL health checker
    
    usage: urlchk.py [-h] [-cm CONTENT_MATCH] [-cf CONTENT_FAIL] [-sm STATUS_MATCH] [-sf STATUS_FAIL] -u URL [-t TIMEOUT] [-v] [-k] [-r RETRIES]
    
    options:
      -h, --help            show this help message and exit
      -cm CONTENT_MATCH, --content-match CONTENT_MATCH
                            Regex to required to match in response content
      -cf CONTENT_FAIL, --content-fail CONTENT_FAIL
                            Regex to fail if found in response content
      -sm STATUS_MATCH, --status-match STATUS_MATCH
                            Comma delimited list of acceptable HTTP status codes
      -sf STATUS_FAIL, --status-fail STATUS_FAIL
                            Comma delimited list of HTTP status codes to fail on
      -u URL, --url URL     URL of the site to check
      -t TIMEOUT, --timeout TIMEOUT
                            Timeout in seconds (default 10)
      -v, --verbose         Verbose output
      -k, --insecure        Skip SSL verification
      -r RETRIES, --retries RETRIES
                            Number of times to retry connection (default 2)
