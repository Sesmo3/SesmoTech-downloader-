from flask import Flask, request, send_file, render_template
import yt_dlp
import os

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

@app.route("/download", methods=["POST"])
def download():
    url = request.form["url"]
    filename = request.form["filename"]
    format_type = request.form["format"]

    ext = "mp3" if format_type == "mp3" else "mp4"
    output_template = f"{filename}.%(ext)s"

    ydl_opts = {
        "outtmpl": output_template,
        "format": "bestaudio/best" if format_type == "mp3" else "best",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192"
        }] if format_type == "mp3" else []
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        final_file = f"{filename}.{ext}"
        response = send_file(final_file, as_attachment=True)

        @response.call_on_close
        def cleanup():
            if os.path.exists(final_file):
                os.remove(final_file)

        return response
    except Exception as e:
        return f"<h2>Download Failed</h2><p>{str(e)}</p>"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
