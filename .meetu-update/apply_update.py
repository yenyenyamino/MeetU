from __future__ import annotations

import base64
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UPDATE_DIR = ROOT / ".meetu-update"
INDEX_PATH = ROOT / "index.html"
WORKFLOW_PATH = ROOT / ".github" / "workflows" / "apply-meetu-update.yml"

IMAGE_TARGETS = {
    "fujiwara": ROOT / "assets" / "characters" / "fujiwara-rin-202608.jpg",
    "sill": ROOT / "assets" / "characters" / "sill-202608.jpg",
    "nanshuo": ROOT / "assets" / "characters" / "nanshuo-202608.jpg",
}


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected exactly one match, found {count}")
    return text.replace(old, new, 1)


def restore_images() -> None:
    for stem, target in IMAGE_TARGETS.items():
        parts = sorted(UPDATE_DIR.glob(f"{stem}.part*"))
        if not parts:
            raise RuntimeError(f"No upload chunks found for {stem}")
        encoded = "".join(part.read_text(encoding="ascii").strip() for part in parts)
        data = base64.b64decode(encoded, validate=True)
        if len(data) < 100_000:
            raise RuntimeError(f"Decoded image for {stem} is unexpectedly small")
        if not data.startswith(b"\xff\xd8\xff"):
            raise RuntimeError(f"Decoded image for {stem} is not a JPEG")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)


def patch_index() -> None:
    text = INDEX_PATH.read_text(encoding="utf-8")

    css_anchor = """        .sub-title {
            max-width: 720px;
            margin: 0 auto;
            color: var(--text-muted);
            font-size: clamp(0.76rem, 1.2vw, 0.88rem);
            font-weight: 300;
            letter-spacing: 0.32em;
            line-height: 2.35;
        }
"""
    css_insert = css_anchor + """
        .common-room-button {
            display: inline-flex;
            min-height: 48px;
            margin-top: 28px;
            padding: 0 24px;
            align-items: center;
            justify-content: center;
            border: 1px solid rgba(194, 184, 163, 0.28);
            color: rgba(255, 255, 255, 0.72);
            background: rgba(194, 184, 163, 0.035);
            font-family: var(--font-sans);
            font-size: 0.68rem;
            font-weight: 500;
            letter-spacing: 0.28em;
            cursor: pointer;
            transition:
                border-color 300ms ease,
                color 300ms ease,
                background 300ms ease,
                transform 500ms var(--ease-cinema);
        }

        .common-room-button:hover,
        .common-room-button:focus-visible {
            border-color: var(--line-strong);
            color: #fff;
            background: var(--accent-faint);
            outline: none;
            transform: translateY(-2px) scale(1.015);
        }
"""
    text = replace_once(text, css_anchor, css_insert, "common-room button CSS")

    quote_anchor = """        .modal-quote {
            margin: 24px 0 0;
            padding-left: 18px;
            border-left: 1px solid rgba(194, 184, 163, 0.38);
            color: rgba(255, 255, 255, 0.68);
            font-size: clamp(0.82rem, 2vw, 0.94rem);
            font-style: italic;
            font-weight: 300;
            letter-spacing: 0.08em;
            line-height: 2;
        }
"""
    quote_replacement = """        .modal-quote {
            margin: 24px 0 0;
            padding-left: 18px;
            border-left: 1px solid rgba(194, 184, 163, 0.38);
            color: rgba(255, 255, 255, 0.68);
            font-size: clamp(0.82rem, 2vw, 0.94rem);
            font-style: italic;
            font-weight: 300;
            letter-spacing: 0.08em;
            line-height: 2;
            white-space: pre-line;
        }
"""
    text = replace_once(text, quote_anchor, quote_replacement, "multiline modal quote")

    mobile_anchor = """            .sub-title {
                letter-spacing: 0.18em;
            }
"""
    mobile_replacement = mobile_anchor + """
            .common-room-button {
                min-height: 46px;
                margin-top: 24px;
                padding-inline: 20px;
                letter-spacing: 0.22em;
            }
"""
    text = replace_once(text, mobile_anchor, mobile_replacement, "mobile common-room button CSS")

    header_anchor = """        <p class="sub-title">
            七個迥異的靈魂，<br>
            他們共用著這座公寓，各自又有那些故事。
        </p>
"""
    header_replacement = header_anchor + """        <button class="common-room-button" id="common-room-button" type="button" aria-haspopup="dialog" aria-controls="resident-modal">
            寓見 MeetU
        </button>
"""
    text = replace_once(text, header_anchor, header_replacement, "main common-room button")

    script_anchor = """    <script>
        const residents = [
"""
    common_room = """    <script>
        const commonRoom = {
            id: "common-room",
            room: "ROOM 102 · COMMON ROOM",
            name: "寓見 MeetU",
            modalKicker: "寓見 MeetU",
            modalTitle: "ROOM 102 · COMMON ROOM",
            quote: "「New tenant？」\n目黑曉抬眼看了你一會，低頭翻找了下，將入住登記表遞了過來。\n「嗯，新來的，今天入住。」\n「歡迎來到寓見。」",
            entrances: [
                {
                    type: "gpts",
                    url: "https://chatgpt.com/g/g-6a6f7c3fbd6081919e2d0aa4d25ef412-yu-jian-meet-u"
                },
                {
                    type: "gem",
                    lockId: "meetu-common-room",
                    gem: {
                        salt: "psc1AQ7FLNgT8YvtDRqlfQ==",
                        iv: "rs5BM9YWRdNvCn4r",
                        cipher: "5N30ZYpSRyO6jbXGVQzHxY+yoDY/sN3L5KW7R19mq8cgz+Q+YcQHGy+fkxS8zMG62fBNUuin/teXkaWd0s8t9VtJUGkZK0Q94x8LgvQ14onldu/X4HuqYL6ZGQ==",
                        iterations: 210000
                    }
                }
            ]
        };

        const residents = [
"""
    text = replace_once(text, script_anchor, common_room, "common-room data")

    meetu_entries = """                    {
                        type: "gpts",
                        label: "Meet U · GPT",
                        url: "https://chatgpt.com/g/g-6a6f7c3fbd6081919e2d0aa4d25ef412-yu-jian-meet-u"
                    },
                    {
                        type: "gem",
                        label: "Meet U · GEM",
                        lockId: "meguro-meet-u",
                        gem: {
                            salt: "psc1AQ7FLNgT8YvtDRqlfQ==",
                            iv: "rs5BM9YWRdNvCn4r",
                            cipher: "5N30ZYpSRyO6jbXGVQzHxY+yoDY/sN3L5KW7R19mq8cgz+Q+YcQHGy+fkxS8zMG62fBNUuin/teXkaWd0s8t9VtJUGkZK0Q94x8LgvQ14onldu/X4HuqYL6ZGQ==",
                            iterations: 210000
                        }
                    },
"""
    text = replace_once(text, meetu_entries, "", "remove MeetU entries from Meguro")

    text = replace_once(text, '                quote: "「閉上你的嘴，滾開。」",', '                quote: "「太近了，請停在那裡就好。」",', "Fujiwara quote")
    text = replace_once(text, '                image: "./assets/characters/fujiwara-rin.png",', '                image: "./assets/characters/fujiwara-rin-202608.jpg",', "Fujiwara image")
    text = replace_once(text, '                image: "./assets/characters/sill.png",', '                image: "./assets/characters/sill-202608.jpg",', "Sill image")
    text = replace_once(text, '                image: "./assets/characters/nanshuo.png",', '                image: "./assets/characters/nanshuo-202608.jpg",', "Nanshuo image")

    text = replace_once(text, '        const grid = document.getElementById("apartment-grid");\n', '        const commonRoomButton = document.getElementById("common-room-button");\n        const grid = document.getElementById("apartment-grid");\n', "common-room button DOM reference")
    text = replace_once(text, """            modalRoom.textContent = resident.room;
            modalName.textContent = resident.name;
""", """            modalRoom.textContent = resident.modalKicker || resident.room;
            modalName.textContent = resident.modalTitle || resident.name;
""", "common-room modal title overrides")
    text = replace_once(text, '        modalClose.addEventListener("click", closeResident);\n', '        commonRoomButton.addEventListener("click", () => openResident(commonRoom));\n        modalClose.addEventListener("click", closeResident);\n', "common-room button event")

    INDEX_PATH.write_text(text, encoding="utf-8", newline="\n")


def clean_bootstrap_files() -> None:
    if WORKFLOW_PATH.exists():
        WORKFLOW_PATH.unlink()
    shutil.rmtree(UPDATE_DIR)


def main() -> None:
    restore_images()
    patch_index()
    clean_bootstrap_files()


if __name__ == "__main__":
    main()
