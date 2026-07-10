from pathlib import Path
import shutil

from config import INPUT_DIR


class UploadAgent:

    @staticmethod
    def save_pdf(file):

        INPUT_DIR.mkdir(parents=True, exist_ok=True)

        filename = Path(file.filename).name

        save_path = INPUT_DIR / filename

        counter = 1

        while save_path.exists():

            save_path = INPUT_DIR / f"{Path(filename).stem}_{counter}.pdf"

            counter += 1

        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return save_path
