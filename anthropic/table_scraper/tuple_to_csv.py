import csv
from io import StringIO

def tuples_to_csv_string(tuple_list):
    # Create a string buffer to hold the CSV data
    output = StringIO()
    
    # Create a CSV writer object
    csv_writer = csv.writer(output)
    
    # Write each tuple as a row in the CSV
    for row in tuple_list:
        csv_writer.writerow(row)
    
    # Get the CSV content as a string
    csv_content = output.getvalue()
    
    # Close the StringIO object
    output.close()
    
    return csv_content