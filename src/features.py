# src/features.py

from urllib.parse import urlparse
import re

def extract_features(url: str) -> dict:
    """
    Convert a raw URL string into a feature dictionary
    with the SAME column names as the training dataset.
    """

    # Make sure url is a string
    if not isinstance(url, str):
        url = str(url)

    # Basic parsing (we may use later if needed)
    parsed = urlparse(url)

    # We'll count characters on the full URL string
    s = url

    # Core counts based on your dataset column names
    features = {}

    # Overall length
    features["url_length"] = len(s)

    # Character counts
    features["n_dots"] = s.count(".")
    features["n_hypens"] = s.count("-")          # note spelling: 'hypens'
    features["n_underline"] = s.count("_")
    features["n_slash"] = s.count("/")
    features["n_questionmark"] = s.count("?")
    features["n_equal"] = s.count("=")
    features["n_at"] = s.count("@")
    features["n_and"] = s.count("&")
    features["n_exclamation"] = s.count("!")
    features["n_space"] = s.count(" ")
    features["n_tilde"] = s.count("~")
    features["n_comma"] = s.count(",")
    features["n_plus"] = s.count("+")
    features["n_asterisk"] = s.count("*")
    features["n_hastag"] = s.count("#")          # note spelling: 'hastag'
    features["n_dollar"] = s.count("$")
    features["n_percent"] = s.count("%")

    # Approximation for redirection count:
    # count of '//' minus 1 (for the normal 'http://')
    double_slashes = [m.start() for m in re.finditer(r"//", s)]
    n_redirection = max(0, len(double_slashes) - 1)
    features["n_redirection"] = float(n_redirection)

    return features
