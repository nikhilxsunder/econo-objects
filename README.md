# econo-objects
## A simple python package for creating economic models and data objects using FRED API data.
## This package is still in beta please try it out and please report any comments, concerns, and issues.

[![Build and test GitHub](https://github.com/nikhilxsunder/econo-objects/actions/workflows/main.yml/badge.svg)](https://github.com/nikhilxsunder/econo-objects/actions)
[![PyPI version](https://img.shields.io/pypi/v/econo-objects.svg)](https://pypi.org/project/econo-objects/)
[![Downloads](https://img.shields.io/pypi/dm/econo-objects.svg)](https://pypi.org/project/econo-objects/)

### Latest Update

- First prerelease version published

### Installation

You can install the package using pip:

```sh
pip install econo-objects
```

### Package Usage

I recommend consulting the offical Binance US API documentation at: 
https://econo-objects.readthedocs.io/en/latest/

Here is a simple example of how to use the package:

```python
# Imports
from econo_objects import FredObject

# Set API Key
Keys.set_fred_api_key("your_api_key_here")

# Initialize Fred Object
fred_obj = FredObject("GDP", "2020-01-01", "2023-01-01")

# Plot GDP
plot = fred_obj.plot_df
```

### Important Notes

- Store your API keys and secrets in environment variables or set directly.
- Do not hardcode your API keys and secrets in your scripts.

### Features

- Easy plotting through predefinned methods
- Data output is already in pandas DataFrame format

## Next Update 

- More Calculations and Models

### Contributing

Contributions are welcome! Please open an issue or submit a pull request.

### License

This project is licensed under the GNU Affero General Public License v3.0 - see the [LICENSE](LICENSE) file for details.