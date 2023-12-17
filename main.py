import pymongo
import certifi
from pymongo import MongoClient
from pprint import pprint
import getpass
from menu_definitions import menu_main
from menu_definitions import add_menu
from menu_definitions import delete_menu
from menu_definitions import list_menu
import datetime
from datetime import date

def add(db):
    """
    Present the add menu and execute the user's selection.
    :param db:  The connection to the current database.
    :return:    None
    """
    add_action: str = ''
    while add_action != add_menu.last_action():
        add_action = add_menu.menu_prompt()
        exec(add_action)


def delete(db):
    """
    Present the delete menu and execute the user's selection.
    :param db:  The connection to the current database.
    :return:    None
    """
    delete_action: str = ''
    while delete_action != delete_menu.last_action():
        delete_action = delete_menu.menu_prompt()
        exec(delete_action)


def list_objects(db):
    """
    Present the list menu and execute the user's selection.
    :param db:  The connection to the current database.
    :return:    None
    """
    list_action: str = ''
    while list_action != list_menu.last_action():
        list_action = list_menu.menu_prompt()
        exec(list_action)


def add_student(db):
    """
    Add a new student, making sure that we don't put in any duplicates,
    based on all the candidate keys (AKA unique indexes) on the
    students collection.  Theoretically, we could query MongoDB to find
    the uniqueness constraints in place, and use that information to
    dynamically decide what searches we need to do to make sure that
    we don't violate any of the uniqueness constraints.  Extra credit anyone?
    :param collection:  The pointer to the students collection.
    :return:            None
    """
    # Create a "pointer" to the students collection within the db database.
    collection = db["students"]
    unique_name: bool = False
    unique_email: bool = False
    lastName: str = ''
    firstName: str = ''
    email: str = ''
    while not unique_name or not unique_email:
        lastName = input("Student last name--> ")
        firstName = input("Student first name--> ")
        email = input("Student e-mail address--> ")
        name_count: int = collection.count_documents({"last_name": lastName, "first_name": firstName})
        unique_name = name_count == 0
        if not unique_name:
            print("We already have a student by that name.  Try again.")
        if unique_name:
            email_count = collection.count_documents({"e_mail": email})
            unique_email = email_count == 0
            if not unique_email:
                print("We already have a student with that e-mail address.  Try again.")
    # Build a new students document preparatory to storing it
    student = {
        "last_name": lastName,
        "first_name": firstName,
        "e_mail": email
    }
    results = collection.insert_one(student)
    print("Student added successfully.")

def add_department(db):
    collection = db["departments"]

    while True:
        try:
            name = input("Department's name --> ")
            abbreviation = input("Department's abbreviation --> ")
            chair_name = input("Department's chair name --> ")
            building = input("Department's building --> ")
            office = input("Department's office number --> ")
            description = input("Department's description --> ")

            # Check for uniqueness constraints
            name_count = collection.count_documents({"name": name})
            abbreviation_count = collection.count_documents({"abbreviation": abbreviation})
            chair_name_count = collection.count_documents({"chair_name": chair_name})
            description_count = collection.count_documents({"description": description})

            if name_count > 0:
                raise pymongo.errors.WriteError("A department with that name already exists.")
            if abbreviation_count > 0:
                raise pymongo.errors.WriteError("A department with that abbreviation already exists.")
            if chair_name_count > 0:
                raise pymongo.errors.WriteError("A department with that chair name already exists.")
            if description_count > 0:
                raise pymongo.errors.WriteError("A department with that description already exists.")

            # Check if the office is occupied
            office_count = collection.count_documents({"building": building, "office": office})
            if office_count > 0:
                raise pymongo.errors.WriteError("A department is already occupying that office.")

            # Validate department data against the schema
            department = {
                "name": name,
                "abbreviation": abbreviation,
                "chair_name": chair_name,
                "building": building,
                "office": office,
                "description": description
            }

            # Insert the department document
            results = collection.insert_one(department)
            print("Department added successfully.")
            break
        except pymongo.errors.WriteError as e:
            print(f"Error: {e}")
            print("Please correct the department data and try again.")



def select_student(db):
    """
    Select a student by the combination of the last and first.
    :param db:      The connection to the database.
    :return:        The selected student as a dict.  This is not the same as it was
                    in SQLAlchemy, it is just a copy of the Student document from
                    the database.
    """
    # Create a connection to the students collection from this database
    collection = db["students"]
    found: bool = False
    lastName: str = ''
    firstName: str = ''
    while not found:
        lastName = input("Student's last name--> ")
        firstName = input("Student's first name--> ")
        name_count: int = collection.count_documents({"last_name": lastName, "first_name": firstName})
        found = name_count == 1
        if not found:
            print("No student found by that name.  Try again.")
    found_student = collection.find_one({"last_name": lastName, "first_name": firstName})
    return found_student

def select_department(db):
    collection = db["departments"]
    found: bool = False
    while not found:
        abbreviation: str = input("Department's abbreviation --> ")
        chair_name: str = input("Department's chair name --> ")
        building: str = input("Department's building --> ")
        office: int = input("Department's office number --> ")
        description: str = input("Department's description --> ")
        name_count: int = collection.count_documents({"abbreviation": abbreviation, "chair_name": chair_name, "building": building, "office": office, "description": description})
        found = name_count == 1
        if not found:
            print("No department found. Try again")
    found_department = collection.find_one({"abbreviation": abbreviation, "chair_name": chair_name, "building": building, "office": office, "description": description})
    return found_department

def delete_student(db):
    """
    Delete a student from the database.
    :param db:  The current database connection.
    :return:    None
    """
    # student isn't a Student object (we have no such thing in this application)
    # rather it's a dict with all the content of the selected student, including
    # the MongoDB-supplied _id column which is a built-in surrogate.
    student = select_student(db)
    # Create a "pointer" to the students collection within the db database.
    students = db["students"]
    # student["_id"] returns the _id value from the selected student document.
    deleted = students.delete_one({"_id": student["_id"]})
    # The deleted variable is a document that tells us, among other things, how
    # many documents we deleted.
    print(f"We just deleted: {deleted.deleted_count} students.")

def delete_department(db):
    department = select_department(db)
    departments = db["departments"]
    deleted = departments.delete_one({"_id": department["_id"]})
    print(f"We just deleted: {deleted.deleted_count} department.")


def list_student(db):
    """
    List all of the students, sorted by last name first, then the first name.
    :param db:  The current connection to the MongoDB database.
    :return:    None
    """
    # No real point in creating a pointer to the collection, I'm only using it
    # once in here.  The {} inside the find simply tells the find that I have
    # no criteria.  Essentially this is analogous to a SQL find * from students.
    # Each tuple in the sort specification has the name of the field, followed
    # by the specification of ascending versus descending.
    students = db["students"].find({}).sort([("last_name", pymongo.ASCENDING),
                                             ("first_name", pymongo.ASCENDING)])
    # pretty print is good enough for this work.  It doesn't have to win a beauty contest.
    for student in students:
        pprint(student)

def list_department(db):
    departments = db["departments"].find({}).sort([("name", pymongo.ASCENDING)])
    for department in departments:
        pprint(department)


def add_course(db):
    course_collection = db["courses"]

    while True:
        department_abbreviation = input("Enter Department Abbreviation --> ")
        course_number = input("Enter Course Number --> ")
        course_name = input("Enter Course Name --> ")
        units = input("Enter Course Units --> ")

        department_collection = db["departments"]
        department = department_collection.find_one({"abbreviation": department_abbreviation})

        if department:
            # Check if the course exists in the courses collection
            existing_course = course_collection.find_one({"courseNumber": course_number})

            if existing_course:
                print("Course with this number already exists. Try again.")
            else:
                course = {
                    "courseNumber": course_number,
                    "courseName": course_name,
                    "units": units,
                    "department": department_abbreviation  # Add a reference to the department
                }

                # Insert the course into the courses collection
                course_collection.insert_one(course)
                print("Course added successfully.")
                break
        else:
            print("Department not found.")


def select_course(db):
    department_abbreviation = input("Enter Department Abbreviation --> ")
    course_number = input("Enter Course Number --> ")

    course = db["courses"].find_one({"departmentAbbreviation": department_abbreviation, "courseNumber": course_number})
    if course:
        return course
    else:
        print("Course not found.")
        return None

def delete_course(db):
    course_number = input("Enter Course Number -->")

    result = db["courses"].delete_one({"courseNumber": course_number})

    if result.deleted_count > 0:
        print("Course deleted successfully.")
    else:
        print("Course not found or deletion unsuccessful.")

def list_course(db):
    courses = db["courses"].find({})
    for course in courses:
        print(f"Course Number: {course.get('courseNumber')}, Course Name: {course.get('courseName')}")

def add_section(db):
    valid_buildings = ['ANAC', 'CDC', 'DC', 'ECS', 'EN2', 'EN3', 'EN4', 'EN5', 'ET', 'HSCI', 'NUR', 'VEC']

    while True:
        department_abbreviation = input("Enter Department Abbreviation --> ")
        course_number = input("Enter Course Number --> ")
        section_number = input("Enter Section Number --> ")
        semester = input("Enter Semester (Fall, Spring, Summer I, Summer II, Summer III, Winter) --> ")
        section_year = int(input("Enter Section Year --> "))
        building = input("Enter Building --> ")
        room = int(input("Enter Room Number (0 - 999) --> "))
        schedule = input("Enter Schedule (MW, TuTh, MWF, F, S) --> ")
        start_time = input("Enter Start Time (format: HH:MM AM/PM) --> ")
        instructor_name = input("Enter Instructor's Name --> ")

        course_collection = db["courses"]
        course = course_collection.find_one({"courseNumber": course_number, "department": department_abbreviation})

        if course:
            existing_section_by_number = next(
                (s for s in course.get("sections", []) if s.get("sectionNumber") == section_number),
                None
            )

            if existing_section_by_number:
                print("Section with this number already exists for the course. Try again.")
                continue

            # Check if the building value is in the valid list
            if building not in valid_buildings:
                print("Invalid building. Please enter a valid building code.")
                continue

            # Check if the time format is valid
            try:
                start_time = datetime.datetime.strptime(start_time, "%I:%M %p")
            except ValueError:
                try:
                    start_time = datetime.datetime.strptime(start_time, "%H:%M")
                except ValueError:
                    print("Invalid time format. Please enter time in HH:MM AM/PM format.")
                    continue

            if not (8 <= start_time.hour <= 19 and 0 <= start_time.minute <= 59):
                print("Start time should be between 8:00 AM and 7:30 PM.")
                continue

            if semester not in ['Fall', 'Spring', 'Summer I', 'Summer II', 'Summer III', 'Winter']:
                print("Invalid semester.")
                continue

            if schedule not in ['MW', 'TuTh', 'MWF', 'F', 'S']:
                print("Invalid schedule.")
                continue

            if not (0 < room < 1000):
                print("Room number should be between 0 and 999.")
                continue

            section_data = {
                "sectionNumber": section_number,
                "schedule": schedule,
                "semester": semester,
                "sectionYear": section_year,
                "building": building,
                "room": room,
                "startTime": start_time.strftime("%I:%M %p"),
                "instructor": instructor_name
            }

            # Update the courses collection to add the section to the course
            course_collection.update_one(
                {"courseNumber": course_number, "department": department_abbreviation},
                {"$push": {"sections": section_data}}
            )
            print("Section added successfully to the course.")
            break
        else:
            print("Course not found in the department.")


def delete_section(db):
    department_abbreviation = input("Enter Department Abbreviation --> ")
    course_number = input("Enter Course Number --> ")
    section_number = input("Enter Section Number --> ")

    course_collection = db["courses"]

    result = course_collection.update_one(
        {
            "courseNumber": course_number,
            "department": department_abbreviation,
            "sections.sectionNumber": section_number
        },
        {"$pull": {"sections": {"sectionNumber": section_number}}}
    )

    if result.modified_count > 0:
        print("Section deleted successfully from the course.")
    else:
        print("Section not found or deletion unsuccessful.")


def list_section(db):
    department_abbreviation = input("Enter Department Abbreviation --> ")
    course_number = input("Enter Course Number --> ")

    course = db["courses"].find_one({"courseNumber": course_number, "department": department_abbreviation})

    if course:
        sections = course.get("sections", [])
        if sections:
            for section in sections:
                print(f"Section Number: {section.get('sectionNumber')}")
                print(f"Semester: {section.get('semester')}")
                print(f"Section Year: {section.get('sectionYear')}")
                print(f"Room: {section.get('room')}")
                print(f"Building: {section.get('building')}")
                print(f"Schedule: {section.get('schedule')}")
                print(f"Start Time: {section.get('startTime')}")
                print(f"Instructor: {section.get('instructor')}")
                print("---------------")
        else:
            print("No sections found for this course.")
    else:
        print("Course not found in the department.")

def select_section(db):
    department_abbreviation = input("Enter Department Abbreviation --> ")
    course_number = input("Enter Course Number --> ")
    section_number = input("Enter Section Number --> ")

    course = db["courses"].find_one(
        {
            "courseNumber": course_number,
            "department": department_abbreviation,
            "sections.sectionNumber": section_number
        },
        {"sections.$": 1}
    )

    if course:
        sections = course.get("sections", [])
        if sections:
            return sections[0]  # Returning the selected section
        else:
            print("No sections found for this course.")
    else:
        print("Section not found or course not found in the department.")
    return None


def add_major(db):
    collection = db["majors"]

    while True:
        try:
            department_abbreviation = input("Department Abbreviation --> ")
            major_name = input("Major Name --> ")
            # Check for uniqueness constraints
            major_count = collection.count_documents({"name": major_name})
            if major_count > 0:
                raise pymongo.errors.WriteError("A major with that name already exists.")

            # Check if the department exists
            department = db["departments"].find_one({"abbreviation": department_abbreviation})
            if not department:
                raise pymongo.errors.WriteError("Department not found.")

            # Validate major data against the schema
            major = {
                "departmentAbbreviation": department_abbreviation,
                "name": major_name
                # Other properties related to the major can be added here
            }

            # Insert the major document
            results = collection.insert_one(major)
            print("Major added successfully.")
            break
        except pymongo.errors.WriteError as e:
            print(f"Error: {e}")
            print("Please correct the major data and try again.")


def delete_major(db):
    collection = db["majors"]

    department_abbreviation = input("Department Abbreviation --> ")
    major_name = input("Major Name --> ")

    result = collection.delete_one({"departmentAbbreviation": department_abbreviation, "name": major_name})

    if result.deleted_count > 0:
        print("Major deleted successfully.")
    else:
        print("Major not found or deletion unsuccessful.")


def list_major(db):
    collection = db["majors"]
    majors = collection.find({}).sort([("name", pymongo.ASCENDING)])

    for major in majors:
        pprint(major)


def select_major(db):
    collection = db["majors"]

    department_abbreviation = input("Department Abbreviation --> ")
    major_name = input("Major Name --> ")

    major = collection.find_one({"departmentAbbreviation": department_abbreviation, "name": major_name})

    if major:
        pprint(major)
    else:
        print("Major not found.")


def add_student_major(db):
    students = db["students"]
    majors = db["majors"]

    student = select_student(db)
    if student:
        major_name = input("Enter Major Name --> ")

        major = majors.find_one({"name": major_name})
        if major:
            # Retrieve existing majors for the student or initialize an empty list
            student_majors = student.get("majors", [])

            # Check if the major is already associated with the student
            if any(m['name'] == major_name for m in student_majors):
                print(f"Student already enrolled in '{major_name}' major.")
            else:
                # Get the current date
                today_date = date.today()

                # Prompt the user to enter the declaration date
                declaration_date_str = input("Enter Declaration Date (YYYY-MM-DD) --> ")

                try:
                    # Convert input string to a date object
                    declaration_date = date.fromisoformat(declaration_date_str)

                    # Check if the declaration date is less than or equal to today's date
                    if declaration_date <= today_date:
                        # Construct the major entry with the declaration date
                        new_major_entry = {"name": major_name, "declarationDate": declaration_date.isoformat()}

                        # Add the new major entry to the list of student's majors
                        student_majors.append(new_major_entry)

                        # Update the student document to include the updated list of majors
                        result = students.update_one(
                            {"_id": student["_id"]},
                            {"$set": {"majors": student_majors}}
                        )
                        if result.modified_count > 0:
                            print(f"Student '{student['first_name']} {student['last_name']}' added to '{major_name}' major.")
                        else:
                            print("Failed to update student's majors.")
                    else:
                        print("Declaration date cannot be in the future.")
                except ValueError:
                    print("Invalid date format. Please use YYYY-MM-DD.")
        else:
            print("Major not found.")
    else:
        print("Student not found.")



def add_major_student(db):
    students = db["students"]
    majors = db["majors"]

    major_name = input("Enter Major Name --> ")

    major = majors.find_one({"name": major_name})
    if major:
        student = select_student(db)
        if student:
            # Retrieve existing majors for the student or initialize an empty list
            student_majors = student.get("majors", [])

            # Check if the student is already enrolled in the selected major
            if any(m['name'] == major_name for m in student_majors):
                print(f"Student already enrolled in '{major_name}' major.")
            else:
                # Get the current date
                today_date = date.today()

                # Prompt the user to enter the declaration date
                declaration_date_str = input("Enter Declaration Date (YYYY-MM-DD) --> ")

                try:
                    # Convert input string to a date object
                    declaration_date = date.fromisoformat(declaration_date_str)

                    # Check if the declaration date is less than or equal to today's date
                    if declaration_date <= today_date:
                        # Construct the major entry with the declaration date
                        new_major_entry = {"name": major_name, "declarationDate": declaration_date.isoformat()}

                        # Add the new major entry to the list of student's majors
                        student_majors.append(new_major_entry)

                        # Update the student document to include the updated list of majors
                        result = students.update_one(
                            {"_id": student["_id"]},
                            {"$set": {"majors": student_majors}}
                        )
                        if result.modified_count > 0:
                            print(f"Student '{student['first_name']} {student['last_name']}' added to '{major_name}' major.")
                        else:
                            print("Failed to update student's majors.")
                    else:
                        print("Declaration date cannot be in the future.")
                except ValueError:
                    print("Invalid date format. Please use YYYY-MM-DD.")
        else:
            print("Student not found.")
    else:
        print("Major not found.")



def list_student_major(db):
    students = db["students"]

    student = select_student(db)
    if student:
        student_majors = student.get("majors", [])
        if student_majors:
            print(f"Majors for {student['first_name']} {student['last_name']}:")
            for major in student_majors:
                print(f"- {major}")
        else:
            print(f"No majors found for {student['first_name']} {student['last_name']}.")
    else:
        print("Student not found.")


def list_major_student(db):
    students = db["students"]

    major_name = input("Enter Major Name --> ")

    students_in_major = students.find({"majors": {"$elemMatch": {"name": major_name}}})
    if students_in_major:
        print(f"Students in '{major_name}' major:")
        for student in students_in_major:
            print(f"- {student['first_name']} {student['last_name']}")
    else:
        print(f"No students found in '{major_name}' major.")




def delete_student_major(db):
    students = db["students"]

    student = select_student(db)
    if student:
        student_majors = student.get("majors", [])
        if student_majors:
            print(f"Majors for {student['first_name']} {student['last_name']}:")
            for index, major in enumerate(student_majors):
                print(f"{index + 1}. {major}")

            if student_majors:
                try:
                    index_to_remove = int(input("Enter the index of the major to remove: ")) - 1
                    if 0 <= index_to_remove < len(student_majors):
                        major_to_remove = student_majors[index_to_remove]
                        student_majors.remove(major_to_remove)

                        # Update the student document to remove the selected major
                        update_data = {"majors": student_majors}

                        # Check and remove declarationDate attribute if exists
                        if "declarationDate" in student:
                            del student["declarationDate"]

                        # Update the student document
                        result = students.update_one(
                            {"_id": student["_id"]},
                            {"$set": update_data, "$unset": {"declarationDate": ""}}
                        )

                        if result.modified_count > 0:
                            print(f"Removed '{major_to_remove}' major from {student['first_name']} {student['last_name']}.")
                        else:
                            print("Failed to remove the major.")
                    else:
                        print("Invalid index. Please enter a valid index.")
                except ValueError:
                    print("Invalid input. Please enter a valid index.")
        else:
            print(f"No majors found for {student['first_name']} {student['last_name']}.")
    else:
        print("Student not found.")


def delete_major_student(db):
    students = db["students"]

    major_name = input("Enter Major Name --> ")

    # Query using $elemMatch to find students with the specified major name in the 'majors' array
    students_with_major = students.find({"majors": {"$elemMatch": {"name": major_name}}})
    students_list = list(students_with_major)

    if students_list:
        print(f"Students in '{major_name}' major:")
        for index, student in enumerate(students_list):
            print(f"{index + 1}. {student['first_name']} {student['last_name']}")

        try:
            index_to_remove = int(input("Enter the index of the student to remove from the major: ")) - 1

            if 0 <= index_to_remove < len(students_list):
                student_to_remove = students_list[index_to_remove]
                student_id = student_to_remove["_id"]

                # Remove the major from the selected student
                students.update_one(
                    {"_id": student_id},
                    {"$pull": {"majors": {"name": major_name}}}
                )

                print(f"Removed {student_to_remove['first_name']} {student_to_remove['last_name']} from '{major_name}' major.")
            else:
                print("Invalid index. Please enter a valid index.")
        except ValueError:
            print("Invalid input. Please enter a valid index.")
    else:
        print(f"No students found in '{major_name}' major.")



def add_student_section(db):
    # Select a student
    student = select_student(db)
    if student:
        # Select a section
        section = select_section(db)
        if section:
            # Get the courses collection
            courses_collection = db["courses"]

            # Fetch course details based on the selected section
            course = courses_collection.find_one(
                {"sections": section}
            )

            if course:
                # Extract course details from the retrieved course document
                course_number = course.get("courseNumber")
                department_abbreviation = course.get("department")

                # Update the section with course details
                section["courseNumber"] = course_number
                section["department"] = department_abbreviation

                # Get the students collection
                students_collection = db["students"]

                # Update the student document to add enrollment to the 'enrollments' array
                result = students_collection.update_one(
                    {"_id": student["_id"]},
                    {"$addToSet": {"enrollments": section}}
                )

                if result.modified_count > 0:
                    print("Student enrolled in the section successfully.")
                else:
                    print("Enrollment unsuccessful.")
            else:
                print("Course details not found for the selected section.")
        else:
            print("Section not found.")
    else:
        print("Student not found.")


def add_section_student(db):
    # Select a section
    section = select_section(db)
    if section:
        # Get the courses collection
        courses_collection = db["courses"]

        # Fetch course details based on the selected section
        course = courses_collection.find_one(
            {"sections": section}
        )

        if course:
            # Extract course details from the retrieved course document
            course_number = course.get("courseNumber")
            department_abbreviation = course.get("department")

            # Select a student
            student = select_student(db)
            if student:
                # Get the students collection
                students_collection = db["students"]

                # Update the student document to add enrollment to the 'enrollments' array in the selected section
                section["courseNumber"] = course_number
                section["department"] = department_abbreviation

                result = students_collection.update_one(
                    {"_id": student["_id"]},
                    {"$addToSet": {"enrollments": section}}
                )

                if result.modified_count > 0:
                    print("Student enrolled in the section successfully.")
                else:
                    print("Enrollment unsuccessful.")
            else:
                print("Student not found.")
        else:
            print("Course details not found for the selected section.")
    else:
        print("Section not found.")


def delete_student_section(db):
    # Select a student
    student = select_student(db)
    if student:
        # Display the current enrollments of the selected student
        current_enrollments = student.get("enrollments", [])
        print("Current Enrollments:")
        for idx, enrollment in enumerate(current_enrollments, start=1):
            # Fetch course details based on the enrollment
            department_abbreviation = enrollment.get("department")
            course_number = enrollment.get("courseNumber")
            section_number = enrollment.get("sectionNumber")
            print(f"{idx}. {department_abbreviation} {course_number} - Section {section_number}")

        # Ask user to select the enrollment to delete
        enrollment_to_delete_idx = int(input("Enter the number of the enrollment to delete: ")) - 1

        if 0 <= enrollment_to_delete_idx < len(current_enrollments):
            section_to_delete = current_enrollments[enrollment_to_delete_idx]

            # Get the students collection
            students_collection = db["students"]

            # Remove the selected section from the student's enrollments
            result = students_collection.update_one(
                {"_id": student["_id"]},
                {"$pull": {"enrollments": section_to_delete}}
            )

            if result.modified_count > 0:
                print("Section deleted from student's enrollments successfully.")
            else:
                print("Deletion unsuccessful.")
        else:
            print("Invalid selection.")
    else:
        print("Student not found.")



def list_student_section(db):
    # Select a student
    student = select_student(db)
    if student:
        # Get the enrolled sections of the selected student
        enrollments = student.get("enrollments", [])

        if enrollments:
            print(f"Enrolled sections for {student['first_name']} {student['last_name']}:")
            for idx, enrollment in enumerate(enrollments, start=1):
                department_abbreviation = enrollment.get("department")
                course_number = enrollment.get("courseNumber")
                section_number = enrollment.get("sectionNumber")
                print(f"{idx}. {department_abbreviation} {course_number} - Section {section_number}")
        else:
            print("No sections enrolled for this student.")
    else:
        print("Student not found.")



def list_enrollment(db):
    # Retrieve all student documents
    all_students = db["students"].find({}, {"first_name": 1, "last_name": 1, "enrollments": 1})

    enrollment_list = []

    # Extract enrollment details along with student names and create a list
    for student in all_students:
        first_name = student.get("first_name")
        last_name = student.get("last_name")
        enrollments = student.get("enrollments", [])
        for enrollment in enrollments:
            # Add student's name to the enrollment record
            enrollment_with_name = {
                "first_name": first_name,
                "last_name": last_name,
                "department": enrollment.get("department"),
                "courseNumber": enrollment.get("courseNumber"),
                "sectionNumber": enrollment.get("sectionNumber")
            }
            enrollment_list.append(enrollment_with_name)

    # Sort the enrollment list by department, course, and section number
    sorted_enrollments = sorted(enrollment_list, key=lambda x: (x['department'], x['courseNumber'], x['sectionNumber']))

    # Display sorted enrollment records with student names
    if sorted_enrollments:
        print("Enrollment Records (Sorted by Department, Course, Section Number):")
        for idx, enrollment in enumerate(sorted_enrollments, start=1):
            first_name = enrollment.get("first_name")
            last_name = enrollment.get("last_name")
            department_abbreviation = enrollment.get("department")
            course_number = enrollment.get("courseNumber")
            section_number = enrollment.get("sectionNumber")
            print(f"{idx}. {first_name} {last_name}: {department_abbreviation} {course_number} - Section {section_number}")
    else:
        print("No enrollment records found.")


def add_student_PassFail(db):
    # Select a student
    student = select_student(db)
    if student:
        department_abbreviation = input("Enter Department Abbreviation --> ")
        course_number = input("Enter Course Number --> ")
        section_number = input("Enter Section Number --> ")

        # Get today's date
        today_date = datetime.datetime.now().date()

        # Check if the entered date is valid and not in the future
        while True:
            try:
                application_date = input("Enter Application Date (YYYY-MM-DD): ")
                application_date = datetime.datetime.strptime(application_date, "%Y-%m-%d").date()
                if application_date > today_date:
                    print("Application date cannot be in the future. Please enter a valid date.")
                else:
                    break
            except ValueError:
                print("Invalid date format. Please enter the date in YYYY-MM-DD format.")

        # Check if the student is already enrolled in the specified section
        enrollment = {
            "department": department_abbreviation,
            "courseNumber": course_number,
            "sectionNumber": section_number
        }

        existing_enrollments = student.get("enrollments", [])

        # Check if the enrollment exists in the student's enrollments array
        for enr in existing_enrollments:
            if enr.get("department") == department_abbreviation and \
               enr.get("courseNumber") == course_number and \
               enr.get("sectionNumber") == section_number:
                # Check if there's an existing minSatisfactoryGrade attribute
                if enr.get("type") == "LetterGrade":
                    # Remove the minSatisfactoryGrade attribute
                    enr.pop("minSatisfactoryGrade", None)

                # Enrollment type is given the PassFail type
                enr["type"] = "PassFail"
                enr["applicationDate"] = application_date.strftime("%Y-%m-%d")

                result = db["students"].update_one(
                    {"_id": student["_id"]},
                    {"$set": {"enrollments": existing_enrollments}}
                )

                if result.modified_count > 0:
                    print("PassFail enrollment added successfully.")
                    return
                else:
                    print("Failed to update the enrollment.")
                    return

        print("Student is not enrolled in the specified section.")
    else:
        print("Student not found.")



def add_student_LetterGrade(db):
    # Select a student
    student = select_student(db)
    if student:
        department_abbreviation = input("Enter Department Abbreviation --> ")
        course_number = input("Enter Course Number --> ")
        section_number = input("Enter Section Number --> ")
        min_satisfactory = input("Enter Minimum Satisfactory Grade (A, B, or C): ").upper()

        if min_satisfactory not in ['A', 'B', 'C']:
            print("Invalid grade. Minimum Satisfactory Grade must be 'A', 'B', or 'C'.")
            return

        # Check if the student is already enrolled in the specified section
        existing_enrollments = student.get("enrollments", [])

        for enr in existing_enrollments:
            if enr.get("department") == department_abbreviation and \
               enr.get("courseNumber") == course_number and \
               enr.get("sectionNumber") == section_number:
                # Check if there's an existing applicationDate attribute
                if enr.get("type") == "PassFail":
                    # Remove the applicationDate attribute
                    enr.pop("applicationDate", None)

                # Enrollment type is given the LetterGrade type
                enr["type"] = "LetterGrade"
                enr["minSatisfactory"] = min_satisfactory

                result = db["students"].update_one(
                    {"_id": student["_id"]},
                    {"$set": {"enrollments": existing_enrollments}}
                )

                if result.modified_count > 0:
                    print("LetterGrade enrollment added successfully.")
                    return
                else:
                    print("Failed to update the enrollment.")
                    return

        print("Student is not enrolled in the specified section.")
    else:
        print("Student not found.")

if __name__ == '__main__':
    cluster = "mongodb+srv://raagpatel01:D8iR2BVBHiB33n7M@cluster0.4tftauz.mongodb.net/?retryWrites=true&w=majority"
    client = MongoClient(cluster, tlsCAFile=certifi.where())
    # As a test that the connection worked, print out the database names.
    print(client.list_database_names())
    # db will be the way that we refer to the database from here on out.
    db = client["CECS323-MongoDB-SingleCollection"]    # Print off the collections that we have available to us, again more of a test than anything.
    department_schema = {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["building", "name", "abbreviation", "chair_name", "description"],
            "properties": {
                "building": {
                    "bsonType": "string",
                    "enum": ['ANAC', 'CDC', 'DC', 'ECS', 'EN2', 'EN3', 'EN4', 'EN5', 'ET', 'HSCI', 'NUR', 'VEC']
                },
                "name": {
                    "bsonType": "string",
                    "minLength": 10,
                    "maxLength": 50
                },
                "abbreviation": {
                    "bsonType": "string",
                    "maxLength": 6
                },
                "chair_name": {
                    "bsonType": "string",
                    "maxLength": 80
                },
                "description": {
                    "bsonType": "string",
                    "maxLength": 80
                }
            }
        }
    }
    course_schema = {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["departmentAbbreviation", "courseNumber", "courseName", "units"],
            "properties": {
                "departmentAbbreviation": {
                    "bsonType": "string",
                    "description": "Abbreviation of the department",
                    "maxLength": 6
                },
                "courseNumber": {
                    "bsonType": "int",
                    "description": "Course number",
                    "minimum": 100,
                    "maximum": 699
                },
                "courseName": {
                    "bsonType": "string",
                    "description": "Name of the course",
                    "maxLength": 100
                },
                "units": {
                    "bsonType": "int",
                    "description": "Number of units for the course",
                    "minimum": 1,
                    "maximum": 5
                }
            },
            "uniqueKeys": {
                "unique_department_courseNumber": {
                    "key": {"departmentAbbreviation": 1, "courseNumber": 1},
                    "name": "unique_department_courseNumber",
                    "background": True
                },
                "unique_department_courseName": {
                    "key": {"departmentAbbreviation": 1, "courseName": 1},
                    "name": "unique_department_courseName",
                    "background": True
                }
            }
        }
    }
    section_schema = {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["courseNumber", "sectionNumber", "semester", "sectionYear", "building", "room", "schedule",
                         "startTime", "instructor"],
            "properties": {
                "courseNumber": {
                    "bsonType": "string",
                    "description": "Course number"
                },
                "sectionNumber": {
                    "bsonType": "string",
                    "description": "Section number"
                },
                "semester": {
                    "bsonType": "string",
                    "description": "Semester",
                    "enum": ["Fall", "Spring", "Summer I", "Summer II", "Summer III", "Winter"]
                },
                "sectionYear": {
                    "bsonType": "int",
                    "description": "Section year"
                },
                "building": {
                    "bsonType": "string",
                    "description": "Building where section takes place",
                    "enum": ['ANAC', 'CDC', 'DC', 'ECS', 'EN2', 'EN3', 'EN4', 'EN5', 'ET', 'HSCI', 'NUR', 'VEC']
                },
                "room": {
                    "bsonType": "int",
                    "description": "Room number",
                    "minimum": 1,
                    "maximum": 999
                },
                "schedule": {
                    "bsonType": "string",
                    "description": "Class schedule",
                    "enum": ["MW", "TuTh", "MWF", "F", "S"]
                },
                "startTime": {
                    "bsonType": "string",
                    "description": "Start time of the section",
                    "pattern": "^([0-1]?[0-9]|2[0-3]):[0-5][0-9] [AP]M$"
                },
                "instructor": {
                    "bsonType": "string",
                    "description": "Instructor's name"
                }
            },
            "uniqueKeys": {
                "unique_courseNumber_sectionNumber_semester_sectionYear": {
                    "key": {"courseNumber": 1, "sectionNumber": 1, "semester": 1, "sectionYear": 1},
                    "name": "unique_courseNumber_sectionNumber_semester_sectionYear",
                    "background": True
                },
                "unique_semester_sectionYear_building_room_schedule_startTime": {
                    "key": {"semester": 1, "sectionYear": 1, "building": 1, "room": 1, "schedule": 1, "startTime": 1},
                    "name": "unique_semester_sectionYear_building_room_schedule_startTime",
                    "background": True
                },
                "unique_semester_sectionYear_schedule_startTime_instructor": {
                    "key": {"semester": 1, "sectionYear": 1, "schedule": 1, "startTime": 1, "instructor": 1},
                    "name": "unique_semester_sectionYear_schedule_startTime_instructor",
                    "background": True
                }
            }
        }
    }

    #db.drop_collection("departments")
    #db.create_collection("departments", validator=department_schema)
    print(db.list_collection_names())
    # student is our students collection within this database.
    # Merely referencing this collection will create it, although it won't show up in Atlas until
    # we insert our first document into this collection.
    students = db["students"]
    student_count = students.count_documents({})
    print(f"Students in the collection so far: {student_count}")

    # ************************** Set up the students collection
    students_indexes = students.index_information()
    if 'students_last_and_first_names' in students_indexes.keys():
        print("first and last name index present.")
    else:
        # Create a single UNIQUE index on BOTH the last name and the first name.
        students.create_index([('last_name', pymongo.ASCENDING), ('first_name', pymongo.ASCENDING)],
                              unique=True,
                              name="students_last_and_first_names")
    if 'students_e_mail' in students_indexes.keys():
        print("e-mail address index present.")
    else:
        # Create a UNIQUE index on just the e-mail address
        students.create_index([('e_mail', pymongo.ASCENDING)], unique=True, name='students_e_mail')
    pprint(students.index_information())
    main_action: str = ''
    while main_action != menu_main.last_action():
        main_action = menu_main.menu_prompt()
        print('next action: ', main_action)
        exec(main_action)


