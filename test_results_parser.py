#!/usr/bin/python3

import xml.dom.minidom
import argparse

# total_points, points_lost_base_case, points_lost_extended_case

# -t, --total-points      value  Total points for the project
# -b, --base-case-points  value  Points to lose for each base case
# -x, --extended-case-points value  Points to lose for each extended test case

TOTAL_POINTS_DEFAULT=30
BASE_CASE_POINTS_DEFAULT=2
EXTENDED_CASE_POINTS_DEFAULT=1
FILENAME_DEFAULT="test-results.xml"

def main():
    parser = argparse.ArgumentParser(description="read test xml files and grade them")
    parser.add_argument("-t", "--total-points", type=int, default=TOTAL_POINTS_DEFAULT,
                        help="Total points for the project (default="+str(TOTAL_POINTS_DEFAULT)+")")

    parser.add_argument("-b", "--base-case-points", type=int, default=BASE_CASE_POINTS_DEFAULT,
                        help="Points to lose for each base case failure (default="+str(BASE_CASE_POINTS_DEFAULT)+")")

    parser.add_argument("-x", "--extended-case-points", type=int, default=EXTENDED_CASE_POINTS_DEFAULT,
                        help="Points to lose for each extended case failure (default="+str(EXTENDED_CASE_POINTS_DEFAULT)+")")

    parser.add_argument("-f", "--test-results-file", type=str, default=FILENAME_DEFAULT,
                        help="Points to lose for each extended case failure (default='"+FILENAME_DEFAULT+"')")

    args=parser.parse_args()

    total_points = args.total_points
    base_case_points = args.base_case_points
    extended_case_points = args.extended_case_points
    test_results_filename = args.test_results_file

    # Open XML document using minidom parser
    DOMTree = xml.dom.minidom.parse(test_results_filename)
    test_suite = DOMTree.documentElement
    test_cases = test_suite.getElementsByTagName("testcase")

    # Grade the test cases
    graded_points = get_project_grade(test_cases, total_points, base_case_points, extended_case_points)

    # Emit Summary Header
    print ("Score: %s / %s" % (graded_points, total_points))
    print("Test: %s" % test_suite.getAttribute("name"))
    print("Test Cases           : %s" % test_suite.getAttribute("tests"))
    print("Test Failures/Errors : %s" % (int(test_suite.getAttribute("failures"))
          + int(test_suite.getAttribute("errors"))))

    # Emit Test Case Details
    for test_case in test_cases:
        test_case_name = str(test_case.getAttribute("name"))
        (status, points_lost) = get_testcase_grade(test_case, base_case_points, extended_case_points)

        if status == "OK":
            print("Test case: %s...[%s]" % (test_case_name, status))
        else:
            print("Test case: %s...[%s] (%d)" % (test_case_name, status, -1*points_lost))
            failure = test_case.getElementsByTagName("failure")[0]
            if failure:
                print(first3Lines(failure.childNodes[0].data))
            else:
                error = test_case.getElementsByTagName("error")[0]
                if error:
                    print(first3Lines(error.childNodes[0].data))
                else:
                    print("\tUnexpected missing failure details for %s", test_case_name)


def get_project_grade(test_cases,
                      total_points, base_case_points, extended_case_points) -> int:
    graded_points = total_points
    for test_case in test_cases:
        (status, points_lost) = get_testcase_grade(test_case, base_case_points, extended_case_points)
        graded_points = graded_points - points_lost
    return graded_points


def get_testcase_grade(test_case, base_case_points, extended_case_points):
    test_case_name = str(test_case.getAttribute("name"))
    points_lost = 0
    status = "OK"
    if test_case.getElementsByTagName("failure") or \
            test_case.getElementsByTagName("error"):
        status = "FAIL"
        points_lost = extended_case_points
        if test_case_name.startswith("base_"):
            points_lost = base_case_points
    return (status, points_lost)


# <testsuite name="edu.vt.cs.cs5254.multiquiz.QuizActivityTest"
# tests="17" failures="5" errors="0" skipped="0"
# time="46.357" timestamp="2021-01-30T14:50:06" hostname="localhost">


def first3Lines(string: str) -> str:
    result = "";
    for string in string.splitlines(False)[0:3]:
        result += "\t"
        result += string
        result += "\n"
    return result


if __name__ == "__main__":
    main()
