from collections import namedtuple
from packaging.specifiers import SpecifierSet
from packaging.version import Version

import resolvelib

spec = """
first 1.0.0
    second == 1.0.0
first 2.0.0
    second == 2.0.0
    third == 1.0.0
first 3.0.0
    second == 3.0.0
    third == 2.0.0
second 1.0.0
    third == 1.0.0
second 2.0.0
    third == 2.0.0
second 3.0.0
    third == 3.0.0
third 1.0.0
third 2.0.0
third 3.0.0
"""


class Requirement(namedtuple("Requirement", "name spec")):  # noqa
    def __repr__(self):
        return "Requirement({name}{spec})".format(
            name=self.name, spec=self.spec
        )


class Candidate(namedtuple("Candidate", "name version")):  # noqa
    def __repr__(self):
        return "Candidate({name}, {version})".format(
            name=self.name, version=self.version
        )


def splitstrip(s, parts):
    return [item.strip() for item in s.strip().split(maxsplit=parts - 1)]


def read_spec(lines):
    candidates = {}
    latest = None
    for line in lines:
        if not line or line.startswith("#"):
            continue
        if not line.startswith(" "):
            name, version = splitstrip(line, 2)
            version = Version(version)
            latest = Candidate(name, version)
            candidates[latest] = set()
        else:
            if latest is None:
                raise RuntimeError(
                    "Spec has dependencies before first candidate"
                )
            name, spec = splitstrip(line, 2)
            spec = SpecifierSet(spec)
            candidates[latest].add(Requirement(name, spec))
    return candidates


class Provider(resolvelib.AbstractProvider):
    def __init__(self, spec):
        self.candidates = read_spec(spec)

    def identify(self, dependency):
        return dependency[0]

    def get_preference(self, resolution, candidates, information):
        return len(candidates)

    def find_matches(self, requirements):
        for candidate in sorted(self.candidates, reverse=True):
            if all(self.is_satisfied_by(r, candidate) for r in requirements):
                yield candidate

    def is_satisfied_by(self, requirement, candidate):
        return (
            candidate.name == requirement.name
            and candidate.version in requirement.spec
        )

    def get_dependencies(self, candidate):
        return self.candidates[candidate]


class Reporter(resolvelib.BaseReporter):
    def starting(self):
        print("starting()")

    def starting_round(self, index):
        print(f"starting_round({index})")

    def ending_round(self, index, state):
        print(f"ending_round({index}, ...)")

    def ending(self, state):
        print("ending(...)")

    def adding_requirement(self, requirement, parent):
        print(f"  adding_requirement({requirement}, {parent})")

    def backtracking(self, candidate):
        print(f"  backtracking({candidate})")

    def pinning(self, candidate):
        print(f"  pinning({candidate})")


def print_result(result):
    for k, v in result.mapping.items():
        print(f"{k}: {v}")


if __name__ == "__main__":
    from pprint import pprint

    provider = Provider(spec.splitlines())

    root_reqs = [Requirement("first", SpecifierSet())]

    resolver = resolvelib.Resolver(provider, Reporter())
    result = resolver.resolve(root_reqs)

    pprint(result.mapping)
