import re

cid_map = {
    "(cid:41)": "F",
    "(cid:50)": "O",
    "(cid:53)": "R",
    "(cid:48)": "M",
    "(cid:36)": "A",
    "(cid:40)": "E",
    "(cid:100)": "Ç",
    "(cid:173)": "Ã",
    "(cid:174)": "Õ",
    "(cid:11)": "(",
    "(cid:12)": ")",
    "(cid:91)": "x",
    "(cid:3)": " ",
    "(cid:20)": "1",
    "(cid:21)": "2",
    "(cid:22)": "3",
    "(cid:23)": "4",
    "(cid:24)": "5",
    "(cid:25)": "6",
    "(cid:26)": "7",
    "(cid:27)": "8",
    "(cid:28)": "9",
    "(cid:19)": "0"
}

def decode_cid(text):
    for cid, char in cid_map.items():
        text = text.replace(cid, char)
    # Remove any remaining CIDs
    text = re.sub(r"\(cid:\d+\)", "", text)
    return text

def main():
    encoded = "(cid:41)(cid:50)(cid:53)(cid:48)(cid:36)(cid:3)(cid:40)(cid:3)(cid:36)(cid:53)(cid:48)(cid:36)(cid:100)(cid:173)(cid:50)(cid:3)(cid:11)(cid:20)(cid:91)(cid:12)"
    decoded = decode_cid(encoded)
    print(f"Decoded: {decoded}")

if __name__ == "__main__":
    main()
