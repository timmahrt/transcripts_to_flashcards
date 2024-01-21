import os

from flask import Blueprint, render_template, request

from app import parse_transcripts
from app import load_transcripts

main = Blueprint("main", __name__)

# TODO: It would be nice if the root path was actually the root and
#       not 'app/routes/'
TRANSCRIPTS_FOLDER = os.path.join(main.root_path, "..", "..", "transcripts")


@main.route("/", methods=["GET", "POST"])
def index():
    print("Inside index")
    url = None
    text = None
    texts = None
    tokens_by_pos = None
    contexts_by_pairs = None
    author = None
    title = None
    error = None

    if request.method == "POST":
        url = request.form.get("url")

        if url:
            url.strip()

        if url is not None and url != "":
            try:
                transcriptData = parse_transcripts.getTranscriptTexts(
                    url, TRANSCRIPTS_FOLDER, "ja"
                )
            except (
                load_transcripts.InvalidYoutubeUrl,
                load_transcripts.NoMachingTranscriptFoundError,
            ) as e:
                error = str(e)
            else:
                texts = transcriptData["transcript"]
                title = transcriptData["title"]
                author = transcriptData["author"]
                text = "".join(texts)
                tokens_by_pos = parse_transcripts.tokenizeText(text)
                contexts_by_pairs = parse_transcripts.getContextsByPairs(
                    texts, tokens_by_pos
                )

    return render_template(
        "index.html",
        url=url,
        transcripts=texts,
        tokens_by_pos=tokens_by_pos,
        contexts_by_pairs=contexts_by_pairs,
        title=title,
        author=author,
        error=error,
    )


print("Loaded routes")
