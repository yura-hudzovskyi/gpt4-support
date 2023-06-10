import csv
from django.shortcuts import render

from supporter.utils import main


def organizations(request):
    if request.method == 'POST':
        main()
        # Example code to read the CSV file and store the data in a list
        organizations = []
        with open('organizations.csv', 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                organizations.append(row)

        # Pass the organizations data to the template
        return render(request, 'index.html', {'organizations': organizations})

    return render(request, 'index.html')
