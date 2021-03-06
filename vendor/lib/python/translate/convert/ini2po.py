#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2007 Zuza Software Foundation
#
# This file is part of translate.
#
# translate is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# translate is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

"""Convert .ini files to Gettext PO localization files.

See: http://docs.translatehouse.org/projects/translate-toolkit/en/latest/commands/ini2po.html
for examples and usage instructions.
"""

import sys

from translate.storage import po


class ini2po:
    """convert a .ini file to a .po file for handling the translation..."""

    def convert_store(self, input_store, duplicatestyle="msgctxt"):
        """converts a .ini file to a .po file..."""
        output_store = po.pofile()
        output_header = output_store.header()
        output_header.addnote("extracted from %s" % input_store.filename, "developer")

        for input_unit in input_store.units:
            output_unit = self.convert_unit(input_unit, "developer")
            if output_unit is not None:
                output_store.addunit(output_unit)
        output_store.removeduplicates(duplicatestyle)
        return output_store

    def merge_store(self, template_store, input_store, blankmsgstr=False, duplicatestyle="msgctxt"):
        """converts two .ini files to a .po file..."""
        output_store = po.pofile()
        output_header = output_store.header()
        output_header.addnote("extracted from %s, %s" % (template_store.filename, input_store.filename), "developer")

        input_store.makeindex()
        for template_unit in template_store.units:
            origpo = self.convert_unit(template_unit, "developer")
            # try and find a translation of the same name...
            template_unit_name = "".join(template_unit.getlocations())
            if template_unit_name in input_store.locationindex:
                translatedini = input_store.locationindex[template_unit_name]
                translatedpo = self.convert_unit(translatedini, "translator")
            else:
                translatedpo = None
            # if we have a valid po unit, get the translation and add it...
            if origpo is not None:
                if translatedpo is not None and not blankmsgstr:
                    origpo.target = translatedpo.source
                output_store.addunit(origpo)
            elif translatedpo is not None:
                print >> sys.stderr, "error converting original ini definition %s" % origpo.name
        output_store.removeduplicates(duplicatestyle)
        return output_store

    def convert_unit(self, input_unit, commenttype):
        """Converts a .ini unit to a .po unit. Returns None if empty
        or not for translation."""
        if input_unit is None:
            return None
        # escape unicode
        output_unit = po.pounit(encoding="UTF-8")
        output_unit.addlocation("".join(input_unit.getlocations()))
        output_unit.source = input_unit.source
        output_unit.target = ""
        return output_unit


def convertini(input_file, output_file, template_file, pot=False, duplicatestyle="msgctxt", dialect="default"):
    """Reads in *input_file* using ini, converts using :class:`ini2po`,
    writes to *output_file*."""
    from translate.storage import ini
    input_store = ini.inifile(input_file, dialect=dialect)
    convertor = ini2po()
    if template_file is None:
        output_store = convertor.convert_store(input_store, duplicatestyle=duplicatestyle)
    else:
        template_store = ini.inifile(template_file, dialect=dialect)
        output_store = convertor.merge_store(template_store, input_store, blankmsgstr=pot, duplicatestyle=duplicatestyle)
    if output_store.isempty():
        return 0
    output_file.write(str(output_store))
    return 1


def convertisl(input_file, output_file, template_file, pot=False, duplicatestyle="msgctxt", dialect="inno"):
    return convertini(input_file, output_file, template_file, pot=False, duplicatestyle="msgctxt", dialect=dialect)


def main(argv=None):
    from translate.convert import convert
    formats = {
               "ini": ("po", convertini), ("ini", "ini"): ("po", convertini),
               "isl": ("po", convertisl), ("isl", "isl"): ("po", convertisl),
               "iss": ("po", convertisl), ("iss", "iss"): ("po", convertisl),
              }
    parser = convert.ConvertOptionParser(formats, usetemplates=True, usepots=True, description=__doc__)
    parser.add_duplicates_option()
    parser.passthrough.append("pot")
    parser.run(argv)


if __name__ == '__main__':
    main()
