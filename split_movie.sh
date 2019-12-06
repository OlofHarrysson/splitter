#/bin/bash

ffmpeg -i movies/home.avi -ss 6.166666666666667 -t 6.5 movie_outputs/chunk1.avi
# ffmpeg -i movies/output.avi -ss 15 -t 20 movie_outputs/chunk2.avi

# ffmpeg -i movies/output.avi -c copy -map 0 -segment_time 00:00:01 -f segment chunk.avi


ffmpeg -i movies/home.avi -ss 6.166666666666667 -t 6.5 movie_outputs/chunk1.avi -vcodec copy -acodec copy


ffmpeg -i movies/home.avi -ss 6.166666666666667 -t 6.5 -c copy movie_outputs/chunk1.avi
