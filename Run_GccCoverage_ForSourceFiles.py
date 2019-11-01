import glob
import subprocess
import os
import time
from enum import Enum
import re


# Note: Similar command shall be called all gcno file
# gcov --all-blocks --function-summaries --branch-probabilities --branch-counts --unconditional-branches CMakeFiles/FastenHomeAut.dir/Src/main.c.gcno

__COMMAND = "gcov"
__COMMAND_ARG = "--all-blocks --function-summaries --branch-probabilities --branch-counts --unconditional-branches"
__gcov_file_dir = "CMakeFiles/FastenHomeAut.dir/"


source_list = []


# PATH correction

# os.path.normpath()
cwd = os.path.normcase(os.path.normpath(os.getcwd()))
script_dir = os.path.normcase(os.path.normpath(os.path.dirname(__file__)))
cwd_is_changed = False

if cwd != script_dir:
    # Go down from /Tools/...
    os.chdir("../../")
    cwd_is_changed = True
    #os.chdir(script_dir)
    print("Working directory changed from: '{}' to '{}'".format(cwd, script_dir))

# Source list
source_list += glob.glob("Src/*.c")
source_list += glob.glob("Src/**/*.c")
source_list += glob.glob("Src/**/**/*.c")
#source_list += Path('Src').glob('**/*.c')


# TODO: Shall we append another?
print("Source list:")
prev_dir = ""
for src_item in source_list:
    src_item = src_item.replace("\\\\", "\\").replace("/", "\\")
    
    [dir, name] = src_item.rsplit("\\", 1)
    if dir != prev_dir:
        prev_dir = dir
        str_indent = "  " * src_item.count("\\")
        print(str_indent + "[" + dir + "]")
    
    str_indent = "  " * (src_item.count("\\") + 1)
    print(str_indent + "- " + name)



# For PATH correction
if cwd_is_changed:
    os.chdir(cwd)
    print("Working directory restored to: '{}'".format(cwd))
else:
    # TODO: Local mode?
    os.chdir("Out/CMakeBuild_GccCoverage/")
    print("Actual working directory: '{}'".format(os.getcwd()))


for source in source_list:
    # Call for all source file
    #print(source)
    # TODO: Argument
    source = source.replace("\\", "/")
    gcno_file_path = __gcov_file_dir + source + ".gcno"
    
    #print("file: '{}'".format(gcno_file_path))
    if os.path.exists(gcno_file_path):
        # Call
        command = __COMMAND + " " + __COMMAND_ARG + " " + gcno_file_path
        print("Command: {}".format(command))
        #subprocess.run(["ls", "-l"])
        #subprocess.run([__COMMAND, command_arg])
        return_code = subprocess.call(command, shell=True)
        # Debug code
        #print("  Return code: {}".format(return_code))
    else:
        # Do not call
        print("'{}' has no gcno file".format(source))


print("Wait...")
for i in range(5):
    print(".")
    time.sleep(1)


print("CWD:")
print(os.getcwd())
print()

print("----------------------------------------")
print("Start gcov parseing...")
print()
gcov_file_list = glob.glob("*.gcov")



# TODO: UnitTest
"""
      513:  871:    if ((str == NULL) || (value == NULL))
        -:  872:    {
    #####:  873:        return false;
"""

class gcov_info(Enum):
    ERROR = 0
    UNKNOWN = 1
    UNCOVERED = 2
    COVERED = 3

def get_line_data(line):
    try:
        [line_info, line_number, line_content] = line.split(":", 2)
    except IndexError:
        print("[ERROR]: Cannot parsed line: '{}'".format(line))
        return (gcov_info.ERROR, None, None)
    line_info = line_info.strip()
    line_number = int(line_number.strip())
    if line_info.isdigit():
        return (gcov_info.COVERED, int(line_info), line_number)
    elif "-" == line_info:
        return (gcov_info.UNKNOWN, None, line_number)
    elif "#####" == line_info:
        return (gcov_info.UNCOVERED, None, line_number)
    else:
        print("[ERROR]: gcov info could not recognize: '{}' at line {}.".format(line_info, line_number))
        return (gcov_info.ERROR, None, line_number)

# Function detection
#   Limitations:
#     more line declarated functions
#     MACRO FUNCTION

# TODO: Move unittest
# https://regex101.com/r/PgMQnh/2
"""
void function1(void)

void function2(void) {

void function3(int blabla)

void function4(int blabla) {

int function5(void)

int * function6(int bla1, int bla2)

INLINE_FUNCTION void function7(int blabla)

void function8 ( int * bla )

void function9 ( uint8_t * ehh, Type_ omg )

bool BUTTON_GetButtonState(ButtonType_t button)
"""

"""
Wrong unittest
/* Noooooooooooooo */
/* Do not accept because the empty () */
void function()

    IO_Output_SetStatus(IO_LED_Blue, IO_Output_Cmd_SetToggle);

    UNUSED_ARGUMENT(source);


    if (UnitTest_InvalidCnt)

    state = (HAL_GPIO_ReadPin(BUTTON_USER_GPIO_PORT, BUTTON_USER_GPIO_PIN) == GPIO_PIN_SET) ? true : false;


    else if (str[1] == 80)

    else if (circBuff->readCnt > circBuff->writeCnt)

    else if (!StrCmp("settime", argv[1]) && argc == 3)

    else if (Logic_Display_ActualState < AppType_Count)

    else if (TaskList[i].isRequestScheduling)

/* Commented line */
     *         Test data in end of buffer (overflow!)

"""

#regex_function_detect = re.compile(r"^[\w\* ]+ (?P<function_name>\w*) *\( *[\w\,\*\_ ]* *\)")
regex_function_detect = re.compile(r"^ *([\w]+[\w\* ]*) (?P<function_name>[^\(\=\? ]+) *\( *[^\)\=\>\<.]+ *\) *\{*$")

gcov_info_list = {}

def parse_gcov_file(file_path):
    with open(file_path, 'r') as file:
        print("Start gcov parseing: '{}'".format(file_path))
        file_name = file_path.split(".gcov")[0]
        gcov_info_list[file_name] = {}
        file_content = file.readlines()
        prev_func_exists = False
        prev_func_name = ""
        for i, line in enumerate(file_content):
            # Is detect function?
            try:
                line_try_parse_for_function = line.split(":", 2)[2]
            except IndexError:
                print("[ERROR]: Cannot parsed line: '{}' at line {}".format(line, i))
                continue
            actual_line_is_function_decl = regex_function_detect.match(line_try_parse_for_function)
            if actual_line_is_function_decl:
                # New function declaration, break the previous!
                function_name = actual_line_is_function_decl.group("function_name")
                # Check line data
                (line_info, line_data, line_number) = get_line_data(line)
                # line data is line number

                if not (line_info == gcov_info.COVERED or line_info == gcov_info.UNKNOWN or line_info.UNCOVERED):
                    print("[ERROR]: Cannot parsed line: '{}' at line {}".format(line, i))
                    continue
                function_is_covered = True if line_info == gcov_info.COVERED else False
                # TODO: line_data not used
                gcov_info_list[file_name][function_name] = {
                    "covered_function": function_is_covered,
                    "function_decl_line": line_number,
                    "coverage": []
                }

                # TODO: Check
                if prev_func_exists:
                    # New started
                    pass
                else:
                    # First started
                    prev_func_exists = True
                    pass
                print("Started new function declaration: '{}' at line '{}'".format(function_name, i+1))
                prev_func_name = function_name

            else:
                # Not Function declaration line, so branch or not necessary code parts
                if prev_func_exists:
                    # Important, check
                    # Check line
                    (line_info, line_data, line_number) = get_line_data(line)
                    if line_info == gcov_info.COVERED or gcov_info.UNCOVERED:
                        # Save information
                        branch_is_covered = True if line_info == gcov_info.COVERED else False
                        # TODO: line_data not used
                        gcov_info_list[file_name][prev_func_name]['coverage'].append((line_number, branch_is_covered))
                    else:
                        print("[ERROR]: Unknown status of line: '{}' at line {}".format(line, i))
                else:
                    # not in function, dont care, go out
                    pass

# Check all gcovs
for gcov_file in gcov_file_list:
    print(gcov_file)
    parse_gcov_file(gcov_file)

# Print gcov result
gcov_export_file = open("GccCoverage.txt", "w+")

def gcov_print(str):
    print(str)
    gcov_export_file.write(str + "\n")

for gcov_file in gcov_info_list:
    # Functions
    gcov_print("File: {}".format(gcov_file))
    for function in gcov_info_list[gcov_file]:
        gcov_print("  Function: {} at line {}".format(
            function,
            gcov_info_list[gcov_file][function]["function_decl_line"]))
        # Could print all dictionary, but not necessary, if the function has not covered
        if gcov_info_list[gcov_file][function]["covered_function"]:
            gcov_print("    " + "Tested")
            for branch_item in gcov_info_list[gcov_file][function]["coverage"]:
                gcov_print("      " + str(branch_item[0]) + ": " + str(branch_item[1]))
        else:
            gcov_print("    " + "Not tested")

gcov_export_file.close()
