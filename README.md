# eml-extractor


This script will go through a given directory recursively, extracting all attachments from .eml files.
.eml files are often how full mailbox dumps are leaked online.
If an attachment with the same filename already exists, MD5 sum of the files are calculated and if not 
a match, the new file will be saved with _# suffix.

By Hamid Kashfi (@hkashfi)
