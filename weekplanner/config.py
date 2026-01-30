def find_event(event_name, config, category="events"):
    # Normalize the input once
    search_term = event_name.lower().strip()
    for _e in config[category]:
        _c = config[category][_e]

        for _k in _c['keywords']:
            if _k.lower() in search_term:
                return _c, _e
    # Fall back, return None
    return None
