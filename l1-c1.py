import unicodecsv
from datetime import datetime as dt

def read_csv(file_path):
	with open(file_path, 'rb') as file:
		reader = unicodecsv.DictReader(file)
		return list(reader)

def parse_date(date):
	if date == '':
		return None
	else:
		return dt.strptime(date, '%Y-%m-%d')

def parse_num(data):
	if data == '':
		return None
	else:
		return int(data)

def parse_state(state):
	return state == 'True'

def parsing(data_list):
	for data in data_list:
		data['join_date'] = parse_date(data['join_date'])
		data['cancel_date'] = parse_date(data['cancel_date'])
		data['is_udacity'] = parse_state(data['is_udacity'])
		data['is_canceled'] = parse_state(data['is_canceled'])
		data['days_to_cancel'] = parse_num(data['days_to_cancel'])
		data['account_key'] = parse_num(data['account_key'])
	return data_list

def uniqueness_number(data_list):
	account_key_set = set()
	for index in range(len(data_list)):
		account_key_set.add(data_list[index]['account_key'])
	return account_key_set

def replace_key(data_list):
	for item in data_list:
		value = item.pop('crt', None)
		item.update({'account_key': value})
	return data_list

def undetected_rows(student_set, daily_engagement):
	strange_row = []
	for row in daily_engagement:
		if row['account_key'] in student_set:
			strange_row.append(row)
	return strange_row

def check_date(start_date, cancel_date):
	return start_date != cancel_date

def anssure_cancelating(not_engagement):
	diff_row = []
	for row in not_engagement:
		if check_date(row['join_date'], row['cancel_date']):
			diff_row.append(row)
	return diff_row

def remove_udacity_accounts(enrollment):
	enrollment_student = []
	for student in enrollment:
		if not student['is_udacity']:
			enrollment_student.append(student)
	return enrollment_student

def filter_paid_student(enrollments):
	paid_student = dict()
	for student in enrollments:
		if student['days_to_cancel'] == None or student['days_to_cancel'] > 7:
			account_key = student['account_key']
			join_date = student['join_date']
			if not account_key in paid_student or join_date > paid_student[account_key]:
				paid_student[student['account_key']] = student['join_date']
	return paid_student

# Wrangling Phase Ph.1
enrollment = read_csv('E:\Data Analysis\c-ud170\enrollments.csv')
daily_engagement = read_csv('E:\Data Analysis\c-ud170\daily_engagement.csv')
project_submissions = read_csv('E:\Data Analysis\c-ud170\project_submissions.csv')

# Parsing Data Ph.1
enrollment = parsing(enrollment)
# Investigation Phase Ph.2
enrollment_row = len(enrollment)
enrollment_uniqueness_student_set = uniqueness_number(enrollment)
enrollment_uniqueness_student_number = len(enrollment_uniqueness_student_set)

daily_engagement_row = len(daily_engagement)
daily_engagement_replacing = replace_key(daily_engagement)
daily_engagement_uniqueness_student_set = uniqueness_number(daily_engagement_replacing)
daily_engagement_uniqueness_student_number = len(daily_engagement_uniqueness_student_set)

project_submissions_row = len(project_submissions)
project_submissions_uniqueness_student_set = uniqueness_number(project_submissions)
project_submissions_uniqueness_student_number = len(project_submissions_uniqueness_student_set)


print("Rows Number: Enrollment {}, Daily Engagement {}, Project Submissions {} \n\nUniqueness Student: Enrollment {}, Daily Engagement {}, Project Submissions {}"
	.format(enrollment_row, daily_engagement_row, project_submissions_row, 
		enrollment_uniqueness_student_number, daily_engagement_uniqueness_student_number, project_submissions_uniqueness_student_number))

# Missing students Ph.2
enrollment_student_not_engagement = undetected_rows(enrollment_uniqueness_student_set - daily_engagement_uniqueness_student_set,enrollment)

#Checker investigation ansure
enrollment_student_not_engagement_day = anssure_cancelating(enrollment_student_not_engagement)
# expected result : 0
# output: 3
# then there's another error.
print("Student With Diff {}".format(len(enrollment_student_not_engagement_day)))
# Detect three student ... they were a vertual student so that their data has true in is_udacity
# remove all udacity accounts.
enrollments_not_udacity_accounts = remove_udacity_accounts(enrollment)
# Inverstigation is done.
# Result Enrollments List Without Virtual Udacity Accounts, Detect There are student unenrolled in course 
# In the same day.

# Exploration Phase 3.
enrollments_paid_student = filter_paid_student(enrollments_not_udacity_accounts)
print(len(enrollments_paid_student))

