from Run_GccCoverage_ForSourceFiles import gcov_info, get_line_data

import unittest


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


if __name__ == '__main__':
    unittest.main()
