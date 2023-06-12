import csv

from django.middleware.csrf import get_token
from django.shortcuts import render, redirect
from supporter.utils import main, generate_message


from django.template import Template, Context


def generate_html_table(request):
    organizations = []
    with open('organizations.csv', 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            organizations.append(row)

    # Generate the HTML table
    html = '''  
              <table>
                <tr>
                  <th>Organization Name</th>
                  <th>Website</th>
                  <th>Contact Information</th>
                  <th>Specialization</th>
                  <th>Score</th>
                  <th>Make Message</th>
                </tr>
            '''

    for org in organizations:
        template = Template('''
                   <tr>
                     <td>{{ org_name }}</td>
                     <td><a href="{{ website }}">{{ website }}</a></td>
                     <td>{{ contact_info }}</td>
                     <td>{{ specialization }}</td>
                     <td>{{ score }}</td>
                     <td><a href="/generate_message/{{ org_name }}/{{ specialization }}" target="_blank">Make Message</a></td>
                   </tr>
                   ''')

        context = Context({
            'org_name': org['Organization Name'],
            'website': org['Website'],
            'contact_info': org['Contact Information'],
            'specialization': org['Specialization'],
            'score': org['Relevance Score'],
            'csrf_token': get_token(request),
        })

        html += template.render(context)

    html += '''
                 </table>
               </body>
               </html>
               '''

    return html


def organizations(request):
    if request.method == 'POST':
        main()
        table = generate_html_table(request)

        # Pass the HTML table to the template
        return render(request, 'index.html', {'html_table': table, 'message': None})

    return render(request, 'index.html')


def generate_and_display_message(request, company_name, specialization):
    if request.method == 'GET':
        message = generate_message(company_name, specialization)
        paragraphs = message.split("\n")

        # Pass the paragraphs to the template
        return render(request, 'message.html', {'paragraphs': paragraphs, "org_name": company_name})
    return redirect('supporter:organizations')
