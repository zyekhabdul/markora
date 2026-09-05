FROM python:3.12-slim

LABEL maintainer="zyekhabdul <zyekhabdulqadirjailani@gmail.com>"
LABEL description="Markora - Sovereign Markdown Notebook & Todo TUI"

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir .

ENV NOTES_DIR=/root/notes
VOLUME ["/root/notes"]

ENTRYPOINT ["markora"]
CMD ["ui"]
