#! /bin/bash
# Exercise maclookup.py CLI interface.

errors=0
logfile="test.log"


# Command to be tested.
cmd="./maclookup.py"

# Test list.  Eac
testList=(
  #Name         Status  Args
  "Normal"      "0"    "8c:85:90:48:90:0e --key=at_BXvpv8y2ypYtWCZUVsZS5JV26rOvv"
  "Invalid MAC" "19"   "85:90:48:90:0e --key=at_BXvpv8y2ypYtWCZUVsZS5JV26rOvv"
  "Invalid Key" "5"    "8c:85:90:48:90:0e --key=BXvpv8y2ypYtWCZUVsZS5JV26rOvv"
  "No Key"      "2"    "8c:85:90:48:90:0e"
  "No Args"     "2"    ""
  ""
)

echo "Starting maclookup tests"
rm -rf ${logfile}

#
# Perform validation tests
#
i=0
test=1
testname=${testList[((i++))]}
while [ -n  "$testname" ]; do
    result=${testList[((i++))]}
    args=${testList[((i++))]}

    echo "${cmd} ${args}" >> ${logfile}

    (${cmd} ${args}  &>> ${logfile})
    rc=$?
    if [ "$rc" != "$result" ]; then
        ((errors++))
        echo "Test ${test} ${testname}: failed: status ${rc} should be ${result}" >> ${logfile}
        echo "Test ${test} ${testname}: failed: status ${rc} should be ${result}"
    else
        echo "Test ${test} ${testname}: passed" >> ${logfile}
        echo "Test ${test} ${testname}: passed"
    fi
    echo "" >> ${logfile}

    # On to next test
    ((test++))
    testname=${testList[((i++))]}
done

#
# Print the validation test summary
#
echo 
if [ $errors -ne 0 ]; then
    echo "** Validation tests failed, ${errors} error(s)" >> ${logfile}
    echo "** Validation tests failed, ${errors} error(s)"
    exit 1
else
    echo "** Validation tests completed successfully" >> ${logfile}
    echo "** Validation tests completed successfully"
    exit 0
fi