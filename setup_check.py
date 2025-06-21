import sys
import os
import pkg_resources

# Expected directory structure
EXPECTED_STRUCTURE = {
    'main.py': 'file',
    'models': {
        'BinomialTree.py': 'file',
        'BlackScholes.py': 'file',
        'ImpliedVolatility.py': 'file',
    },
    'plots': {
        'utility.py': 'file',
    }
}

# Required packages
required_packages = [
    'streamlit',
    'numpy',
    'pandas',
    'scipy',
    'matplotlib',
    'plotly',
    'yfinance'
]

def check_structure(root, structure):
    """Recursively check directory structure matches expected."""
    for name, value in structure.items():
        path = os.path.join(root, name)
        if isinstance(value, dict):
            if not os.path.exists(path):
                print(f"✖ Directory missing: {path}")
                return False
            if not os.path.isdir(path):
                print(f"✖ Expected directory, found file: {path}")
                return False
            if not check_structure(path, value):
                return False
        elif value == 'file':
            if not os.path.exists(path):
                print(f"✖ File missing: {path}")
                return False
            if not os.path.isfile(path):
                print(f"✖ Expected file, found directory: {path}")
                return False
    return True

print("Checking required packages...")
missing = []
for package in required_packages:
    try:
        pkg_resources.require(package)
        print(f"✔ {package} is installed.")
    except pkg_resources.DistributionNotFound:
        missing.append(package)
        print(f"✖ {package} is NOT installed.")

if missing:
    print("\nThe following packages are missing:")
    for pkg in missing:
        print(f" - {pkg}")
    print("\nInstall them using:")
    print("pip install " + " ".join(missing))
else:
    print("\nAll required packages are installed!")

print("\nChecking directory structure...")
if check_structure('.', EXPECTED_STRUCTURE):
    print("\n✔ Directory structure is correct!")
else:
    print("\n✖ Directory structure is incorrect! Please check the output above.")
