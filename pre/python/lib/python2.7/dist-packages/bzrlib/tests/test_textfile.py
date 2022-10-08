# Copyright (C) 2006 Canonical Ltd
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

from StringIO import StringIO

from bzrlib.errors import BinaryFile
from bzrlib.tests import TestCase, TestCaseInTempDir
from bzrlib.textfile import text_file, check_text_lines, check_text_path


class TextFile(TestCase):

    def test_text_file(self):
        s = StringIO('ab' * 2048)
        self.assertEqual(text_file(s).read(), s.getvalue())
        s = StringIO('a' * 1023 + '\x00')
        self.assertRaises(BinaryFile, text_file, s)
        s = StringIO('a' * 1024 + '\x00')
        self.assertEqual(text_file(s).read(), s.getvalue())

    def test_check_text_lines(self):
        lines = ['ab' * 2048]
        check_text_lines(lines)
        lines = ['a' * 1023 + '\x00']
        self.assertRaises(BinaryFile, check_text_lines, lines)


class TextPath(TestCaseInTempDir):

    def test_text_file(self):
        with file('boo', 'wb') as f: f.write('ab' * 2048)
        check_text_path('boo')
        with file('boo', 'wb') as f: f.write('a' * 1023 + '\x00')
        self.assertRaises(BinaryFile, check_text_path, 'boo')
