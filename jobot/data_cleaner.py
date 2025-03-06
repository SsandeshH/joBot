# cleaning the data
def clean_job_data(job_data):
    cleaned_data = {}

    # Clean company_name
    cleaned_data['company_name'] = job_data.get('company_name', '').strip().replace('\n', ' ').replace('  ', ' ')

    # Clean job_title
    cleaned_data['job_title'] = job_data.get('job_title', '').strip()

    # Clean job_category
    cleaned_data['job_category'] = job_data.get('Job Category', '').split('\n')[0].strip()

    # Clean job_level
    cleaned_data['job_level'] = job_data.get('Job Level', '').strip()

    # Clean no_of_vacancy
    cleaned_data['no_of_vacancy'] = job_data.get('No. of Vacancy/s', '').strip('[] ')

    # Clean employment_type
    cleaned_data['employment_type'] = job_data.get('Employment Type', '').strip()

    # Clean job_location
    cleaned_data['job_location'] = job_data.get('Job Location', '').strip()

    # Clean offered_salary
    cleaned_data['offered_salary'] = job_data.get('Offered Salary', '').strip()

    # Clean deadline
    cleaned_data['deadline'] = job_data.get('Apply Before(Deadline)', '').split('\n')[0].strip()

    # Clean education_level
    cleaned_data['education_level'] = job_data.get('Education Level', '').strip()

    # Clean experience_required
    cleaned_data['experience_required'] = job_data.get('Experience Required', '').strip()

    # Clean professional_skill_required
    cleaned_data['professional_skill_required'] = job_data.get('Professional Skill Required', '').replace('\n', ', ').strip()

    return cleaned_data

# def clean_job_data(job_data_list):
#     """
#     Cleans a list of job data dictionaries.
#     """
#     cleaned_jobs = []
    
#     for job_data in job_data_list:
#         cleaned_data = {
#             'company_name': job_data.get('company_name', '').strip().replace('\n', ' ').replace('  ', ' '),
#             'job_title': job_data.get('job_title', '').strip(),
#             'job_category': job_data.get('Job Category', '').split('\n')[0].strip(),
#             'job_level': job_data.get('Job Level', '').strip(),
#             'no_of_vacancy': job_data.get('No. of Vacancy/s', '').strip('[] '),
#             'employment_type': job_data.get('Employment Type', '').strip(),
#             'job_location': job_data.get('Job Location', '').strip(),
#             'offered_salary': job_data.get('Offered Salary', '').strip(),
#             'deadline': job_data.get('Apply Before(Deadline)', '').split('\n')[0].strip(),
#             'education_level': job_data.get('Education Level', '').strip(),
#             'experience_required': job_data.get('Experience Required', '').strip(),
#             'professional_skill_required': job_data.get('Professional Skill Required', '').replace('\n', ', ').strip(),
#         }
#         cleaned_jobs.append(cleaned_data)
    
#     return cleaned_jobs
