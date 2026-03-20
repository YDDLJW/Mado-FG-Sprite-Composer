import struct
from PIL import Image

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def read_png_text_chunks(path):
    result = {}
    with open(path, "rb") as f:
        sig = f.read(8)
        if sig != PNG_SIGNATURE:
            return result

        while True:
            raw_len = f.read(4)
            if len(raw_len) < 4:
                break
            length = struct.unpack(">I", raw_len)[0]
            chunk_type = f.read(4)
            chunk_data = f.read(length)
            f.read(4)

            if chunk_type in (b"tEXt", b"iTXt", b"zTXt"):
                try:
                    if chunk_type == b"tEXt":
                        if b"\x00" in chunk_data:
                            key, value = chunk_data.split(b"\x00", 1)
                            key = key.decode("latin1", errors="ignore").strip()
                            value = value.decode("latin1", errors="ignore").strip()
                            result[key] = value

                    elif chunk_type == b"zTXt":
                        if b"\x00" in chunk_data:
                            key, rest = chunk_data.split(b"\x00", 1)
                            key = key.decode("latin1", errors="ignore").strip()
                            result[key] = rest.decode("latin1", errors="ignore").strip()

                    elif chunk_type == b"iTXt":
                        parts = chunk_data.split(b"\x00", 5)
                        if len(parts) >= 6:
                            key = parts[0].decode("utf-8", errors="ignore").strip()
                            text = parts[5].decode("utf-8", errors="ignore").strip()
                            result[key] = text
                except Exception:
                    pass

            if chunk_type == b"IEND":
                break
    return result


def get_png_info_text(path):
    text_map = {}
    try:
        with Image.open(path) as im:
            for k, v in im.info.items():
                if isinstance(v, bytes):
                    try:
                        v = v.decode("utf-8", errors="ignore")
                    except Exception:
                        v = str(v)
                text_map[str(k)] = str(v)
    except Exception:
        pass
    return text_map


def parse_pos_string(s):
    if not s:
        return None
    s = s.strip()

    if "pos," in s:
        idx = s.find("pos,")
        s = s[idx:]

    parts = [x.strip() for x in s.split(",")]
    if len(parts) >= 3 and parts[0] == "pos":
        try:
            x = int(parts[1])
            y = int(parts[2])
            result = {"x": x, "y": y}
            if len(parts) >= 7:
                try:
                    result["w"] = int(parts[3])
                    result["h"] = int(parts[4])
                    result["frames"] = int(parts[5])
                    result["com"] = parts[6]
                except Exception:
                    pass
            return result
        except Exception:
            return None
    return None


def get_image_position(path):
    candidates = []

    info_text = get_png_info_text(path)
    for k, v in info_text.items():
        candidates.append(v)
        candidates.append(f"{k}\x00{v}")

    chunk_text = read_png_text_chunks(path)
    for k, v in chunk_text.items():
        candidates.append(v)
        candidates.append(f"{k}\x00{v}")

    try:
        with open(path, "rb") as f:
            raw = f.read()
            idx = raw.find(b"pos,")
            if idx != -1:
                tail = raw[idx:idx + 128]
                try:
                    candidates.append(tail.decode("latin1", errors="ignore"))
                except Exception:
                    pass
    except Exception:
        pass

    for c in candidates:
        parsed = parse_pos_string(c)
        if parsed:
            return parsed

    return {"x": 0, "y": 0}