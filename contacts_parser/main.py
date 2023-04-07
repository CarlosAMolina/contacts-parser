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


class OnlyOneValueAllowedError(ValueError):
    def __init__(self, *args: object):
        print(*args)
        super().__init__(*args)


class Contact:
    STR_EMPTY = ""
    INT_EMPTY = 0

    def __init__(self) -> None:
        self._email: tp.Optional[str] = None
        self._name: str = self.STR_EMPTY
        self._family_name: str = self.STR_EMPTY
        self._note: tp.Optional[str] = None
        self._phone: int = self.INT_EMPTY

    def __repr__(self) -> str:
        return f"""
Contact:
- email={self.email}
- _name={self._name}
- _family_name={self._family_name}
- name={self.name}
- note={self.note}
- phone={self.phone}
"""

    @property
    def email(self) -> tp.Optional[str]:
        return self._email

    @email.setter
    def email(self, value: str):
        if self._is_email_initialized():
            raise OnlyOneValueAllowedError(self)
        else:
            value = self._get_str_to_set(value)
            if re.search(r".+@.+\..+", str(value)) is None:
                raise ValueError
            self._email = value

    def _is_email_initialized(self) -> bool:
        return self._email is not None

    @property
    def name(self) -> str:
        if self._is_name_initialized():
            return self._get_name_to_show()
        raise ValueError

    def _get_name_to_show(self) -> str:
        if self._is_name_initialized() and self._is_family_name_initialized():
            if self._name in self._family_name:
                return self._family_name
            elif self._family_name in self._name:
                return self._name
            else:
                # Sometimes the name contains a `;` and the order of the strings is different than in family_name.
                # Example
                # N:aparato;dentista;;;
                # FN:dentista aparato
                name = self._name
                if ";" in name:
                    name = self._name.replace(";", " ")
                name_list = name.split(" ")
                family_name_list = self._family_name.split(" ")
                if all(element in family_name_list for element in name_list) or all(
                    element in name_list for element in family_name_list
                ):
                    if len(name_list) > len(family_name_list):
                        return name
                    else:
                        return self._family_name
                else:
                    raise OnlyOneValueAllowedError
        else:
            raise ValueError

    @name.setter
    def name(self, value: str):
        if self._is_name_initialized():
            raise OnlyOneValueAllowedError(self)
        else:
            value = self._get_str_to_set(value)
            self._name = value

    def _is_name_initialized(self) -> bool:
        return self._name != self.STR_EMPTY

    def set_family_name(self, value: str):
        if self._is_family_name_initialized():
            raise OnlyOneValueAllowedError(self)
        else:
            value = self._get_str_to_set(value)
            self._family_name = value

    def _is_family_name_initialized(self) -> bool:
        return self._family_name != self.STR_EMPTY

    def _get_str_to_set(self, value: str) -> str:
        value = value.strip()
        if len(value) == 0:
            raise ValueError
        return value

    @property
    def note(self) -> tp.Optional[str]:
        return self._note

    @note.setter
    def note(self, value: str):
        if self._is_note_initialized():
            raise OnlyOneValueAllowedError(self)
        else:
            value = self._get_str_to_set(value)
            self._note = value

    def _is_note_initialized(self) -> bool:
        return self._note is not None

    @property
    def phone(self) -> int:
        if self._is_phone_initialized():
            return self._phone
        raise ValueError

    def _is_phone_initialized(self) -> bool:
        return self._phone != self.INT_EMPTY

    @phone.setter
    def phone(self, value: str):
        value: int = self._get_phone_to_set(value)
        if self._is_phone_initialized() and self._phone != value:
            raise OnlyOneValueAllowedError(self)
        else:
            self._phone = value

    def _get_phone_to_set(self, value: str) -> int:
        value = self._get_str_to_set(value)
        if value.startswith("+"):
            value = value[1:]
        if value.startswith("34") and len(value) > 9:
            value = value[2:]
        return int(value)


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
        return quopri.decodestring(string).decode("utf-8")

    def _get_value_regex_findall(self, regex: str) -> str:
        regex_result = re.findall(regex, self._line)
        if len(regex_result) == 0:
            self.raise_not_parsed_error()
        result = regex_result[0][-1]
        return result

    def raise_not_parsed_error(self):
        raise ValueError(f"Not parsed: {self._line}")


class ContactToCsvExporter:
    def __init__(self, contact: Contact) -> None:
        self._contact = contact

    def export_to_csv(self):
        raise NotImplemented


class VcfFileParser:
    def get_contacts_in_file(self, file_path_name: str) -> tp.Iterator[Contact]:
        contacts_count = 0
        for line in FileReader().get_lines_in_file(file_path_name):
            line_parsed = VcfLineParser(line)
            if line_parsed.is_type("init_contact"):
                contacts_count += 1
                print(f"Init contact: {contacts_count}")
                contact = Contact()
            elif line_parsed.is_type("version"):
                pass
            elif line_parsed.is_type("name_encoded"):
                value = line_parsed.get_value("name_encoded")
                print(f"Name decoded: {value}")
                contact.name = value
            elif line_parsed.is_type("name"):
                value = line_parsed.get_value("name")
                print(f"Name: {value}")
                contact.name = value
            elif line_parsed.is_type("family_name"):
                value = line_parsed.get_value("family_name")
                print(f"Family name: {value}")
                contact.set_family_name(value)
            elif line_parsed.is_type("family_name_encoded"):
                value = line_parsed.get_value("family_name_encoded")
                print(f"Family name decoded: {value}")
                contact.set_family_name(value)
            elif line_parsed.is_type("phone"):
                value = line_parsed.get_value("phone")
                print(f"Phone: {value}")
                contact.phone = value
            elif line_parsed.is_type("note_encoded"):
                value = line_parsed.get_value("note_encoded")
                print(f"Note decoded: {value}")
                contact.note = value
            elif line_parsed.is_type("email"):
                value = line_parsed.get_value("email")
                print(f"Email: {value}")
                contact.email = value
            elif line_parsed.is_type("end_contact"):
                yield contact
            else:
                line_parsed.raise_not_parsed_error()

def run(file_path_name: str):
    for contact in VcfFileParser().get_contacts_in_file(file_path_name):
        print(contact)

if __name__ == "__main__":
    file_path_name = "/home/x/Downloads/Contactos.vcf"
    run(file_path_name)
