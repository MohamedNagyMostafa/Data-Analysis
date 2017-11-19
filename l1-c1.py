import unicodecsv
import numpy as np
from collections import defaultdict
from datetime import datetime as dt

def read_csv(file_path):
	with open(file_path, 'rb') as file:
		reader = unicodecsv.DictReader(file)
		return list(reader)

def parse_date_enrollment(date):
	if date == '':
		return None
	else:
		return dt.strptime(date, '%Y-%m-%d')

def parse_date_engagement(date):
	if date == '':
		return None
	else:
		return dt.strptime(date, '%m/%d/%Y')

def parse_num(data):
	if data == '':
		return None
	else:
		return int(data)

def parse_state(state):
	return state == 'True'

def parsing_engagement(data_list):
	for data in data_list:
		data['utc_date'] = parse_date_engagement(data['utc_date'])
		data['total_minutes_visited'] = float(data['total_minutes_visited'])
	return data_list

def parsing_enrollment(data_list):
	for data in data_list:
		data['join_date'] = parse_date_enrollment(data['join_date'])
		data['cancel_date'] = parse_date_enrollment(data['cancel_date'])
		data['is_udacity'] = parse_state(data['is_udacity'])
		data['is_canceled'] = parse_state(data['is_canceled'])
		data['days_to_cancel'] = parse_num(data['days_to_cancel'])
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

def udacity_account_keys(enrollment):
	udacity_accounts = set()
	for student in enrollment:
		if student['is_udacity']:
			udacity_accounts.add(student['account_key'])
	return udacity_accounts

def remove_udacity_accounts(data, udacity_accounts):
	student_data = []
	for student in data:
		if not student['account_key'] in udacity_accounts:
			student_data.append(student)
	return student_data

def filter_paid_student(enrollments):
	paid_student = dict()
	for student in enrollments:
		if student['days_to_cancel'] == None or student['days_to_cancel'] > 7:
			account_key = student['account_key']
			join_date = student['join_date']
			if not account_key in paid_student or join_date > paid_student[account_key]:
				paid_student[student['account_key']] = student['join_date']
	return paid_student

def during_first_week(join_student_date, engagement_date):
	time_delta = engagement_date - join_student_date
	return  time_delta.days < 7 

def filter_engagement_paid_first_week(paid_student, daily_engagement):
	paid_student_first_week = []
	for student_engag in daily_engagement:
		account_key = student_engag['account_key']
		if account_key in paid_student and during_first_week(paid_student[account_key], student_engag['utc_date']):
			paid_student_first_week.append(student_engag)
	return paid_student_first_week

def break_to_student_data_group(student_data):
	student_data_group = defaultdict(list)
	for student in student_data:
		account_key = student['account_key']
		student_data_group[account_key].append(student)
	return student_data_group

def student_data_total_mints_group(data_group):
	total_mints_group = dict()
	for account_key, engagement_list in data_group.items():
		total_mints = 0
		for engagement in engagement_list:
			total_mints = total_mints + engagement['total_minutes_visited']
		total_mints_group[account_key] = total_mints
	return total_mints_group

def total_average_for_mints(student_data):
	total_average = 0
	for student_account in student_data:
		total_average = total_average + student_data[student_account]
	return total_average/ len(student_data)
# Wrangling Phase Ph.1
enrollment = read_csv('E:\Data Analysis\c-ud170\enrollments.csv')
daily_engagement = read_csv('E:\Data Analysis\c-ud170\daily_engagement.csv')
project_submissions = read_csv('E:\Data Analysis\c-ud170\project_submissions.csv')

# Parsing Data Ph.1
enrollment = parsing_enrollment(enrollment)
daily_engagement = parsing_engagement(daily_engagement)
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
udacity_accounts = udacity_account_keys(enrollment)
enrollments_not_udacity_accounts = remove_udacity_accounts(enrollment, udacity_accounts)
# Inverstigation is done.
# Result Enrollments List Without Virtual Udacity Accounts, Detect There are student unenrolled in course 
# In the same day.

# Exploration Phase 3.
enrollments_paid_student = filter_paid_student(enrollments_not_udacity_accounts)
print("paid students 'enrollment' : {}".format(len(enrollments_paid_student)))
# Ph3.2 filter paid students during their first week
engagments_not_udacity_accounts = remove_udacity_accounts(daily_engagement, udacity_accounts)
paid_student_engagement_first_week = filter_engagement_paid_first_week(enrollments_paid_student, engagments_not_udacity_accounts)

# Can make investigation on exploration data.
# Ph3.3 get average mints spent during week.
paid_student_engagement_first_week_groups = break_to_student_data_group(paid_student_engagement_first_week)
# investigation... expected output 995 
print("paid student number {}".format(len(paid_student_engagement_first_week_groups)))
# resume exploration.
paid_student_engagement_first_week_total_mints = student_data_total_mints_group(paid_student_engagement_first_week_groups)
# investigation ... expected output 995
print("paid student number {}".format(len(paid_student_engagement_first_week_total_mints)))

total_average_for_mints = total_average_for_mints(paid_student_engagement_first_week_total_mints)
print("total average is : {} mintues".format(total_average_for_mints))
# Also can use import numpy
total_mints = list(paid_student_engagement_first_week_total_mints.values())
# numpy.mean(paid_student_engagement_first_week_total_mints.values())
print("mean : {}\nstandard deviation : {}\nmaximum point: {}\nminimum point: {}"
	.format(
		np.mean(total_mints),
		np.std(total_mints),
		np.max(total_mints),
		np.min(total_mints)
		)
	)
# detection ... max has a problem ... standard deviation is more than mean with a long diff.
# min equal zero and max 10568 which led to there's an error because week have 10080 mints < max !!!
