from flask import Flask, render_template_string, request
from main import get_uploaders_in_category
app = Flask(__name__)


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Uploaders in Category</title>
    <script>
    function submitCategory(e) {
        e.preventDefault();
        const categoryInput = document.getElementById('category');
        const category = categoryInput.value.trim();
        if (category) {
            window.location.href = `/${encodeURIComponent(category)}`;
        } else {
            alert('Please enter a category name.');
        }
    }
    </script>
</head>
<body>
    <form method="post" action="/" onsubmit="submitCategory(event)">

        <label for="category">Enter Category Name (Without Category: prefix):</label>
        <input type="text" id="category" 
            name="category"
            required value="{{ category }}" 
            placeholder="e.g. Images from Wiki Loves Folklore 2026"
        />
        <button type="submit">Submit</button>
    </form>
   {% if uploaders %}
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
                                  uploaders=uploaders, 
                                  category=category, 
                                  upload_count=upload_count)

@app.route('/{category}', methods=['GET', 'POST'])
def category(category):
    uploaders , upload_count = get_uploaders_in_category(category)
    return render_template_string(HTML_TEMPLATE, 
                                  uploaders=uploaders, 
                                  category=category, 
                                  upload_count=upload_count)