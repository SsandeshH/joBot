import psycopg2

# Establish connection
conn = psycopg2.connect(
    host="localhost",
    port="5432",
    database="meroJobDb",
    user="postgres",
    password="SsandeshH12345"
)

# Create an instance of cursor
cur = conn.cursor()

def clean_data(value):
    """
    Convert empty strings to None to avoid PostgreSQL errors.
    """
    return None if isinstance(value, str) and value.strip() == "" else value

def insert_values(job_data):
    """
    Insert job data into the PostgreSQL database.
    """
    try:
        cur.execute(
            '''
            INSERT INTO jobs (
                company_name, job_title, job_category, job_level, no_of_vacancy, 
                employment_type, job_location, offered_salary, deadline, 
                education_level, experience_required, professional_skill_required
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''',
            (
                clean_data(job_data.get('company_name')),
                clean_data(job_data.get('job_title')),
                clean_data(job_data.get('job_category')),
                clean_data(job_data.get('job_level')),
                clean_data(job_data.get('no_of_vacancy')),  # Integer/number column
                clean_data(job_data.get('employment_type')),
                clean_data(job_data.get('job_location')),
                clean_data(job_data.get('offered_salary')),  # Integer/number column
                clean_data(job_data.get('deadline')),
                clean_data(job_data.get('education_level')),
                clean_data(job_data.get('experience_required')),
                clean_data(job_data.get('professional_skill_required'))
            )
        )
        conn.commit()  # Commit the transaction
        print(f"Inserted: {job_data.get('job_title')}")
    except Exception as e:
        print(f"Error inserting data: {e}")
        conn.rollback()  # Rollback in case of error

