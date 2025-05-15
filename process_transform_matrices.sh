#!/bin/bash

mkdir -p recalage/matrices
echo "======================================================================="
for file in recalage/transforms/*.txt; do
    # check if file exists
    if [ -f "$file" ]; then
        echo "======================================================================="
        echo "Processing transform from recalage of: $file"
        echo "======================================================================="

        python recalage/process_transforms.py --transform="$file"
    fi
done

echo "All transforms processed."
ls recalage/matrices
echo "======================================================================="