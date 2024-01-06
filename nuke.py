import sys
import subprocess
import os

# Constants
TEMPLATES_PATH = os.path.expanduser("~/nuclei-templates")
NUCLEI_PATH = os.path.expanduser("~/go/bin/nuclei")
API_KEY = ''

def check_go_installation():
    try:
        subprocess.run(["go", "version"], check=True)
    except FileNotFoundError:
        print("Go is not installed. Please install Go before running this script.")
        sys.exit(1)
    except subprocess.CalledProcessError:
        print("There was an error running Go.")
        sys.exit(1)

def write_subdomains_to_file(subdomains):
    if subdomains:
        file_name = f"{DOMAIN.replace('.', '_')}.txt"
        with open(file_name, 'w') as file:
            for subdomain in subdomains:
                file.write(f"{subdomain}.{DOMAIN}\n")
        return file_name
    else:
        print(f"No subdomains found for {DOMAIN}")
        sys.exit(1)

def write_domain_to_file():
    file_name = f"{DOMAIN.replace('.', '_')}.txt"
    with open(file_name, 'w') as file:
        file.write(DOMAIN + "\n")
    return file_name

def install_pysecuritytrails():
    try:
        import pysecuritytrails
    except ImportError:
        print(">> pysecuritytrails module is not installed. Please install it using pip <<")
        print("pip install pysecuritytrails")
        sys.exit()

def check_nuclei_installation():
    check_go_installation()
    try:
        subprocess.run([NUCLEI_PATH, "-version"], check=True)
    except FileNotFoundError:
        print("Nuclei is not installed. Installing nuclei.")
        subprocess.run(["go", "install", "-v", "github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest"], check=True)
    except subprocess.CalledProcessError:
        print("Nuclei is installed, but there was an error running it.")

def check_nuclei_templates():
    if not os.path.exists(TEMPLATES_PATH):
        print("Nuclei templates not found. Cloning the repository.")
        subprocess.run(["git", "clone", "https://github.com/projectdiscovery/nuclei-templates", TEMPLATES_PATH], check=True)

def update_nuclei_templates():
    print("Updating Nuclei templates...")
    subprocess.run([NUCLEI_PATH, "-update-templates", "-silent"], check=True)

def run_nuclei(file_name):
    print("Running Nuclei with the subdomains...")
    subprocess.run([NUCLEI_PATH, "-l", file_name, "-fr", "-uc", "-headless", "-t", TEMPLATES_PATH], check=True)

def main():
    print(f"Do not put in https:// or a trailing slash")
    DOMAIN = input(f"What is the targete like example.com or 127.0.0.1: ")
    file_name = ''
    if API_KEY:
        install_pysecuritytrails()
        from pysecuritytrails import SecurityTrails, SecurityTrailsError
        st = SecurityTrails(API_KEY)
        try:
            st.ping()
            subdomains = st.domain_subdomains(DOMAIN).get('subdomains', [])
            file_name = write_subdomains_to_file(subdomains)
        except SecurityTrailsError:
            print('Ping to SecurityTrails failed, check your API key.')
            sys.exit(1)
        except Exception as e:
            print(f"An error occurred: {e}")
            sys.exit(1)
    else:
        print("API key is not set. Running against the main domain.")
        file_name = write_domain_to_file()

    check_nuclei_installation()
    check_nuclei_templates()
    update_nuclei_templates()
    run_nuclei(file_name)

if __name__ == "__main__":
    main()
