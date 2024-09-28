

YT_VID_ID=$1

if [ -z "$YT_VID_ID" ]; then
    echo "Usage: $0 <youtube-video-id>"
    exit 1
fi

# Download the transcript
echo " --- Downloading transcript for video: $YT_VID_ID"
python yt-transcript-helper/yttx_retriever.py https://www.youtube.com/watch?v=$YT_VID_ID
echo " --- Prettifying the transcript"
python yt-transcript-helper/yttx_prettifier.py .local/output/yttx/$YT_VID_ID/cleaned_transcript.txt 