#!/bin/bash
# Script to build a single PDF from all documentation markdown files

# Output PDF filename
OUTPUT_PDF="XPCS_WebPlot_Documentation.pdf"

# Title page content
TITLE_PAGE="---
title: XPCS WebPlot Documentation
subtitle: Complete Guide for Users, Developers, and Administrators
author: XPCS WebPlot Team
date: $(date +%Y-%m-%d)
---

"

# Create temporary file with title page
echo "$TITLE_PAGE" > /tmp/title_page.md

# Combine all markdown files in the correct order
pandoc /tmp/title_page.md \
    README.md \
    getting_started.md \
    quick_reference.md \
    user_guide.md \
    api_reference.md \
    architecture.md \
    development_guide.md \
    deployment_guide.md \
    faq.md \
    -o "$OUTPUT_PDF" \
    --pdf-engine=xelatex \
    --toc \
    --toc-depth=3 \
    --number-sections \
    --highlight-style=tango \
    -V geometry:margin=1in \
    -V linkcolor:blue \
    -V urlcolor:blue \
    -V toccolor:blue \
    --metadata title="XPCS WebPlot Documentation" \
    2>&1

# Check if PDF was created successfully
if [ $? -eq 0 ]; then
    echo "✓ PDF generated successfully: $OUTPUT_PDF"
    ls -lh "$OUTPUT_PDF"
else
    echo "✗ Failed to generate PDF"
    exit 1
fi

# Clean up
rm -f /tmp/title_page.md
