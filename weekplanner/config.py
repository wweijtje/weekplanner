def all_event_keywords(config, category="events"):
    all_keywords = ''
    for _e in config[category]:
        _c = config[category][_e]
        all_keywords += ''.join(_c['keywords'])
    all_keywords = all_keywords.lower().replace(' ','')
    return all_keywords


def find_event(event_name, config, category="events"):

    if event_name.lower().replace(' ','') in all_event_keywords(config=config, category=category):
        for _e in config[category]:
            _c = config[category][_e]
            if event_name.lower().replace(' ','') in ''.join(_c['keywords']).lower().replace(' ',''):
                return _c, _e
    else:
        return None
