# Detect Dangling CNAME Records

This script identifies and reports potential security risks associated with dangling CNAME records. It checks a list of fully qualified domain names (FQDNs) to determine if their CNAMEs point to unregistered or misconfigured resources, potentially making them vulnerable to takeover.

## Features

1. **CNAME Resolution**  
   The script resolves the CNAME records for a given list of FQDNs to their canonical names.

2. **IP Resolution**  
   For domains with valid CNAMEs, the script resolves the associated A records (IP addresses). If the CNAME chain is broken or misconfigured, it is flagged.

3. **HTTP Status Check**  
   The script checks the HTTP status of the resolved domains to identify potential risks, such as misconfigurations or unresponsive domains.

4. **Detailed Logging**  
   The script logs each step of the process to provide a clear audit trail of the checks performed.

## Prerequisites

- Python 3.7+
- Libraries: `socket`, `subprocess`, `csv`, and `requests` (if added for HTTP handling).

Install the required libraries using `pip` if necessary:
```bash
pip install requests
```

## Usage

1. **Prepare the Input CSV**  
   Create a CSV file named `input.csv` with the following columns:
   - `FQDN`: Fully Qualified Domain Name (e.g., `example.com`).
   - `Canonical_Name`: (Optional) The expected canonical name for the FQDN.

2. **Run the Script**  
   Execute the script using Python:
   ```bash
   python dangling_check.py
   ```

3. **View Results**  
   The output will be saved to a file named `results.csv`, containing the following columns:
   - `FQDN`: The original domain.
   - `Canonical_Name`: The resolved canonical name.
   - `CNAME`: Whether a valid CNAME was found.
   - `Resolved IP`: The resolved A record (IP address) if available.
   - `HTTP Status`: The HTTP response status code or error.

## Example

### Input (`input.csv`):
```csv
FQDN,Canonical_Name
cdn.example.com,
assets.example.org,static.example.com
```

### Output (`results.csv`):
```csv
FQDN,Canonical_Name,CNAME,Resolved IP,HTTP Status
cdn.example.com,,example-cdn.azureedge.net,104.21.12.34,200
assets.example.org,static.example.com,example-static.s3.amazonaws.com,52.216.20.45,404
```

## Limitations

1. **Shared IP Addresses**  
   Some shared hosting or cloud resources may return generic HTTP responses when accessed via IP instead of a proper domain.

2. **Domains without A Records**  
   Domains explicitly configured without an A record will be flagged, even if this is intentional.

3. **Timeouts and Connection Errors**  
   The script may fail for domains with slow responses or connectivity issues.

## Improvement Opportunities

### Add `Host` Header for HTTP Checks  
To handle shared hosting environments or cloud services, the script could be enhanced by including a `Host` header in HTTP requests. This would ensure the server correctly handles the request, even for shared IP addresses.

#### Example:
```python
response = requests.get(
    f'http://{resolved_ip}', 
    headers={'Host': domain},
    timeout=10
)
```

## Contributing

Contributions are welcome! Feel free to submit a pull request or open an issue for any bug fixes or feature requests.

## License

This project is licensed under the [MIT License](LICENSE).
