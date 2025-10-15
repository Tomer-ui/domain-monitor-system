import requests
from concurrent.futures import ThreadPoolExecutor
import ssl
import socket
from datetime import datetime
from logs import logger #this is our "imported" logger.

# this function show us certificate status.
def get_certificate_info(hostname: str):
    """
    Connects to a given hostname and retrieves its SSL certificate expiration info.
    returns: (status, expiry_date. issuer) in a form of a tuple.
    
    """
    logger.debug(f"Starting certificate check for {hostname}")
    try:
        context = ssl.create_default_context()
        with socket.create_connection((hostname, 443), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                issuer_info = dict(x[0] for x in cert['issuer'])
                issuer = issuer_info.get('commonName', 'N/A')

        expiry_date_str = cert['notAfter']
        expiry_date = datetime.strptime(expiry_date_str, "%b %d %H:%M:%S %Y %Z")        
    
        if expiry_date < datetime.now():
            logger.warning(f"Certificate for {hostname} has expired .")
            return 'expired', expiry_date.strftime("%Y-%m-%d"), issuer
        else:
            logger.info(f"Certificate for {hostname} is valid .")
            return 'valid', expiry_date.strftime("%Y-%m-%d"), issuer

    except socket.gaierror:
        # this error occurs if the DNS lookup fails (e.g., domain does not exist).
        # this is the cause of '[Errno 11001] getaddrinfo failed'.
        logger.error(f"DNS resolution failed for {hostname}.")
        return 'failed', 'DNS resolution failed', 'N/A'
    except ssl.SSLCertVerificationError:
        # this error occurs for SSL certificate validation issues, like a hostname mismatch.
        # this is the cause of '[SSL: CERTIFICATE_VERIFY_FAILED]...'.
        logger.error(f"SSL certificate verification failed for {hostname}.")
        return 'failed', 'SSL certificate invalid', 'N/A'
    except socket.timeout:
        # this error occurs if the connection attempt exceeds the timeout value.
        logger.error(f"Connection timed out for {hostname}.")
        return 'failed', 'Connection timed out', 'N/A'
    except ConnectionRefusedError:
        # this error occurs if the server is reachable but actively refuses the connection.
        logger.error(f"Connection refused for {hostname}.")
        return 'failed', 'Connection refused', 'N/A'
    except Exception as e:
        # a general catch-all for any other unexpected errors.
        # we log the specific error for debugging but return a generic message to the user.
        logger.error(f"An unexpected error occurred during certificate check for {hostname}: {e}")
        return 'failed', 'An unknown error occurred', 'N/A'

    
    

def check_domain_status(domain: str):
    """
    Checks the status of a single domain using HTTPS. It gets the HTTP
    status code even if the certificate is invalid, while still checking
    the certificate status separately.
           Returns:
        A dictionary containing the check results.
    """
    logger.debug(f"Starting status check for {domain}")
    result = {
        'domain': domain,
        'status_code': 'N/A',      
        'certificate_status': 'N/A',
        'certificate_expiry': 'N/A',
        'issuer': 'N/A'
    }

    try:
        # we can use verify=False to get the status code even if the certificate is invalid.
        # the separate get_certificate_info call will still give us the real certificate status.
        response = requests.get(f'https://{domain}', timeout=5, allow_redirects=True, verify=False)
        result['status_code'] = response.status_code

        # response.url.split('/')[2] is a safe way to get the final hostname after redirects.
        final_hostname = response.url.split('/')[2]
        cert_status, cert_expiry, issuer = get_certificate_info(final_hostname)
        result['certificate_status'] = cert_status
        result['certificate_expiry'] = cert_expiry
        result['issuer'] = issuer
        
    except requests.exceptions.RequestException as e:
        # this will now only catch connection errors, not SSL certificate errors.
        logger.error(f"HTTPS check for {domain} failed: {e}.")
        result['status_code'] = 'FAILED'
            
    logger.info(f"Successfully checked {domain}. Status: {result['status_code']}.")
    return result

def check_domains_concurrently(domains):
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(check_domain_status, domains))
        return results