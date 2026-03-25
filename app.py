from flask import Flask, render_template_string, request
import toolforge

import unicodedata

app = Flask(__name__)



SQL_QUERY = """
 SELECT actor_name, COUNT(fr_id) AS cnt
        FROM linktarget
        JOIN categorylinks ON lt_id = cl_target_id
        JOIN page ON cl_from = page_id
        JOIN file ON page_title = file_name
        JOIN filerevision ON fr_id = file_latest
        JOIN actor ON fr_actor = actor_id
        WHERE lt_namespace = 14 
            AND lt_title = %s
        GROUP BY actor_id
        ORDER BY cnt DESC
"""

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Uploaders in Category</title>
</head>
<body>
    <form method="post" action="/">
        <label for="category">Enter Category Name:</label>
        <input type="text" id="category" name="category" required>
        <button type="submit">Submit</button>
    </form>
   {% if uploaders|length > 0 %}
    <h1>Uploaders in Category: {{ category }}</h1>
    <h2>Total Uploads: {{ upload_count }}</h2>
    
   
    <table border="1">
        <tr>
            <th>Uploader</th>
            <th>Number of Files</th>
        </tr>
        {% for uploader in uploaders %}
        <tr>
            <td>{{ uploader[0] }}</td>
            <td>{{ uploader[1] }}</td>
        </tr>
        {% endfor %}
    </table>
   {% endif %}
</body>
</html>
"""
def normalize_category_name(category_name : str):
    # Capitalize first letter, replace spaces with _, NFC normalization
    name = category_name.strip().replace(' ', '_')
    # Use str.title() for locale-aware capitalization (handles multibyte)
    name = name.title() if name else name
    name = unicodedata.normalize('NFC', name)
    return name

def get_uploaders_in_category(category_name):
    norm_category = normalize_category_name(category_name)
    conn = toolforge.connect('commonswiki')
    uploaders = []
    upload_count = 0
    with conn.cursor() as cursor:
        cursor.execute(SQL_QUERY, (norm_category,))
        for row in cursor.fetchall():
            uploaders.append((row[0], row[1]))
            upload_count += row[1]
        return uploaders, upload_count

@app.route('/', methods=['GET', 'POST'])
def index():
    uploaders = []
    upload_count = 0
    category = ""
    if request.method == 'POST':
        category = request.form['category']
        uploaders_raw = get_uploaders_in_category(category)
        uploaders, upload_count = uploaders_raw
        print(uploaders)
    return render_template_string(HTML_TEMPLATE, 
                                  uploaders=uploaders, category=category, upload_count=upload_count)