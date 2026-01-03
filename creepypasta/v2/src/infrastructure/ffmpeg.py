"""
FFmpeg utilities for video generation.
"""

import logging
from pathlib import Path

import ffmpeg

logger = logging.getLogger(__name__)


def get_audio_duration(audio_path: Path) -> float:
    """Get duration of audio file in seconds."""
    probe = ffmpeg.probe(str(audio_path))
    return float(probe["format"]["duration"])


def create_intro_stream(
    title: str,
    duration: float,
    fade_duration: float,
    width: int,
    height: int,
    framerate: int,
    font_path: str,
    title_font_size: int,
):
    """Create black screen with centered title that fades in."""
    stream = ffmpeg.input(
        f"color=c=black:s={width}x{height}:r={framerate}:d={duration}",
        f="lavfi",
    )

    # Title text (centered, appears after fade starts)
    stream = stream.filter(
        "drawtext",
        fontfile=font_path,
        text=title,
        fontcolor="white",
        fontsize=title_font_size,
        x="(w-text_w)/2",
        y="(h-text_h)/2",
    )

    # Fade in the intro
    stream = stream.filter("fade", type="in", start_time=0, duration=fade_duration)

    stream = stream.filter(
        "scale", w=width, h=height, force_original_aspect_ratio="increase"
    )
    stream = stream.filter("format", "yuv420p")

    return stream


def create_image_stream(
    image_path: Path,
    duration: float,
    fade_duration: float,
    width: int,
    height: int,
    framerate: int,
):
    """Create image stream with fade in/out, scaled to target resolution."""
    stream = ffmpeg.input(
        str(image_path),
        loop=1,
        t=duration,
        framerate=framerate,
    )

    stream = stream.filter(
        "scale", w=width, h=height, force_original_aspect_ratio="increase"
    )

    stream = stream.filter("fade", type="in", start_time=0, duration=fade_duration)
    stream = stream.filter(
        "fade", type="out", start_time=duration - fade_duration, duration=fade_duration
    )

    return stream


def create_video(
    image_paths: list[Path],
    audio_path: Path,
    output_path: Path,
    title: str,
    intro_duration: float,
    crossfade_duration: float,
    width: int,
    height: int,
    framerate: int,
    font_path: str,
    title_font_size: int,
    vcodec: str,
    acodec: str,
    pix_fmt: str,
    preset: str = "p4",
    narration_volume: float = 4.0,
    ambient_path: Path | None = None,
    ambient_volume: float = 1.5,
    audio_end_padding: float = 1.0,
) -> Path:
    """
    Create video from images + audio.

    Flow:
    1. Intro (black screen with title, fades in)
    2. Scene images (equally spaced, with crossfades)
    3. Narration audio (starts after intro fade completes)
    4. Ambient audio (loops underneath, optional)
    """
    audio_duration = get_audio_duration(audio_path)
    image_duration = audio_duration / len(image_paths)

    logger.info(f"Audio: {audio_duration:.1f}s, {len(image_paths)} images @ {image_duration:.1f}s each")

    # Create intro (with fade in using same duration as crossfades)
    intro = create_intro_stream(
        title=title,
        duration=intro_duration,
        fade_duration=crossfade_duration,
        width=width,
        height=height,
        framerate=framerate,
        font_path=font_path,
        title_font_size=title_font_size,
    )

    # Create image streams
    image_streams = []
    for path in image_paths:
        stream = create_image_stream(
            image_path=path,
            duration=image_duration,
            fade_duration=crossfade_duration,
            width=width,
            height=height,
            framerate=framerate,
        )
        image_streams.append(stream)

    # Concat intro + images
    video = ffmpeg.concat(intro, *image_streams, v=1, a=0).node
    
    # Calculate total duration for fade out
    total_duration = intro_duration + (image_duration * len(image_paths)) + audio_end_padding
    
    # Start audio fade after padding (prevents cutting off ending words)
    audio_fade_start = total_duration - crossfade_duration
    
    # Video fade starts at end of video content
    video_fade_start = total_duration - crossfade_duration
    
    # Apply final fade out to video
    video_with_fade = video[0].filter("fade", type="out", start_time=video_fade_start, duration=crossfade_duration)

    # Narration: boost volume, delay until after intro fade completes, fade out at end
    narration_delay = intro_duration  # Start narration when intro ends
    narration = ffmpeg.input(str(audio_path))
    narration = narration.filter("volume", volume=narration_volume)
    narration = narration.filter("adelay", delays=f"{int(narration_delay * 1000)}|{int(narration_delay * 1000)}", all=False)
    narration = narration.filter("afade", type="out", start_time=audio_fade_start, duration=crossfade_duration)

    # Mix with ambient if provided
    if ambient_path and ambient_path.exists():
        logger.info(f"Adding ambient audio: {ambient_path}")
        # Loop ambient for total duration, set volume low
        ambient = ffmpeg.input(str(ambient_path), stream_loop=-1, t=total_duration)
        ambient = ambient.filter("volume", volume=ambient_volume)
        ambient = ambient.filter("afade", type="in", start_time=0, duration=2.0)
        ambient = ambient.filter("afade", type="out", start_time=audio_fade_start, duration=crossfade_duration)
        
        # Mix narration + ambient
        audio_mixed = ffmpeg.filter([narration, ambient], "amix", inputs=2, duration="longest")
    else:
        audio_mixed = narration

    # Output
    output_path.parent.mkdir(parents=True, exist_ok=True)

    ffmpeg.output(
        video_with_fade,
        audio_mixed,
        str(output_path),
        vcodec=vcodec,
        acodec=acodec,
        pix_fmt=pix_fmt,
        preset=preset,
        r=framerate,
        shortest=None,
    ).run(overwrite_output=True)

    logger.info(f"Video saved: {output_path}")
    return output_path
