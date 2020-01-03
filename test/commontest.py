#
# Copyright 2019-2020 Ghent University
#
# This file is part of vsc-install,
# originally created by the HPC team of Ghent University (http://ugent.be/hpc/en),
# with support of Ghent University (http://ugent.be/hpc),
# the Flemish Supercomputer Centre (VSC) (https://www.vscentrum.be),
# the Flemish Research Foundation (FWO) (http://www.fwo.be/en)
# and the Department of Economy, Science and Innovation (EWI) (http://www.ewi-vlaanderen.be/en).
#
# https://github.com/hpcugent/vsc-install
#
# vsc-install is free software: you can redistribute it and/or modify
# it under the terms of the GNU Library General Public License as
# published by the Free Software Foundation, either version 2 of
# the License, or (at your option) any later version.
#
# vsc-install is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU Library General Public License
# along with vsc-install. If not, see <http://www.gnu.org/licenses/>.
#
"""
Tests for functionality in vsc.install.commentest

@author: Kenneth Hoste (Ghent University)
"""
import os
import sys

from mock import MagicMock, call
from vsc.install.testing import TestCase

from vsc.install.commontest import CommonTest, check_autogenerated_ci_config_file


class CommontestTest(TestCase):
    """Tests for functionality in vsc.install.commentest."""

    def test_check_autogenerated_ci_config_file(self):
        """Tests for check_autogenerated_ci_config_file function."""

        test_fn = 'Jenkinsfile'
        test_contents = "this just a test"

        # run checks in temporary directory, since we're creating files to test with
        os.chdir(self.tmpdir)

        # make very sure test file doesn't exist yet
        self.assertFalse(os.path.exists(test_fn))

        # we need to use MagickMock to create an instance of CommonTest without triggering running of tests;
        # unsafe=True is required because otherwise all calls to methods that start with 'assert'
        # raise an AttributeError...
        mocked_self = MagicMock(CommonTest, unsafe=True)

        if sys.version_info[0] >= 3:
            # if specified file doesn't exist, assertTrue is called with False
            # (and a FileNotFoundError is raised afterwards)
            self.assertErrorRegex(FileNotFoundError, '.*', check_autogenerated_ci_config_file,
                                  mocked_self, test_fn, test_contents)
        else:
            # if specified file doesn't exist, assertTrue is called with False (and an IOError is raised afterwards)
            self.assertErrorRegex(IOError, "No such file or directory", check_autogenerated_ci_config_file,
                                  mocked_self, test_fn, test_contents)
        mocked_self.assertTrue.assert_called_once_with(False)  # file existince check
        mocked_self.assertEqual.assert_not_called()
        mocked_self.assertNotEqual.assert_not_called()
        mocked_self.reset_mock()

        expected_error_msg = "Contents of Jenkinsfile does not match expected contents, "
        expected_error_msg += "you should run 'python -m vsc.install.ci' again to re-generate %s" % test_fn

        # check using existing test file => assertEqual should be called with found + expected contents
        open(test_fn, 'w').write('foobar')
        check_autogenerated_ci_config_file(mocked_self, test_fn, test_contents)
        mocked_self.assertTrue.assert_called_once_with(True)  # file existence check
        mocked_self.assertEqual.assert_called_once_with('foobar', test_contents, expected_error_msg)
        mocked_self.assertNotEqual.assert_not_called()
        mocked_self.reset_mock()

        # if file includes existing contents, those are passed to assertEqual
        open(test_fn, 'w').write(test_contents)
        check_autogenerated_ci_config_file(mocked_self, test_fn, test_contents)
        mocked_self.assertTrue.assert_called_once_with(True)  # file existence check
        mocked_self.assertEqual.assert_called_once_with(test_contents, test_contents, expected_error_msg)
        mocked_self.assertNotEqual.assert_not_called()
        mocked_self.reset_mock()

        # if a file named <file>.NOT_AUTOGENERATED_YET exists, then assertNotEqual is used,
        # since then contents *must* be different from expected contents
        expected_error_msg = "Found %(fn)s.NOT_AUTOGENERATED_YET, so contents of %(fn)s is expected " % {'fn': test_fn}
        expected_error_msg += "to be different from what vsc-install generates (but it's not!): this just a test"

        def check_ignore(pattern_check_result):
            """Helper function to test check_autogenerated_ci_config_file when ignore file is in place."""
            check_autogenerated_ci_config_file(mocked_self, test_fn, test_contents)
            # two calls to assertTrue: file existence check + vsc-install issue URL pattern check
            asserttrue_args = mocked_self.assertTrue.call_args_list
            self.assertEqual(len(asserttrue_args), 2)
            # first one is file existence check
            self.assertEqual(asserttrue_args[0], call(True))
            # second one is vsc-install issue URL pattern check: 1st unnamed arg should be pattern check result
            self.assertEqual(asserttrue_args[1][0][0], pattern_check_result)
            # no assertEqual, only assertNotEqual
            mocked_self.assertEqual.assert_not_called()
            mocked_self.assertNotEqual.assert_called_once_with(test_contents, test_contents, expected_error_msg)
            mocked_self.reset_mock()

        open(test_fn + '.NOT_AUTOGENERATED_YET', 'w').write('')
        check_ignore(False)

        open(test_fn + '.NOT_AUTOGENERATED_YET', 'w').write('https://github.com/hpcugent/vsc-install/issues/1234')
        check_ignore(True)