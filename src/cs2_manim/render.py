# TODO: Define chapter-level narration/music and visual asset licensing.
# RISK: FFmpeg concat requires uniform codec, dimensions, frame rate and time base.
# VERIFY: ffprobe every chapter and compilation; inspect output playable in CI.
"""Run isolated Manim scenes, produce chapter MP4 files and one compilation."""

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess


def run(command, **kwargs):
    return subprocess.run(command, check=True, **kwargs)


def duration(path):
    proc = run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
               capture_output=True, text=True)
    seconds = float(proc.stdout.strip())
    if seconds <= 0:
        raise ValueError(f"Zero-duration movie: {path}")
    return seconds


def clock(seconds):
    seconds = round(seconds)
    return f"{seconds // 3600:02d}:{seconds // 60 % 60:02d}:{seconds % 60:02d}"


def render(manifest_file, output, quality):
    manifest_file = Path(manifest_file).resolve()
    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    scene_file = Path(__file__).with_name("scenes.py").resolve()
    media = output / "_media"
    entries = []
    for chapter in manifest["chapters"]:
        slug = chapter["slug"]
        data_file = (manifest_file.parent / chapter["data_file"]).resolve()
        env = dict(os.environ, CS2_CHAPTER_FILE=str(data_file))
        quality_flag = {"low": "-ql", "medium": "-qm", "high": "-qh"}[quality]
        run(["manim", quality_flag, "--format=mp4", "--disable_caching",
             "--media_dir", str(media), "-o", slug,
             str(scene_file), "MarketChapter"], env=env)
        matches = list(media.rglob(slug + ".mp4"))
        if len(matches) != 1:
            raise RuntimeError(f"Expected a unique MP4 for {slug}: {matches}")
        chapter_movie = output / f"{slug}.mp4"
        shutil.copyfile(matches[0], chapter_movie)
        entries.append({"title": chapter["title"], "file": chapter_movie.name,
                        "seconds": duration(chapter_movie)})

    if not entries:
        raise ValueError("Manifest has no chapters")
    # Slugs are generated internally; filenames never include raw series names.
    concat_file = output / "_concat.txt"
    concat_file.write_text("".join(f"file '{entry['file']}'\n" for entry in entries),
                           encoding="utf-8")
    compilation = output / "CS2-Market-Compilation.mp4"
    run(["ffmpeg", "-nostdin", "-y", "-hide_banner", "-loglevel", "error",
         "-f", "concat", "-safe", "0", "-i", str(concat_file),
         "-c", "copy", "-movflags", "+faststart", str(compilation)])
    compilation_seconds = duration(compilation)

    timestamp = 0.0
    chapters = []
    for entry in entries:
        chapters.append(f"{clock(timestamp)} {entry['title']}")
        timestamp += entry["seconds"]
    (output / "chapters.txt").write_text("\n".join(chapters) + "\n", encoding="utf-8")
    (output / "report.json").write_text(
        json.dumps({"quality": quality, "chapters": entries,
                    "compilation": compilation.name,
                    "duration_seconds": compilation_seconds},
                   indent=2) + "\n", encoding="utf-8")
    print(f"Verified {len(entries)} chapter MP4s and {compilation}")


def main():
    parser = argparse.ArgumentParser(description="Render the CS2-Manim chapters")
    parser.add_argument("--manifest", default="build/manifest.json")
    parser.add_argument("--output", default="dist")
    parser.add_argument("--quality", choices=("low", "medium", "high"), default="low")
    args = parser.parse_args()
    render(args.manifest, args.output, args.quality)


if __name__ == "__main__":
    main()
