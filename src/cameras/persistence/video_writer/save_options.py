from pathlib import Path

from pydantic import BaseModel


class SaveOptions(BaseModel):
    writer_dir: Path
    video_filename: str = "movie.mp4"
    timestamp_filename: str = "timestamps.npy"
    fps: float
    fourcc: str = "MP4V"
    frame_width: int
    frame_height: int

    @property
    def full_path_video(self):
        return Path().joinpath(self.writer_dir, self.video_filename)

    @property
    def full_path_timestamp(self):
        return Path().joinpath(self.writer_dir, self.timestamp_filename)
