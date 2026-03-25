from flask import Flask, render_template_string, request
import toolforge

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
      AND lt_title = ?
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
   {% if len(uploaders) > 0 %}
    <h1>Uploaders in Category: {{ category }}</h1>
    
   
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
def get_uploaders_in_category(category_name):
    conn = toolforge.connect('commonswiki')
    with conn.cursor() as cursor:
        cursor.execute(SQL_QUERY, (category_name,))
        results = cursor.fetchall()
        return results

@app.route('/', methods=['GET', 'POST'])
def index():
    uploaders = []
    category = ""
    if request.method == 'POST':
        category = request.form['category']
        uploaders_raw = get_uploaders_in_category(category)
        uploaders = [(row[0], row[1]) for row in uploaders_raw]
        print(uploaders)
    return render_template_string(HTML_TEMPLATE, uploaders=uploaders, category=category)