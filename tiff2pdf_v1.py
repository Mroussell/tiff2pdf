"""TIFF to PDF Conversion Script

This script allows the user to Convert all designated .tif/.tiff files
into a multipage PDF document

This tool accepts .tiff and .tif field and will ignore all others
and those that have an incorrect hex signature/

This script requires these packages to be installed:
    * PyPDF2
    * PIL 


This file contains the following functions:
    * check_hex - returns true for correct hex signature and false otherwise
    * tiff2pdf - returns string to created pdf file.

-Michael Roussell
DCSK
MIT License.
"""
#!/usr/bin/env python

import os
import sys
import binascii
from colorama import Fore
from datetime import datetime

from PyPDF2 import PdfFileMerger
from PIL import Image, ImageSequence


def check_hex(file_path: str) -> bool:
    """Checks input file via path for correct Hex file signature.

    Parameters:
    ----------
        file_path: str (required)
            String object that points to file to be read.

    Returns:
    ---------
        True if file matches Hex signature, If not false.

    Raises:
        None: yet
    """
    # Check OS endian style for signature checking.
    endian = sys.byteorder
    if endian == "little":
        byte_sig = "b'49492a00"
    else:
        byte_sig = "b'4d4d002a"

    # Open file, parse bytes, and check for correct file signature.
    with open(file_path, "rb") as f:
        hex_dump = ""
        n = 0
        for chunk in iter(lambda: f.read(32), b""):
            hex_dump = hex_dump + str(binascii.hexlify(chunk))
            n += 1
            if n > 10:
                break
        if hex_dump[:10] == byte_sig:
            return True
        else:
            return False


def tiff_to_pdf(tiff_path: str) -> str:
    """Converts TIFF file to PDF via pillow package library Image and ImageSequence objects

    Parameters:
    ----------
    tiff_path: str (required)
        A String object that represents the path to desired tiff file for conversion.

    Returns:
    ---------
    pdf_path: (str)
        A String object that represents the path to save location of pdf output file.

    Raises:
    --------
    KeyError:
        Raised on file or file path not found.
    OtherError:
        File in path not TIFF file.
    """
    # Ceate PDF file path from TIFF file path, Raise Exception if no file found.
    if ".tiff" in tiff_path:
        pdf_path = tiff_path.replace(".tiff", ".pdf")
    else:
        pdf_path = tiff_path.replace(".tif", ".pdf")
    
    # Check that file exists
    if not os.path.exists(tiff_path):
        print(Fore.RED + "Exiting with Error Code 1:")
        raise Exception(f"{tiff_path} does not find.")

    # Create Image object from path
    image = Image.open(tiff_path)

    # For page in Tiff Image object, create PDF file.
    images = []
    for i, page in enumerate(ImageSequence.Iterator(image)):
        page = page.convert("RGB")
        images.append(page)

    # Check if image was larger than 1 page.
    if len(images) == 1:
        images[0].save(pdf_path)
    else:
        images[0].save(pdf_path, save_all=True, append_images=images[1:])
    return pdf_path


def main():
        # For all TIFF files in working directory, convert to PDF and add path to a middle files list
    print("~~~> Launching TIFF to PDF Converter.")
    middle_file_names = []

    # TODO: Would need to change file path for Windows, NOTE: requires absolute path
    input_path = "input/"
    for file in os.listdir(input_path):
        if (file.endswith(".tiff") or file.endswith(".tif")) and check_hex(input_path + file):
            middle_file_names.append(tiff_to_pdf(input_path + file))
        else:
            continue

    # Merge all PDF output files into output PDF file using Py2PDF PdfMerger Class object
    merger = PdfFileMerger()

    # Append  all pdf middle files to merger object.
    for pdf in middle_file_names:
        merger.append(pdf)

    # Set date and name for output file.
    # TODO: Would need to change file path for Windows, NOTE: requires absolute path
    now = datetime.now()
    out_path = "outputs/"
    outfile_name = "tiff2pdf_output_" + now.strftime("%Y_%m_%d_%H_%M_%S") + ".pdf"

    # Write merged PDF middle files to outfile.
    merger.write(out_path + outfile_name)
    print(Fore.CYAN + f"{outfile_name} created succesfully in original path.")

    # Delete middle files.
    for file in middle_file_names:
        os.remove(file)
        print(Fore.YELLOW + f"Removing {file}.")

    # Close merger and End Program.
    print(Fore.GREEN + "Exiting with Error Code 0:")
    merger.close()
    print(Fore.RESET + "~~~> Closing TIFF to PDF Converter." +   Fore.GREEN +  " Success!")
    quit()

"""
Running from this file.
"""
if __name__ == "__main__":
    main()
