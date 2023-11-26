

def remove(data):
    new_data = []
    for r in data:
        r.pop("objectID")
        new_data.append(r)
    return new_data
