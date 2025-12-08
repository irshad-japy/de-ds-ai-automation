import argparse
import os
from typing import List, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Scopes we need:
# - upload videos
# - manage your own YouTube content
SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube"
]

CLIENT_SECRETS_FILE = "client_secret.json"
TOKEN_FILE = "token.json"

# --------- AUTH ---------

def get_authenticated_service():
    """
    Returns an authorized YouTube Data API client.
    Uses OAuth installed-app flow and stores token in token.json
    """
    creds = None

    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # Refresh existing token
            creds.refresh(Request())
        else:
            # Run local server flow on first use
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRETS_FILE, SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Save the credentials for next run
        with open(TOKEN_FILE, "w", encoding="utf-8") as token:
            token.write(creds.to_json())

    return build("youtube", "v3", credentials=creds)

# --------- UPLOAD VIDEO ---------

def upload_video(
    youtube,
    video_file: str,
    title: str,
    description: str = "",
    tags: Optional[List[str]] = None,
    category_id: str = "27",  # 27 = Education
    privacy_status: str = "public",
    default_language: Optional[str] = None,
    made_for_kids: bool = False,
    recording_date: Optional[str] = None,  # "YYYY-MM-DD" or RFC3339
):
    """
    Uploads a video to YouTube and returns the new video ID.

    :param youtube: Authorized YouTube client
    :param video_file: Path to local .mp4 file
    :param title: Video title (<= 100 chars recommended)
    :param description: Video description (<= 5000 chars)
    :param tags: List of tags (total 500 chars recommended)
    :param category_id: YouTube category ID (string)
    :param privacy_status: 'public' | 'unlisted' | 'private'
    :param default_language: e.g. 'en', 'hi', 'en-IN', 'hi-IN'
    :param made_for_kids: True/False
    :param recording_date: e.g. '2025-12-05' or full RFC3339
    """

    if not os.path.exists(video_file):
        raise FileNotFoundError(f"Video file not found: {video_file}")

    snippet = {
        "title": title[:100],
        "description": description[:5000],
        "categoryId": category_id,
    }

    if tags:
        snippet["tags"] = tags

    if default_language:
        snippet["defaultLanguage"] = default_language

    status_body = {
        "privacyStatus": privacy_status,  # 'public' / 'unlisted' / 'private'
        "selfDeclaredMadeForKids": made_for_kids,
    }

    body = {
        "snippet": snippet,
        "status": status_body,
    }

    if recording_date:
        body["recordingDetails"] = {
            "recordingDate": recording_date  # "YYYY-MM-DD" or RFC3339
        }

    # Create a MediaFileUpload for resumable upload
    media = MediaFileUpload(
        video_file,
        mimetype="video/mp4",
        chunksize=-1,        # -1 = default chunk size
        resumable=True
    )

    request = youtube.videos().insert(
        part="snippet,status,recordingDetails",
        body=body,
        media_body=media
    )

    print(f"Uploading video: {video_file}")
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Upload progress: {int(status.progress() * 100)}%")

    if "id" not in response:
        raise RuntimeError(f"Upload failed, response: {response}")

    video_id = response["id"]
    print(f"✅ Upload complete. Video ID: {video_id}")
    return video_id


# --------- PLAYLIST ---------

def add_to_playlist(youtube, video_id: str, playlist_id: str):
    """
    Adds the uploaded video to a playlist.
    playlist_id: YouTube playlist ID, e.g. 'PLxxxx'
    """
    body = {
        "snippet": {
            "playlistId": playlist_id,
            "resourceId": {
                "kind": "youtube#video",
                "videoId": video_id,
            }
        }
    }

    response = youtube.playlistItems().insert(
        part="snippet",
        body=body
    ).execute()

    print(f"✅ Added to playlist {playlist_id}. PlaylistItem ID: {response.get('id')}")

# --------- CAPTIONS (SUBTITLES) ---------

def upload_captions(
    youtube,
    video_id: str,
    caption_file: str,
    language: str = "en",
    name: Optional[str] = None,
    is_draft: bool = False,
    sync: bool = True,
):
    """
    Uploads a caption/subtitle file (.srt/.vtt/transcript) for a video.

    NOTE:
    - For plain transcript without timings, set sync=True (YouTube will auto-sync).
    - For fully-timed SRT/VTT, sync can be False.

    :param youtube: Authorized YouTube client
    :param video_id: Video ID to attach captions to
    :param caption_file: Path to caption file (.srt or .vtt)
    :param language: e.g. 'en', 'hi'
    :param name: Track name shown in UI (default = "<language> subtitles")
    :param is_draft: True to keep captions as draft
    :param sync: True to auto-sync non-timed transcript
    """

    if not os.path.exists(caption_file):
        raise FileNotFoundError(f"Caption file not found: {caption_file}")

    if not name:
        name = f"{language} subtitles"

    print(f"Uploading captions: {caption_file} (lang={language})")

    body = {
        "snippet": {
            "language": language,
            "name": name,
            "videoId": video_id,
            "isDraft": is_draft,
        }
    }

    media = MediaFileUpload(
        caption_file,
        mimetype="application/octet-stream",
        resumable=False,
    )

    request = youtube.captions().insert(
        part="snippet",
        body=body,
        media_body=media,
        sync=sync,
    )

    response = request.execute()
    caption_id = response.get("id")
    print(f"✅ Captions uploaded. Caption ID: {caption_id}")

# --------- CLI WRAPPER ---------

def parse_args():
    parser = argparse.ArgumentParser(
        description="Upload a video to YouTube with metadata and optional playlist & captions."
    )

    parser.add_argument(
        "--video-file",
        required=True,
        help="Path to local MP4 file."
    )
    parser.add_argument(
        "--title",
        required=True,
        help="Video title (max ~100 chars)."
    )
    parser.add_argument(
        "--description",
        default="",
        help="Video description (max ~5000 chars)."
    )
    parser.add_argument(
        "--tags",
        default="",
        help="Comma-separated tags, e.g. 'ai,python,automation'."
    )
    parser.add_argument(
        "--category-id",
        default="27",
        help="YouTube category ID (default: 27 Education)."
    )
    parser.add_argument(
        "--privacy-status",
        default="public",
        choices=["public", "unlisted", "private"],
        help="Privacy status for the video."
    )
    parser.add_argument(
        "--default-language",
        default=None,
        help="Default language code (e.g. 'hi', 'en', 'en-IN')."
    )
    parser.add_argument(
        "--made-for-kids",
        action="store_true",
        help="Mark video as made for kids."
    )
    parser.add_argument(
        "--recording-date",
        default=None,
        help="Recording date (YYYY-MM-DD or RFC3339)."
    )
    parser.add_argument(
        "--playlist-id",
        default=None,
        help="Playlist ID to add the video to (optional)."
    )
    parser.add_argument(
        "--caption-file",
        default=None,
        help="Caption (.srt/.vtt) file path (optional)."
    )
    parser.add_argument(
        "--caption-language",
        default="en",
        help="Caption language code (default: 'en')."
    )
    parser.add_argument(
        "--caption-name",
        default=None,
        help="Custom caption track name (optional)."
    )
    parser.add_argument(
        "--caption-draft",
        action="store_true",
        help="Upload captions as draft (not published)."
    )

    return parser.parse_args()


def main():
    args = parse_args()

    # Prepare tags list
    tags_list = None
    if args.tags:
        tags_list = [t.strip() for t in args.tags.split(",") if t.strip()]

    youtube = get_authenticated_service()

    # 1. Upload video
    video_id = upload_video(
        youtube=youtube,
        video_file=args.video_file,
        title=args.title,
        description=args.description,
        tags=tags_list,
        category_id=args.category_id,
        privacy_status=args.privacy_status,
        default_language=args.default_language,
        made_for_kids=args.made_for_kids,
        recording_date=args.recording_date,
    )

    # 2. Add to playlist (optional)
    if args.playlist_id:
        add_to_playlist(youtube, video_id, args.playlist_id)

    # 3. Upload captions (optional)
    if args.caption_file:
        upload_captions(
            youtube,
            video_id=video_id,
            caption_file=args.caption_file,
            language=args.caption_language,
            name=args.caption_name,
            is_draft=args.caption_draft,
            sync=True,  # good if using plain transcript or simple SRT
        )

    print("✅ All done.")


if __name__ == "__main__":
    main()
