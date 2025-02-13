The purpose of this repo is to have a repository of Security Now! text transcripts to feed into an AI model.

The .py files are for:

- Downloading from grc.com
- Fixing file date stamps to make the file date match the episode date
- Creating the summary files so you can get all episodes into Google's NotebookLM which has a max 50 file limit with 500000 words per file.

# Downloading Security Now podcast files

*NOTE: You can run these .py files, and download them straight from grc.com but please don't doxx Steve's wonderful website. If you just want the episodes you can download the zip files from [zips](/zips/)

## TLDR for Google's NotebookLM

Download [this](/summarized/summarized001-1011.zip), extract and upload to a notebook. Slowly. When I tried, it rejected random ones. I'd do 5 files at a time.
