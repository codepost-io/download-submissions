import argparse
import base64
import os
import sys

import codepost

codepost.configure_api_key("YOUR API KEY")

##################### Argument Parsing ######################################################
parser = argparse.ArgumentParser(description='Download codePost submissions to a local folder.')

parser.add_argument('course_name', help='Name of codePost course')
parser.add_argument('course_period', help='Name of codePost period')
parser.add_argument('assignment', help='Name of codePost assignment')

args = parser.parse_args()

OUTPUT_DIRECTORY = args.assignment

_cwd = os.getcwd()
_upload_dir = os.path.join(_cwd, OUTPUT_DIRECTORY)

##################### Download submissions  ################################################

course_obj_list = codepost.course.list_available(name=args.course_name, period=args.course_period)
if len(course_obj_list) != 1:
    errorMessage = "Could not find a course with name={} and period={}.".format(args.course_name, args.course_period)
    raise ValueError(errorMessage)

course_obj = course_obj_list[0]

assignment = course_obj.assignments.by_name(name=args.assignment)
if assignment is None:
    errorMessage = "Could not find an assignment called {} in this course.".format(args.assignment)
    raise ValueError(errorMessage)

submissions = assignment.list_submissions()

##################### Write submissions locally  ############################################

def get_students_from_submission(submission):
    return ','.join(submission.students)

def is_directory(path):
    return path is not None

def write_file(cp_file, path="."):
    # thanks to @sschaub for prodding us to support binary files output
    data = cp_file.code
    is_binary = False

    if data[0:4] == "data" and "," in data[0:100]:
        prefix, data_remainder = data.split(",", 1)
        if prefix.split(";")[-1] == "base64":
            data = base64.b64decode(data_remainder)
            is_binary = True
    
    with open(os.path.join(path, cp_file.name), 'wb' if is_binary else 'w') as f:
        f.write(data)
        f.close()

for submission in submissions:

    # create folder for this submission
    dirname = get_students_from_submission(submission)
    student_dir = os.path.join(_upload_dir, dirname)
    os.makedirs(student_dir)

    # write submission's files into this folder
    for file in submission.files:
        if is_directory(file.path):

            sub_dir = os.path.join(student_dir, file.path)

            # if appropriate sub-folder doesn't exist, create it
            if not os.path.exists(sub_dir):
                os.makedirs(sub_dir)

            write_file(file, path=sub_dir)

        else:
            write_file(file, path=student_dir)

    # report progress to terminal
    print('#', end="")
    sys.stdout.flush()

print()
