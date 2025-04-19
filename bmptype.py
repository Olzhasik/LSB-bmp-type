import stegano
import os
import sys
from tkinter import Tk
from tkinter.filedialog import askopenfilename, asksaveasfilename


def hide_text(image_path: str, message: str, new_image_path: str):
    message += "\0"
    message_bytes = message.encode()
    size = len(message_bytes).to_bytes(4, byteorder="big")
    data = size + message_bytes
    data_bits = "".join(f"{byte:08b}" for byte in data)

    try:
        with open(image_path, "rb") as src:
            header = src.read(54)
            if len(header) != 54:
                raise ValueError("Некорректный BMP-заголовок.")

            pixels = bytearray(src.read())

        if len(data_bits) > len(pixels):
            raise ValueError("Сообщение слишком длинное для данного изображения.")

        for i, bit in enumerate(data_bits):
            pixels[i] = (pixels[i] & 0b11111110) | int(bit)

        with open(new_image_path, "wb") as dst:
            dst.write(header)
            dst.write(pixels)

    except Exception as e:
        print(f"Ошибка при сокрытии сообщения: {e}")
        sys.exit(1)


def reveal_text(image_path: str) -> str:
    try:
        with open(image_path, "rb") as file:
            file.seek(54)
            pixels = file.read()

        size_bits = [str(pixels[i] & 1) for i in range(32)]
        size = int("".join(size_bits), 2)

        message_bits = [str(pixels[i] & 1) for i in range(32, 32 + size * 8)]
        message_bytes = bytes(
            int("".join(message_bits[i:i + 8]), 2) for i in range(0, len(message_bits), 8)
        )

        return message_bytes.split(b"\0")[0].decode(errors="replace")

    except Exception as e:
        print(f"Ошибка при извлечении сообщения: {e}")
        sys.exit(1)


def validate_bmp(file_path: str) -> bool:
    if not os.path.exists(file_path):
        print(f"Файл не найден: {file_path}")
        return False

    try:
        with open(file_path, "rb") as file:
            return file.read(2) == b'BM'
    except Exception:
        return False


def choose_file(prompt: str) -> str:
    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    file_path = askopenfilename(title=prompt, filetypes=[("BMP Files", "*.bmp")])
    root.destroy()
    return file_path


def choose_save_location(default_extension=".bmp") -> str:
    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    file_path = asksaveasfilename(
        title="Выберите место для сохранения нового изображения",
        defaultextension=default_extension,
        filetypes=[("BMP Files", "*.bmp")]
    )
    root.destroy()
    return file_path


if __name__ == "__main__":
    print("BMP-стеганография: сокрытие и извлечение текстовых сообщений.")

    action = input("1: Спрятать сообщение\n2: Раскрыть сообщение\nВыбор: ").strip()

    if action == "1":
        image_path = choose_file("Выберите BMP-изображение для скрытия сообщения")
        if not image_path or not validate_bmp(image_path):
            print("Выбран недопустимый файл.")
            sys.exit(1)

        secret_message = input("Введите секретное сообщение: ").strip()

        new_image_path = choose_save_location()
        if not new_image_path:
            print("Место сохранения не выбрано.")
            sys.exit(1)

        hide_text(image_path, secret_message, new_image_path)
        print(f"Сообщение успешно спрятано в {new_image_path}")

    elif action == "2":
        image_path = choose_file("Выберите BMP-изображение для раскрытия сообщения")
        if not image_path or not validate_bmp(image_path):
            print("Выбран недопустимый файл.")
            sys.exit(1)

        extracted_message = reveal_text(image_path)
        print("Скрытое сообщение:", extracted_message)

    else:
        print("Ошибка: неизвестный выбор.")
