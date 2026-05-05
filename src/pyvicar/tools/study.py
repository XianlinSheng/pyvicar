from dataclasses import dataclass, field
from abc import abstractmethod
import re


@dataclass
class SegType:
    name: str
    label: str

    @abstractmethod
    def decode(self, code):
        pass


@dataclass
class SegVal:
    label: str

    @abstractmethod
    def encode(self):
        pass


@dataclass
class SegTypeInt(SegType):
    def decode(self, code):
        pattern = re.compile(rf"^{self.label}([+-]?\d+)")
        m = pattern.match(code)

        if m:
            value = int(m.group(1))
            rest = code[m.end() :]
            return SegValInt(self.label, value), rest
        else:
            raise ValueError(
                f"Unrecognized code for an integer segment {self.name}, expected format {pattern.pattern} but encountered {code}"
            )


@dataclass
class SegValInt(SegVal):
    value: int

    def encode(self):
        return f"{self.label}{self.value}"


@dataclass
class SegTypeOptionalInt(SegType):
    off_value: int

    def decode(self, code):
        pattern = re.compile(rf"^{self.label}([+-]?\d+)")
        m = pattern.match(code)

        if m:
            value = int(m.group(1))
            rest = code[m.end() :]
            return SegValOptionalInt(self.label, True, value), rest
        else:
            return SegValOptionalInt(self.label, False, self.off_value), code


@dataclass
class SegValOptionalInt(SegVal):
    on: bool
    value: int

    def encode(self):
        return f"{self.label}{self.value}" if self.on else ""


@dataclass
class SegTypeSwitch(SegType):
    def decode(self, code):
        pattern = re.compile(rf"^{self.label}")
        m = pattern.match(code)

        if m:
            rest = code[m.end() :]
            return SegValSwitch(self.label, True), rest
        else:
            return SegValSwitch(self.label, False), code


@dataclass
class SegValSwitch(SegVal):
    on: bool

    def encode(self):
        return self.label if self.on else ""


@dataclass
class SegTypeChoice(SegType):
    choices: tuple[str]

    def decode(self, code):
        pattern = re.compile(rf"^{self.label}({'|'.join(self.choices)})")
        m = pattern.match(code)

        if m:
            choice = str(m.group(1))
            rest = code[m.end() :]
            return SegValChoice(self.label, choice), rest
        else:
            raise ValueError(
                f"Unrecognized code for a segment with choices {self.name}, expected format {pattern.pattern} but encountered {code}"
            )


@dataclass
class SegValChoice(SegVal):
    choice: str

    def encode(self):
        return f"{self.label}{self.choice}"


@dataclass
class SegTypeOptionalChoice(SegType):
    choices: tuple[str]
    off_choice: str

    def decode(self, code):
        pattern = re.compile(rf"^{self.label}({'|'.join(self.choices)})")
        m = pattern.match(code)

        if m:
            choice = str(m.group(1))
            rest = code[m.end() :]
            return SegValOptionalChoice(self.label, True, choice), rest
        else:
            return SegValOptionalChoice(self.label, False, self.off_choice), code


@dataclass
class SegValOptionalChoice(SegVal):
    on: bool
    choice: str

    def encode(self):
        return f"{self.label}{self.choice}" if self.on else ""


@dataclass
class StudyType:
    segs_t: list[SegType] = field(default_factory=list)

    @classmethod
    def make_empty(cls):
        return cls([])

    def add_int(self, name, label):
        self.segs_t.append(SegTypeInt(name, label))
        return self

    def add_optional_int(self, name, label, off_value=0):
        self.segs_t.append(SegTypeOptionalInt(name, label, off_value))
        return self

    def add_switch(self, name, label):
        self.segs_t.append(SegTypeSwitch(name, label))
        return self

    def add_optional(self, name, label, substudy_t):
        self.segs_t.append(SegTypeOptional(name, label, substudy_t))
        return self

    def add_choice(self, name, label, choices):
        self.segs_t.append(SegTypeChoice(name, label, choices))
        return self

    def add_optional_choice(self, name, label, choices, off_choice=""):
        self.segs_t.append(SegTypeOptionalChoice(name, label, choices, off_choice))
        return self

    def add_branch(self, name, label, mapping):
        self.segs_t.append(SegTypeBranch(name, label, mapping))
        return self

    def add_optional_branch(self, name, label, mapping, off_branch_substudy=None):
        if off_branch_substudy is None:
            off_branch_substudy = ("", StudyType())
        if isinstance(off_branch_substudy, str):
            off_branch_substudy = (off_branch_substudy, mapping[off_branch_substudy])
        self.segs_t.append(
            SegTypeOptionalBranch(name, label, mapping, off_branch_substudy)
        )
        return self

    def decode_self(self, code):
        rest = code
        studyv = StudyVal([])
        for segt in self.segs_t:
            val, rest = segt.decode(rest)
            studyv.segs_v.append(val)
            setattr(studyv, segt.name, val)
            setattr(studyv, f"{segt.name}_idx", len(studyv.segs_v) - 1)

        return studyv, rest

    def decode(self, code):
        studyv, rest = self.decode_self(code)
        if rest:
            raise ValueError(
                f"Code has redundant residue '{rest}' unspecified in the study type"
            )
        return studyv


@dataclass
class StudyVal:
    segs_v: list[SegVal]

    def encode(self):
        return "".join(v.encode() for v in self.segs_v)


@dataclass
class SegTypeBranch(SegType):
    mapping: dict[str, StudyType]

    def decode(self, code):
        pattern = re.compile(rf"^{self.label}")
        m = pattern.match(code)

        if m:
            rest = code[m.end() :]
        else:
            raise ValueError(
                f"Unrecognized code for a branch segment {self.name}, expected format {pattern.pattern} but encountered {code}"
            )

        pattern = re.compile(rf"^({'|'.join(self.mapping.keys())})")
        m = pattern.match(rest)

        if m:
            branch = str(m.group(1))
            rest = rest[m.end() :]
        else:
            raise ValueError(
                f"Unrecognized code for a branch segment {self.name}, expected format {pattern.pattern} for branch name but encountered {rest}"
            )

        substudy_t = self.mapping[branch]
        substudy, rest = substudy_t.decode_self(rest)

        return SegValBranch(self.label, branch, substudy), rest


@dataclass
class SegValBranch(SegVal):
    branch: str
    substudy: StudyVal

    def encode(self):
        return f"{self.label}{self.branch}{self.substudy.encode()}"


@dataclass
class SegTypeOptionalBranch(SegType):
    mapping: dict[str, StudyType]
    off_branch_substudy: tuple[str, StudyType]

    def decode(self, code):
        pattern = re.compile(rf"^{self.label}")
        m = pattern.match(code)

        if m:
            rest = code[m.end() :]
        else:
            return (
                SegValOptionalBranch(self.label, False, *self.off_branch_substudy),
                code,
            )

        pattern = re.compile(rf"^({'|'.join(self.mapping.keys())})")
        m = pattern.match(rest)

        if m:
            branch = str(m.group(1))
            rest = rest[m.end() :]
        else:
            return (
                SegValOptionalBranch(self.label, False, *self.off_branch_substudy),
                code,
            )

        substudy_t = self.mapping[branch]
        substudy, rest = substudy_t.decode_self(rest)

        return SegValOptionalBranch(self.label, True, branch, substudy), rest


@dataclass
class SegValOptionalBranch(SegVal):
    on: bool
    branch: str
    substudy: StudyVal

    def encode(self):
        return f"{self.label}{self.branch}{self.substudy.encode()}" if self.on else ""


@dataclass
class SegTypeOptional(SegType):
    substudy_t: StudyType

    def decode(self, code):
        pattern = re.compile(rf"^{self.label}")
        m = pattern.match(code)

        if m:
            rest = code[m.end() :]
            substudy_v, rest = self.substudy_t.decode_self(rest)
            return (
                SegValOptional(self.label, True, substudy_v),
                rest,
            )
        else:
            return SegValOptional(self.label, False, None), code


@dataclass
class SegValOptional(SegVal):
    on: bool
    substudy: StudyVal | None

    def encode(self):
        return f"{self.label}{self.substudy.encode()}" if self.on else ""
