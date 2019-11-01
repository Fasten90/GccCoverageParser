
import unittest

from Run_GccCoverage_ForSourceFiles import gcov_info, get_line_data, regex_function_detect


class GccCoverageParser(unittest.TestCase):

    def test_gcov_line_data(self):
        # TODO: UnitTest
        """
              513:  871:    if ((str == NULL) || (value == NULL))
                -:  872:    {
            #####:  873:        return false;
        """
        test_gcov_datas = [
            ("      513:  871:    if ((str == NULL) || (value == NULL))",
             gcov_info.COVERED),
            (
            "        -:  872:    {",
            gcov_info.UNKNOWN
            ),
            (
            "    #####:  873:        return false;",
            gcov_info.UNCOVERED
            )
        ]

        for test_gcov_line in test_gcov_datas:
            test_data = test_gcov_line[0]
            expected_result = test_gcov_line[1]
            res = get_line_data(test_data)
            check_res = res[0]
            assert (check_res == expected_result)

    def test_function_detection_is_function(self):
        function_ok_list = \
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
        # not null lines is a test
        for line in function_ok_list.split("\n"):
            if line.strip():
                # Not null line
                # Be careful! Check the full line!
                res = regex_function_detect.match(line)
                assert (res)


    def test_function_detection_is_not_function(self):
        function_not_list = \
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
        # not null lines is a test
        for line in function_not_list.split("\n"):
            if line.strip():
                # Not null line
                # Be careful! Check the full line!
                res = regex_function_detect.match(line)
                assert (not res)


if __name__ == '__main__':
    unittest.main()
