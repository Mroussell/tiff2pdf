"""TIFF to PDF Conversion Script

This script allows the user to Convert all designated ".tif" and ".tiff" files
into a single multipage PDF document.

This tool accepts .tiff and .tif field and will ignore all others
and those that have an incorrect hex signature.

This script requires these packages to be installed:
    * PyPDF2
    * PIL 


This file contains the following functions:
    * check_hex - returns true for correct hex signature and false otherwise
    * tiff2pdf - returns string to created pdf file.
    * main - designates paths and structure for the script.

-Michael Roussell
Dekalb Community Service Board
Copy Right 2022
MIT License.
"""
#!/usr/bin/env python

import os
import sys
import binascii
from datetime import datetime

from PyPDF2 import PdfFileMerger
from PIL import Image, ImageSequence


def check_hex(file_path: str) -> bool:
    """Checks input file via path for correct Hexadecimal file signature.

    Parameters:
    ----------
        file_path: str (required)
            String object that points to file to be read.

    Returns:
    ---------
        True if file matches Hex signature, If not False.

    Raises:
        NONE: if file is not properly signed.
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
            print(f"Error Code 2: File at {file_path} is not signed as TIFF.")
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
        print("Exiting with Error Code 1:")
        raise Exception(f"{tiff_path} does not find.")

    # Create Image object from path
    image = Image.open(tiff_path)

    # For page in Tiff Image object, create PDF file.
    images = []
    for i, page in enumerate(ImageSequence.Iterator(image)):
        page = page.convert("RGB")
        images.append(page)

    # Check if image was larger than 1 page, append to the same middle file if not.
    if len(images) == 1:
        images[0].save(pdf_path)
    else:
        images[0].save(pdf_path, save_all=True, append_images=images[1:])
    
    print(f"{pdf_path} created")
    return pdf_path


def main():
    # gather cli arguments passed from php and parse them 
    pat_files = sys.argv
    pat_id = sys.argv[1].lower().replace(",", "_")

    # For all TIFF files in working directory, convert to PDF and add path to a middle files list
    print("~~~> Launching TIFF to PDF Converter.")
    middle_file_names = []

    # For all tif or tiff files with correct path and in proper batch, create pdf middle file
    current_path = os.getcwd()
    input_path = os.path.join('pdf', 'input')
    for file in os.listdir(input_path):
        if (file.endswith(".tiff") or file.endswith(".tif")) and check_hex(os.path.join(input_path, file)) and file in pat_files:
            middle_file_names.append(tiff_to_pdf(os.path.join(input_path, file)))
        else:
            continue

    # Merge all PDF output files into output PDF file using Py2PDF PdfMerger Class object
    merger = PdfFileMerger()

    # Append  all pdf middle files to merger object.
    for pdf in middle_file_names:
        merger.append(pdf)

    # Set date and name for output file. 
    now = datetime.now()
    out_path =os.path.join('pdf','output')
    outfile_name = pat_id + "_merged_" + now.strftime("%Y_%m_%d_%H_%M_%S") + ".pdf"

    # Write merged PDF middle files to outfile and close merger.
    merger.write(os.path.join(out_path, outfile_name))
    print(f"{outfile_name} created succesfully in output path.")
    merger.close()

    # Delete middle files.
    for file in middle_file_names:
            print(f"Removing {file}.")
            os.remove(file)

    # Delete origin files for this batch
    for file in os.listdir(input_path):
        if file in pat_files:
            print(f"Removing {file}.")
            os.remove(os.path.join(input_path , file))

    #  End Program.
    print("Exiting with Error Code 0:")
    print("~~~> Closing TIFF to PDF Converter. Merger Success!")
    quit()

"""
Running from this file.
"""
if __name__ == "__main__":
    main()
