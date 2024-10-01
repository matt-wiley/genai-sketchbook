import json

def main():
    with open("session_data.json", "r") as f:
        data = json.load(f)

    with open("all_track_info.md", "a") as f:
        f.write("# TRACK 5: LEADERSHIP, STRATEGY & ROI \n")
        for session in data:
            f.write(f"---\n")
            f.write(f"## {session.get('title')}\n")
            f.write(f"{session.get('time')}\n\n")
            f.write(f"### Description: \n\n{session.get('description')}\n")
            f.write(f"### Speakers:\n\n")
            for speaker in session.get('speakers'):
                f.write(f"#### {speaker.get('name')}\n\n")
                f.write(f" > **{speaker.get('title')}**<br />\n")
                f.write(f" > *{speaker.get('company')}*<br />\n")
                f.write(f" > \n")
                f.write(f" > {speaker.get('bio')}\n")
            f.write("\n\n")


if __name__ == "__main__":
    main()