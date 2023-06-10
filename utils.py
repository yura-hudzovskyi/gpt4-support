import csv

def compare_csv_files(file1, file2, output_file):
    # Read data from file1
    data1 = set()
    with open(file1, 'r') as csvfile1:
        reader = csv.reader(csvfile1)
        next(reader)  # Skip header row
        for row in reader:
            data1.add(row[1])  # Assuming the link is in the second column (index 1)

    # Read data from file2 and compare with data1
    unique_data = set()
    with open(file2, 'r') as csvfile2:
        reader = csv.reader(csvfile2)
        next(reader)  # Skip header row
        for row in reader:
            link = row[1]  # Assuming the link is in the second column (index 1)
            if link not in data1:
                unique_data.add(link)

    # Write unique data to output file
    with open(output_file, 'w', newline='') as csvfile_out:
        writer = csv.writer(csvfile_out)
        writer.writerow(['Organization', 'Website', 'Contact', 'Focus Area'])  # Header row
        for link in unique_data:
            writer.writerow(['', link, '', ''])

# Usage example:
file1 = ""
file2 = 'file2.csv'
output_file = 'unique_links.csv'

compare_csv_files(file1, file2, output_file)
