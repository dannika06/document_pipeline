import os
import logging
import gc
from docling.document_converter import DocumentConverter

# Base directory (directory where this script lives)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Define input/output directories relative to project root
INPUT_DIR = os.path.join(BASE_DIR, "..", "input_docs")
OUTPUT_DIR = os.path.join(BASE_DIR, "..", "outputs")

logger = logging.getLogger(__name__)


def process_document(file_path, converter):
    try:
        result = converter.convert(file_path)
        content = result.document.export_to_markdown()
        return content
    except Exception as e:
        logger.error(f"Failed to process {file_path}: {e}")
        return None


def main():
    os.makedirs(INPUT_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Logger setup after OUTPUT_DIR is guaranteed to exist
    LOG_PATH = os.path.join(OUTPUT_DIR, "pipeline.log")

    class EmojiFormatter(logging.Formatter):
        EMOJIS = {
            logging.INFO: "[+]",
            logging.WARNING: "[!]",
            logging.ERROR: "[X]",
        }

        def format(self, record):
            record.levelname_emoji = self.EMOJIS.get(record.levelno, "[?]")
            return super().format(record)

    formatter = EmojiFormatter("%(asctime)s %(levelname_emoji)s [%(levelname)s] %(message)s")

    file_handler = logging.FileHandler(LOG_PATH, mode='w')
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logging.basicConfig(level=logging.INFO, handlers=[file_handler, stream_handler])

    converter = DocumentConverter()

    for filename in os.listdir(INPUT_DIR):
        if not filename.lower().endswith((".pdf", ".docx", ".pptx")):
            continue

        input_path = os.path.join(INPUT_DIR, filename)
        output_filename = os.path.splitext(filename)[0] + ".md"
        output_path = os.path.join(OUTPUT_DIR, output_filename)

        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            logger.info(f"Skipping {filename} (output already exists at {output_path})")
            continue
        elif os.path.exists(output_path):
            logger.warning(f"Re-processing {filename} (previous output was empty)")

        logger.info(f"Processing: {filename}")
        content = process_document(input_path, converter)

        if content is None:
            logger.error(f"Skipping save for {filename} — processing failed")
            continue

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)

        logger.info(f"Saved: {output_path}")
        gc.collect()


if __name__ == "__main__":
    main()