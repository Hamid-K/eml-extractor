
#!/usr/bin/env python
# This script will go through a given directory recursively, extracting all attachments from .eml files.
# .eml files are often how full mailbox dumps are leaked online.
# If an attachment with the same filename already exists, MD5 sum of the files are calculated and if not 
# a match, the new file will be saved with _# suffix.
#
# Hamid Kashfi (@hkashfi)

import os
import sys
import email
import email.policy
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
from time import time
from rich.console import Console
from rich.progress import Progress, BarColumn , TextColumn, TimeElapsedColumn

def file_md5(file_data):
    return hashlib.md5(file_data).hexdigest()

def existing_file_md5(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def make_unique_filename(target_dir, filename, file_data):
    base, extension = os.path.splitext(filename)
    original_path = os.path.join(target_dir, filename)
    if os.path.exists(original_path):
        new_md5 = file_md5(file_data)
        if existing_file_md5(original_path) == new_md5:
            return None  # The file is identical, no need to create a new version
        counter = 1
        while True:
            unique_filename = f"{base}_{counter}{extension}"
            unique_path = os.path.join(target_dir, unique_filename)
            if not os.path.exists(unique_path) or existing_file_md5(unique_path) == new_md5:
                break
            counter += 1
    else:
        unique_filename = filename
    return unique_filename

def extract_attachments_from_file(file_path, target_dir, progress: Progress, task_id, stats: dict, verbose: bool, console: Console):
    with open(file_path, 'rb') as f:
        msg = email.message_from_binary_file(f, policy=email.policy.default)
        for part in msg.walk():
            if part.get_content_disposition() == 'attachment':
                filename = part.get_filename()
                if filename:
                    file_data = part.get_payload(decode=True)
                    unique_filename = make_unique_filename(target_dir, filename, file_data)
                    if unique_filename:  # File doesn't have an identical match
                        save_path = os.path.join(target_dir, unique_filename)
                        with open(save_path, 'wb') as f_out:
                            f_out.write(file_data)
                        stats['extracted'] += 1
                        if verbose:  # Verbose logging
                            eml_filename = os.path.basename(file_path)
                            console.log(f"[yellow]Extracted: [white] {unique_filename} \n[yellow] From: [white] {eml_filename}\n-----------------")
    stats['processed'] += 1
    progress.update(task_id, advance=1, refresh=True)


def extract_and_save_attachments(start_dir, target_dir="extracted", verbose=False):
    if not os.path.exists(target_dir):
        os.makedirs(target_dir, exist_ok=True)
    eml_files = [os.path.join(root, file) for root, dirs, files in os.walk(start_dir) for file in files if file.endswith('.eml')]
    stats = {'processed': 0, 'extracted': 0}

    console = Console()
    with Progress(
        BarColumn(bar_width=None),  # Adding the filling progress line back
        TextColumn("[progress.percentage]{task.percentage:>3.1f}%"),
        TextColumn("([yellow]{task.completed}/{task.total} [default] .eml processed)"),
        TextColumn("([yellow]{task.fields[extracted]} [default]files extracted)"),
        TimeElapsedColumn(),
        console=console,
        transient=True
    ) as progress:
        task_id = progress.add_task("Processing...", total=len(eml_files), extracted=stats['extracted'])
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(extract_attachments_from_file, file_path, target_dir, progress, task_id, stats, verbose, console) for file_path in eml_files]
            for future in as_completed(futures):
                progress.update(task_id, extracted=stats['extracted'])

    return stats['processed'], stats['extracted']



if __name__ == "__main__":
    verbose = "-v" in sys.argv
    if len(sys.argv) not in [2, 3]:
        print("Usage: script.py <directory_path> [-v]")
        sys.exit(1)

    start_directory = sys.argv[1] if sys.argv[1] != '-v' else sys.argv[2]
    console = Console()
    console.log("[bold magenta]Starting extraction...[/]")
    start_time = time()
    total_processed, total_extracted = extract_and_save_attachments(start_directory, verbose=verbose)
    end_time = time()
    elapsed_time = end_time - start_time
    console.log(f"[bold green]Extraction completed in {elapsed_time:.2f} seconds.[/]")
    console.log(f"[bold yellow]Total .eml files processed: {total_processed}[/]")
    console.log(f"[bold yellow]Total attachments extracted: {total_extracted}[/]")
