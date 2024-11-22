import csv
import subprocess
import logging

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S"
)

def dig_query(domain, record_type):
    """Run a dig query for a specific record type."""
    logging.info(f"Querying {record_type} record for domain: {domain}")
    try:
        result = subprocess.run(
            ['dig', '+short', record_type, domain],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode == 0:
            response = result.stdout.strip()
            logging.info(f"{record_type} record for {domain}: {response}")
            return response.splitlines()[0] if response else None
        else:
            logging.error(f"Error querying {record_type} record for {domain}: {result.stderr.strip()}")
            return None
    except Exception as e:
        logging.error(f"Exception during dig query for {domain}: {str(e)}")
        return None

def normalize_domain(domain):
    """Remove the trailing dot from a domain, if present."""
    return domain.rstrip('.') if domain else domain

def resolve_cname_chain(domain, max_depth=5):
    """Recursively resolve CNAME chains until an A record is found."""
    current_domain = normalize_domain(domain)
    for depth in range(max_depth):
        logging.info(f"Resolving CNAME for: {current_domain} (Depth: {depth + 1})")
        cname_result = dig_query(current_domain, "CNAME")
        if not cname_result:
            logging.info(f"No further CNAME found for: {current_domain}")
            return current_domain  # Likely an A record
        current_domain = normalize_domain(cname_result)
    logging.warning(f"CNAME chain exceeded max depth for: {domain}")
    return None

def resolve_ip(domain):
    """Resolve the domain to an IP address."""
    logging.info(f"Resolving IP for domain: {domain}")
    return dig_query(domain, "A")

def check_http_status(domain, timeout=10):
    """Check HTTP status for the domain."""
    domain = normalize_domain(domain)
    logging.info(f"Checking HTTP status for domain: {domain}")
    try:
        response = subprocess.run(
            ['curl', '-Is', '--max-time', str(timeout), domain],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if response.returncode == 0:
            status_line = response.stdout.splitlines()[0]
            logging.info(f"HTTP status for {domain}: {status_line}")
            return status_line
        else:
            logging.error(f"HTTP error for {domain}: Return code {response.returncode}")
            return f"HTTP error {response.returncode}"
    except subprocess.TimeoutExpired:
        logging.error(f"HTTP request for {domain} timed out")
        return "Timeout"
    except Exception as e:
        logging.error(f"HTTP check failed for {domain}: {str(e)}")
        return "HTTP check failed"

def process_csv(input_file, output_file):
    """Process the input CSV file and write the results to an output CSV file."""
    with open(input_file, mode='r', newline='', encoding='utf-8') as infile, \
         open(output_file, mode='w', newline='', encoding='utf-8') as outfile:
        
        reader = csv.DictReader(infile)
        fieldnames = ["FQDN", "Canonical_Name", "CNAME", "Resolved IP", "HTTP Status"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for row in reader:
            fqdn = row.get("FQDN*")
            canonical_name = row.get("Canonical_Name*")
            
            logging.info(f"Processing FQDN: {fqdn}, Canonical Name: {canonical_name}")
            
            # Step 1: Resolve CNAME Chain
            resolved_cname = resolve_cname_chain(canonical_name)
            
            # Step 2: Resolve Target Domain to an IP
            resolved_ip = resolve_ip(resolved_cname) if resolved_cname else "No valid resolution"
            
            # Step 3: Check HTTP Status
            http_status = check_http_status(resolved_cname) if resolved_cname else "No HTTP check (invalid resolution)"
            
            writer.writerow({
                "FQDN": fqdn,
                "Canonical_Name": canonical_name,
                "CNAME": resolved_cname if resolved_cname else "No valid CNAME record",
                "Resolved IP": resolved_ip,
                "HTTP Status": http_status
            })
            logging.info(f"Finished processing {fqdn}")

if __name__ == "__main__":
    input_csv = "input.csv"  # Replace with your input file path
    output_csv = "output.csv"  # Replace with your desired output file path
    logging.info("Starting processing of the input CSV file...")
    process_csv(input_csv, output_csv)
    logging.info("Processing completed. Results written to the output CSV file.")
