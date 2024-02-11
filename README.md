# eml-extractor


This script will go through a given directory recursively, extracting all attachments from .eml files.
.eml files are often how full mailbox dumps are leaked online.
If an attachment with the same filename already exists, MD5 sum of the files are calculated and if not 
a match, the new file will be saved with _# suffix.

![eml-extractor](https://github.com/Hamid-K/eml-extractor/assets/3099449/a1cdcd57-ad8d-40a5-a94b-9adfc8548710)


By Hamid Kashfi (@hkashfi)
