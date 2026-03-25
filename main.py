import toolforge

import unicodedata



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

if __name__ == "__main__":
    category = "Images from Wiki Loves Folklore 2026"
    uploaders, upload_count = get_uploaders_in_category(category)
    print(f"Uploaders in category '{category}':")
    for uploader in uploaders:
        print(f"{uploader[0]}: {uploader[1]} uploads")
    print(f"Total uploads: {upload_count}")