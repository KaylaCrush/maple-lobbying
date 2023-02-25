import requests
########################
# Misc Utility Methods #
########################

def pull_html(url):
    headers={"User-Agent": "Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148"}
    result = requests.get(url, headers=headers)
    result.raise_for_status()
    return result.content

# Equivalent to converting to a set and back, but it preserves list order
def unique_values(sequence):
    seen = set()
    return [x for x in sequence if x not in seen and not seen.add(x)]

# Returns values of new_sequence that don't appear in old_sequence.
# This is so I only process new urls when I scrape recent reports
def new_values(new_sequence, old_sequence):
    return [x for x in new_sequence if x not in old_sequence]
