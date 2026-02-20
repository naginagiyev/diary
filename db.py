import psycopg2
from config import connectionString

def saveRecord(createdAt, respondedAt, happinessScore, productivityScore, notes):
    if createdAt:
        createdAt = createdAt.replace(tzinfo=None)
    if respondedAt:
        respondedAt = respondedAt.replace(tzinfo=None)

    conn = psycopg2.connect(connectionString)
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO diary (created_at, responded_at, happiness_score, productivity_score, notes)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (createdAt, respondedAt, happinessScore, productivityScore, notes),
            )
        conn.commit()
    finally:
        conn.close()