
import toolforge
import unicodedata
from collections import Counter

# Query 1: Get file page IDs from the Commons links cluster (x4)
CATEGORY_QUERY = """
    SELECT p.page_id
    FROM categorylinks AS cl
    JOIN linktarget AS lt
        ON lt.lt_id = cl.cl_target_id
    JOIN page AS p
        ON p.page_id = cl.cl_from
    WHERE lt.lt_namespace = 14
      AND lt.lt_title = %s
      AND p.page_namespace = 6
"""

# Query 2: Get uploader information from Commons core (s4)
UPLOADER_QUERY = """
    SELECT
        a.actor_name,
        COUNT(fr.fr_id) AS cnt
    FROM page AS p
    JOIN file AS f
        ON p.page_title = f.file_name
    JOIN filerevision AS fr
        ON fr.fr_id = f.file_latest
    JOIN actor AS a
        ON fr.fr_actor = a.actor_id
    WHERE p.page_namespace = 6
      AND p.page_id IN ({placeholders})
    GROUP BY a.actor_id, a.actor_name
"""

BATCH_SIZE = 200


def normalize_category_name(category_name: str):
    category_name = category_name.strip()

    if category_name.lower().startswith("category:"):
        category_name = category_name[9:]

    category_name = category_name.replace(" ", "_")

    if not category_name:
        return ""

    # Capitalize the first character without changing other letters
    category_name = (
        category_name[0].upper() + category_name[1:]
    )

    return unicodedata.normalize("NFC", category_name)


def get_uploaders_in_category(category_name):
    norm_category = normalize_category_name(category_name)

    if not norm_category:
        return [], 0

    # Step 1: Connect to x4 to retrieve category members
    with toolforge.connect(
        "commonswiki",
        extension="links"
    ) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                CATEGORY_QUERY,
                (norm_category.encode("utf-8"),)
            )
            page_ids = [row[0] for row in cursor.fetchall()]

    print(
        f"Found {len(page_ids)} file pages "
        f"in category '{norm_category}'."
    )

    if not page_ids:
        return [], 0

    # Step 2: Connect to s4 to retrieve uploader information
    counts = Counter()

    with toolforge.connect("commonswiki") as conn:
        with conn.cursor() as cursor:

            for i in range(0, len(page_ids), BATCH_SIZE):
                batch = page_ids[i:i + BATCH_SIZE]

                placeholders = ",".join(
                    ["%s"] * len(batch)
                )

                query = UPLOADER_QUERY.format(
                    placeholders=placeholders
                )

                cursor.execute(query, batch)

                for actor_name, count in cursor.fetchall():
                    if isinstance(actor_name, bytes):
                        actor_name = actor_name.decode("utf-8")

                    counts[actor_name] += count

    # Step 3: Sort contributors by upload count
    uploaders = counts.most_common()
    upload_count = sum(counts.values())

    return uploaders, upload_count


if __name__ == "__main__":
    category = "images_from_Wiki_Loves_Folklore_2026"

    uploaders, upload_count = get_uploaders_in_category(
        category
    )

    print(f"\nUploaders in category '{category}':")

    for username, count in uploaders:
        print(f"{username}: {count} uploads")

    print(f"\nTotal uploads: {upload_count}")
    print(f"Total contributors: {len(uploaders)}")
