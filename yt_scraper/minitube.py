from pytube import YouTube
from pytube import extract
from pytube import Stream, StreamQuery


class MiniTube(YouTube):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def check_availability(self):
        return True

    @property
    def streams(self):
        if self._fmt_streams:
            return StreamQuery(self._fmt_streams)
        stream_manifest = extract.apply_descrambler(self.streaming_data)
        _fmt_streams = [
            Stream(
                stream=stream,
                monostate=self.stream_monostate,
            )
            for stream in stream_manifest
        ]
        self._fmt_streams = StreamQuery(_fmt_streams)
        return self._fmt_streams
