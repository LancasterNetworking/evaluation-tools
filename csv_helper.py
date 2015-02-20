import csv

"""Data should be in the form [{}, ]"""
def write_data(csv_file_name, data):
    if len(data) > 0:
        with open(csv_file_name, 'wb') as f:
            w = csv.DictWriter(f, fieldnames=data[0].keys())
            w.writeheader()
            for d in data:
                w.writerow(d)
        return csv_file_name
    else:
        return None
