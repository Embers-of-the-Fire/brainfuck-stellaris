#!/usr/bin/env python3

import argparse
from pathlib import Path


SUPPORTED = frozenset("><+-.[]")
INSTRUCTIONS = SUPPORTED | {","}


def translate(source: str) -> str:
    instructions = []
    open_brackets = []
    line = 1
    column = 0

    for character in source:
        if character == "\n":
            line += 1
            column = 0
            continue

        column += 1
        if character not in INSTRUCTIONS:
            continue
        if character == ",":
            raise ValueError(f"unsupported input instruction ',' at {line}:{column}")
        if character == "[":
            open_brackets.append((line, column))
        elif character == "]":
            if not open_brackets:
                raise ValueError(f"unmatched ']' at {line}:{column}")
            open_brackets.pop()

        instructions.append(character)

    if open_brackets:
        open_line, open_column = open_brackets[-1]
        raise ValueError(f"unmatched '[' at {open_line}:{open_column}")

    if not instructions:
        return """event_target:bf_vm_null = {
    save_global_event_target_as = bf_vm_code_head
    save_global_event_target_as = bf_vm_code_tail
}
"""

    lines = [
        "create_node = yes",
        "last_created_army = {",
        "    set_variable = {",
        "        which = bf_ll_value",
        f"        value = {ord(instructions[0])} # {instructions[0]}",
        "    }",
        "    save_global_event_target_as = bf_vm_code_head",
        "    save_event_target_as = t_bf_vm_code_cursor",
        "    event_target:bf_vm_null = {",
        "        save_global_event_target_as = bf_ll_prev@last_created_army",
        "        save_global_event_target_as = bf_ll_next@last_created_army",
        "    }",
        "}",
    ]

    for instruction in instructions[1:]:
        lines.extend(
            [
                "linked_list_extend_after = {",
                "    NODE = t_bf_vm_code_cursor",
                "    NULL = bf_vm_null",
                "}",
                "last_created_army = {",
                "    set_variable = {",
                "        which = bf_ll_value",
                f"        value = {ord(instruction)} # {instruction}",
                "    }",
                "}",
            ]
        )

    lines.extend(
        [
            "event_target:t_bf_vm_code_cursor = {",
            "    save_global_event_target_as = bf_vm_code_tail",
            "}",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Translate Brainfuck source into BFVM code-tape effects."
    )
    parser.add_argument("source", type=Path, help="UTF-8 Brainfuck source file")
    parser.add_argument("-o", "--output", type=Path, help="output effect file")
    arguments = parser.parse_args()

    try:
        source = arguments.source.read_text(encoding="utf-8")
        output = translate(source)
        if arguments.output is None:
            print(output, end="")
        else:
            arguments.output.write_text(output, encoding="utf-8")
    except (OSError, ValueError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
