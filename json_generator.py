# garbage file for json generation
# on git in case the language gets more complex

import json
def main():
    to_dump = {}
    to_dump["symbols"] = []
    symbols = """  ?     SYMB_TERNARY_START
                   :     SYMB_COLON
                   !==   SYMB_XOR
                   !=    SYMB_XOR
                   !     SYMB_NOT
                   ~^    SYMB_XNOR
                   ~     SYMB_NOT
                   &&    SYMB_AND
                   &     SYMB_AND
                   ||    SYMB_OR
                   |     SYMB_OR
                   ^~    SYMB_XNOR
                   ^     SYMB_XOR
                   ===   SYMB_XNOR
                   ==    SYMB_XNOR
                   =     SYMB_EQ
                   <->   SYMB_XNOR
                   ->    SYMB_ARROW
                   ;     SYMB_SEMICOLON
                   (     SYMB_LEFT_PAREN
                   )     SYMB_RIGHT_PAREN
                   ,     SYMB_COMMA
                   *     SYMB_STAR
                   begin SYMB_BEGIN
                   end   SYMB_END
                   0     SYMB_ZERO
                   1     SYMB_ONE"""
    for line in symbols.splitlines():
        # generate split
        split = [x.strip() for x in line.strip().split(" ") if len(x) > 0 and not x.isspace()]

        if len(split) != 2:
            raise ValueError(f'Couldn\'t find valid split for line "{line}"')

        to_dump["symbols"].append({"symbol":split[0], "token":split[1]})

    to_dump["comment"] = [{"symbol":"/*", "token":"COMMENT_ML_START"},
                          {"symbol":"*/", "token":"COMMENT_ML_END"},
                          {"symbol":"//", "token":"COMMENT_SL"}]

    to_dump["regex"] = [{"match":r'\$([A-Za-z_][A-Za-z0-9_]*)\b', "token":"KEYWORD"},
                        {"match":r'([A-Za-z_][A-Za-z0-9_]*)\b', "token":"VARIABLE"}]
    print(json.dumps(to_dump, indent="  "))

if __name__ == "__main__":
    main()