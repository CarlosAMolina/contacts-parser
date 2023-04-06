import quopri
import os.path
import re
import typing as tp


class FileReader:
    def get_lines_in_file(self, file: str) -> tp.Iterator[str]:
        self._assert_is_file(file)
        with open(file, "r") as f:
            for line in f.read().splitlines():
                if len(line) != 0:
                    yield (line)

    def _assert_is_file(self, file: str):
        if not os.path.isfile(file):
            raise FileNotFoundError(file)

class VcfLineParser:
    regexs = {
        "init_contact": r"^BEGIN:VCARD$",
        "version": r"^VERSION:(\d+\.\d+)$",
        "name": r"^N:;?(.*?);{2,3}$",
        "name_encoded": r"^N;CHARSET=UTF-8;ENCODING=QUOTED-PRINTABLE:;?(.*?);*$",
        "family_name": r"^FN:(.*?)$",
        "family_name_encoded": r"^FN;CHARSET=UTF-8;ENCODING=QUOTED-PRINTABLE:(.*?)$",
        "phone": r"^TEL;(CELL|HOME|X-Casa):\+?(\d+)$",
        "note_encoded": r"^NOTE;(CHARSET=UTF-8;)?ENCODING=QUOTED-PRINTABLE:(.*?)$",
        "email": r"^EMAIL;HOME:(.*?)$",
        "end_contact": r"^END:VCARD$",
    }

    def __init__(self, line: str) -> None:
        self._line = line

    def is_type(self, regex_key: str) -> bool:
        return self._is_regex_matched(self.regexs[regex_key])

    def _is_regex_matched(self, regex: str) -> bool:
        return re.search(regex, self._line) is not None

    def get_value(self, regex_key: str) -> str:
        if regex_key in ["name", "family_name", "email"]:
            return self._get_value_regex_search(self.regexs[regex_key])
        elif regex_key in ["name_encoded", "family_name_encoded"]:
            result = self._get_value_regex_search(self.regexs[regex_key])
            return self._get_decoded(result)
        elif regex_key in ["note_encoded"]:
            result = self._get_value_regex_findall(self.regexs[regex_key])
            return self._get_decoded(result)
        elif regex_key in ["phone"]:
            return self._get_value_regex_findall(self.regexs[regex_key])
        else:
            self.raise_not_parsed_error()

    def _get_value_regex_search(self, regex: str) -> str:
        regex_result = re.search(regex, self._line)
        if regex_result is None:
            self.raise_not_parsed_error()
        result = regex_result.group(1)
        return result

    def _get_decoded(self, string: str) -> str:
        return quopri.decodestring(string).decode('utf-8')

    def _get_value_regex_findall(self, regex: str) -> str:
        regex_result = re.findall(regex, self._line)
        if len(regex_result) == 0:
            self.raise_not_parsed_error()
        result = regex_result[0][-1]
        return result

    def raise_not_parsed_error(self):
        raise ValueError(f"Not parsed: {self._line}")


class VcfFileParser:
    def parse_file(self, file_path_name: str):
        contacts_count = 0
        for line in FileReader().get_lines_in_file(file_path_name):
            line_parsed = VcfLineParser(line)
            if line_parsed.is_type("init_contact"):
                contacts_count += 1
                print(f"Init contact: {contacts_count}")
            elif line_parsed.is_type("version"):
                pass
            elif line_parsed.is_type("name_encoded"):
                value = line_parsed.get_value("name_encoded")
                print(f"Name decoded: {value}")
            elif line_parsed.is_type("name"):
                value = line_parsed.get_value("name")
                print(f"Name: {value}")
            elif line_parsed.is_type("family_name"):
                value = line_parsed.get_value("family_name")
                print(f"Family name: {value}")
            elif line_parsed.is_type("family_name_encoded"):
                value = line_parsed.get_value("family_name_encoded")
                print(f"Family name decoded: {value}")
            elif line_parsed.is_type("phone"):
                value = line_parsed.get_value("phone")
                print(f"Phone: {value}")
            elif line_parsed.is_type("note_encoded"):
                value = line_parsed.get_value("note_encoded")
                print(f"Note decoded: {value}")
            elif line_parsed.is_type("email"):
                value = line_parsed.get_value("email")
                print(f"Email: {value}")
            elif line_parsed.is_type("end_contact"):
                print()
            else:
                line_parsed.raise_not_parsed_error()
        print(f"Contacts count: {contacts_count}")


if __name__ == "__main__":
    file_path_name = "/home/x/Downloads/Contactos.vcf"
    VcfFileParser().parse_file(file_path_name)

